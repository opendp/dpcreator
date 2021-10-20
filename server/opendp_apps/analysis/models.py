from django.db import models
from django.conf import settings
from django.utils import timezone

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.model_helpers.models import \
    (TimestampedModelWithUUID,)
from opendp_apps.utils.extra_validators import \
    (validate_not_negative,
     validate_epsilon_or_none)


class DepositorSetupInfo(TimestampedModelWithUUID):
    """
    Metadata and aggregate data about potential release of Dataset
    """
    class DepositorSteps(models.TextChoices):
        """
        Enumeration for different statuses during depositor process
        """
        STEP_0100_UPLOADED = 'step_100', 'Step 1: Uploaded'
        STEP_0200_VALIDATED = 'step_200', 'Step 2: Validated'   # done automatically for Dataverse use case
        STEP_0300_PROFILING_PROCESSING = 'step_300', 'Step 3: Profiling Processing'
        STEP_0400_PROFILING_COMPLETE = 'step_400', 'Step 4: Profiling Complete'
        STEP_0500_VARIABLE_DEFAULTS_CONFIRMED = 'step_500', 'Step 5: Variable Defaults Confirmed'
        STEP_0600_EPSILON_SET = 'step_600', 'Step 6: Epsilon Set'
        # Error statuses should begin with 9
        STEP_9100_VALIDATION_FAILED = 'error_9100', 'Error 1: Validation Failed'
        STEP_9200_DATAVERSE_DOWNLOAD_FAILED = 'error_9200', 'Error 2: Dataverse Download Failed'
        STEP_9300_PROFILING_FAILED = 'error_9300', 'Error 3: Profiling Failed'
        STEP_9400_CREATE_RELEASE_FAILED = 'error_9400', 'Error 4: Create Release Failed'

    """
    Confidence Interval choices
    """
    CI_90_ALPHA = astatic.CI_90_ALPHA
    CI_95_ALPHA = astatic.CI_95_ALPHA
    CI_99_ALPHA = astatic.CI_99_ALPHA
    CI_CHOICES = astatic.CI_CHOICES

    """
    Often used Delta values
    """
    DELTA_0 = 0.0
    DELTA_10_NEG_5 = 10.0**-5
    DELTA_10_NEG_6 = 10.0**-6
    DELTA_10_NEG_7 = 10.0**-7

    # User who initially added/uploaded data
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT)

    # Set on save
    is_complete = models.BooleanField(default=False,
                                      help_text='auto-populated on save')

    # Track workflow based on DepositorSteps
    user_step = models.CharField(max_length=128,
                                 choices=DepositorSteps.choices,
                                 default=DepositorSteps.STEP_0100_UPLOADED)

    # Populated from the UI
    dataset_questions = models.JSONField(null=True, blank=True)
    epsilon_questions = models.JSONField(null=True, blank=True)

    # Includes variable ranges and categories
    variable_info = models.JSONField(null=True, blank=True)

    #
    # Epsilon related fields
    #
    default_epsilon = models.FloatField(null=True,
                                        blank=True,
                                        help_text='Default based on answers to epsilon_questions.',
                                        validators=[validate_epsilon_or_none])
    
    epsilon = models.FloatField(null=True, blank=True,
                                help_text=('Used for OpenDP operations, starts as the "default_epsilon"'
                                           ' value but may be overridden by the user.'),
                                validators=[validate_epsilon_or_none])

    #
    # Delta related fields
    #
    default_delta = models.FloatField(null=True,
                                      blank=True,
                                      default=DELTA_0,
                                      help_text='Default based on answers to epsilon_questions.',
                                      validators=[validate_not_negative])

    delta = models.FloatField(null=True,
                              blank=True,
                              default=DELTA_0,
                              help_text=('Used for OpenDP operations, starts as the "default_delta"'
                                         ' value but may be overridden by the user.'),
                              validators=[validate_not_negative])

    confidence_interval = models.FloatField(\
                            choices=CI_CHOICES,
                            default=CI_95_ALPHA,
                            help_text=('Used for OpenDP operations, starts as the "default_delta"'
                                       ' value but may be overridden by the user.'))


    class Meta:
        verbose_name = 'Depositor Setup Data'
        verbose_name_plural = 'Depositor Setup Data'
        ordering = ('-created', )

    def __str__(self):
        if hasattr(self, 'dataversefileinfo'):
            return f'{self.dataversefileinfo} - {self.user_step}'
        elif hasattr(self, 'uploadfileinfo'):
            return f'{self.uploadfileinfo} - {self.user_step}'
        else:
            return f'{self.object_id} - {self.user_step}'

    def get_dataset_info(self):
        """
        Access a DataSetInfo object, either dataversefileinfo or uploadfileinfo
        # Workaround for https://github.com/opendp/dpcreator/issues/257
        """
        if hasattr(self, 'dataversefileinfo'):
            return self.dataversefileinfo
        elif hasattr(self, 'uploadfileinfo'):
            return self.uploadfileinfo

        raise AttributeError('DepositorSetupInfo does not have access to a DataSetInfo instance')


    def set_user_step(self, new_step:DepositorSteps) -> bool:
        """Set a new user step. Does *not* save the object."""
        assert isinstance(new_step, DepositorSetupInfo.DepositorSteps), \
            "new_step must be a valid choice in DepositorSteps"
        self.user_step = new_step
        return True
    
    def save(self, *args, **kwargs):
        # Future: is_complete can be auto-filled based on either field values or the STEP
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        # This ensures that `is_complete` gets added to update_fields or else the process cannot proceed
        # from the frontend
        if self.variable_info and self.epsilon \
            and self.user_step == self.DepositorSteps.STEP_0600_EPSILON_SET:
            self.is_complete = True
        else:
            self.is_complete = False
        # Specifically for this model, we are overriding the update method with an explicit list of
        # update_fields, so we need to set the updated field manually.
        # All other models will be updated without this step due to the auto_now option from the parent class.
        self.updated = timezone.now()
        super(DepositorSetupInfo, self).save(*args, **kwargs)


class ReleaseInfo(TimestampedModelWithUUID):
    """
    Release of differentially private result from an AnalysisPlan
    """
    dataset = models.ForeignKey('dataset.DataSetInfo',
                                on_delete=models.PROTECT)

    epsilon_used = models.FloatField(null=False,
                                     blank=False,
                                     validators=[validate_not_negative])
    dp_release = models.JSONField()

    dp_release_json_file = models.FileField( \
                                   # storage=settings.RELEASE_FILE_STORAGE_ROOT,
                                   upload_to='release-files/%Y/%m/%d/',
                                   blank=True, null=True)

    dp_release_pdf_file = models.FileField(
                                   # storage=settings.RELEASE_FILE_STORAGE_ROOT,
                                   upload_to='release-files/%Y/%m/%d/',
                                   blank=True, null=True)

    #pdf_release

    class Meta:
        verbose_name = 'Release Information'
        verbose_name_plural = 'Release Information'
        ordering = ('dataset', '-created')


class AnalysisPlan(TimestampedModelWithUUID):
    """
    Details of request for a differentially private release
    ! Do we want another object to monitor the plan once it is sent to the execution engine?
    """
    class AnalystSteps(models.TextChoices):
        """
        Enumeration for statuses during the analysis process
        """
        STEP_0700_VARIABLES_CONFIRMED = 'step_700', 'Step 7: Variables Confirmed'
        STEP_0800_STATISTICS_CREATED = 'step_800', 'Step 8: Statistics Created'
        STEP_0900_STATISTICS_SUBMITTED = 'step_900', 'Step 9: Statistics Submitted'
        STEP_1000_RELEASE_COMPLETE = 'step_1000', 'Step 10: Release Complete'
        STEP_1100_DV_RELEASE_DEPOSITED = 'step_1100', 'Step 11: Dataverse Release Deposited'  # Dataverse Only
        STEP_1200_PROCESS_COMPLETE = 'step_1200', 'Step 12: Process Complete'
        # Error statuses should begin with 9
        STEP_9500_RELEASE_CREATION_FAILED = 'error_9500', 'Error 5: Release Creation Failed'
        STEP_9600_RELEASE_DEPOSIT_FAILED = 'error_9600', 'Error 6: Release Deposit Failed'

    analyst = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT)

    name = models.CharField(max_length=255)

    dataset = models.ForeignKey('dataset.DataSetInfo',
                                on_delete=models.PROTECT)
    is_complete = models.BooleanField(default=False)
    user_step = models.CharField(max_length=128,
                                 choices=AnalystSteps.choices)

    # Includes variable ranges and categories
    variable_info = models.JSONField(null=True, blank=True)

    #custom_variables = models.JSONField(null=True)
    dp_statistics = models.JSONField(null=True)

    release_info = models.ForeignKey(ReleaseInfo, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f'{self.dataset} - {self.user_step}'

    def is_editable(self) -> bool:
        """
        Allow editing if the user step is either:'
          STEP_0700_VARIABLES_CONFIRMED or
          STEP_0800_STATISTICS_CREATED
        """
        editable_steps = [self.AnalystSteps.STEP_0700_VARIABLES_CONFIRMED,
                          self.AnalystSteps.STEP_0800_STATISTICS_CREATED]
        return self.user_step in editable_steps


    def save(self, *args, **kwargs):
        # Future: is_complete can be auto-filled based on either field values or the user_step
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        super(AnalysisPlan, self).save(*args, **kwargs)



