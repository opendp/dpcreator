from django.db import models
from django.conf import settings
from opendp_apps.model_helpers.models import \
    (TimestampedModelWithUUID,)


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

    # user who initially added/uploaded data
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT)
    is_complete = models.BooleanField(default=False)
    user_step = models.CharField(max_length=128,
                                 choices=DepositorSteps.choices,
                                 default=DepositorSteps.STEP_0100_UPLOADED)
    epsilon = models.FloatField(null=True, blank=True)
    dataset_questions = models.JSONField(null=True, blank=True)

    # Includes variable ranges and categories
    variable_info = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'Depositor Setup Data'
        verbose_name_plural = 'Depositor Setup Data'
        ordering = ('dataversefileinfo', '-created', )

    def __str__(self):
        return f'{self.dataversefileinfo} - {self.user_step}'

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
        if self.variable_info and self.epsilon \
            and self.user_step == self.DepositorSteps.STEP_0600_EPSILON_SET:
            self.is_complete = True
        else:
            self.is_complete = False

        super(DepositorSetupInfo, self).save(*args, **kwargs)


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

    def __str__(self):
        return f'{self.dataset} - {self.user_step}'

    def save(self, *args, **kwargs):
        # Future: is_complete can be auto-filled based on either field values or the user_step
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        super(AnalysisPlan, self).save(*args, **kwargs)


class ReleaseInfo(TimestampedModelWithUUID):
    """
    Release of differentially private result from an AnalysisPlan
    """
    dataset = models.ForeignKey('dataset.DataSetInfo',
                                on_delete=models.PROTECT)

    # also gives analyst
    analysis_plan = models.ForeignKey(AnalysisPlan,
                                      on_delete=models.PROTECT)

    epsilon_used = models.FloatField(null=False, blank=False)
    dp_release = models.JSONField()

    class Meta:
        verbose_name = 'Release Information'
        verbose_name_plural = 'Release Information'
        ordering = ('dataset', '-created')

