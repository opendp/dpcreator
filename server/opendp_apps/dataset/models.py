from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import CASCADE
from django.conf import settings
from polymorphic.models import PolymorphicModel
from opendp_apps.model_helpers.models import \
    (TimestampedModel, TimestampedModelWithUUID)

UPLOADED_FILE_STORAGE = FileSystemStorage(location=settings.UPLOADED_FILE_STORAGE_ROOT)


class DataSetInfo(TimestampedModelWithUUID, PolymorphicModel):
    """
    Base type for table that either holds DV data
    or a file upload
    """
    name = models.CharField(max_length=128)

    # user who initially added/uploaded data
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT)

    class SourceChoices(models.TextChoices):
        UserUpload = 'upload', 'Upload'
        Dataverse = 'dataverse', 'Dataverse'

    source = models.CharField(max_length=128,
                              choices=SourceChoices.choices)

    # Redis key to store potentially sensitive information
    # during analysis setup
    data_profile_key = models.CharField(max_length=128, blank=True)

    class Meta:
        verbose_name = 'Dataset Information'
        verbose_name_plural = 'Dataset Information'
        ordering = ('name', '-created')

    def __str__(self):
        return self.name


class DataverseFileInfo(DataSetInfo):
    """
    Refers to a DV file from within a DV dataset
    """
    # TODO: This should have all fields from DV API response
    dataverse_file_id = models.CharField(max_length=128)
    doi = models.CharField(max_length=128)
    installation_name = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'Dataverse File Information'
        verbose_name_plural = 'Dataverse File Information'
        ordering = ('name', '-created')

    def __str__(self):
        return f'{self.name} ({self.installation_name})'

    def save(self, *args, **kwargs):
        # Future: is_complete can be auto-filled based on either field values or the STEP
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        self.source = DataSetInfo.SourceChoices.Dataverse
        super(DataverseFileInfo, self).save(*args, **kwargs)



class UploadFileInfo(DataSetInfo):
    """
    Refers to a file uploaded independently of DV
    """

    # user uploaded files, keep them off of the web path, etc.
    #
    data_file = models.FileField('User uploaded files',
                    storage=UPLOADED_FILE_STORAGE,
                    upload_to='user-files/%Y/%m/%d/')

    def save(self, *args, **kwargs):
        # Future: is_complete can be auto-filled based on either field values or the STEP
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        self.source = DataSetInfo.SourceChoices.UserUpload
        super(UploadFileInfo, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.source})'


class DepositorSetupInfo(TimestampedModelWithUUID):
    """
    Metadata and aggregate data about potential release of Dataset
    """
    class DepositorSteps(models.TextChoices):
        """10/21 Waiting for UI finalization to define these"""
        STEP_10_TOA = 'step_10', 'Step 10: Terms of Access'
        STEP_20_UPLOAD_DEPOSIT = 'step_20', 'Step 20: Upload'   # done automatically for Dataverse use case
        STEP_30_DATASET_TYPE = 'step_30', 'Step 30: Dataset Type'

    # each dataset can only have one DepositorSetupInfo object
    dataset = models.OneToOneField(DataSetInfo,
                                   on_delete=models.PROTECT)
    is_complete = models.BooleanField(default=False)
    user_step = models.CharField(max_length=128,
                                 choices=DepositorSteps.choices)
    epsilon = models.FloatField(null=True, blank=True)
    dataset_questions = models.JSONField(null=True)
    variable_ranges = models.JSONField(null=True)
    variable_categories = models.JSONField(null=True)

    class Meta:
        verbose_name = 'Depositor Setup Data'
        verbose_name_plural = 'Depositor Setup Data'
        ordering = ('dataset', '-created')

    def __str__(self):
        return f'{self.dataset} - {self.user_step}'

    def save(self):
        # Future: is_complete can be auto-filled based on either field values or the STEP
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        super(DepositorSetupInfo, self).save(*args, **kwargs)


class AnalysisPlan(TimestampedModelWithUUID):
    """
    Details of request for a differentially private release
    ! Do we want another object to monitor the plan once it is sent to the execution engine?
    """
    class AnalystSteps(models.TextChoices):
        """10/21 Waiting for UI finalization to define these"""
        STEP_010_TOA = 'step_010', 'Step 10: Terms of Access'
        STEP_020_CUSTOM_VARIABLES = 'step_020', 'Step 20: Custom Variables'
        STEP_030_VARIABLE_TYPES = 'step_030', 'Step 30: Confirm Variable Types'
        STEP_100_ANALYSIS_READY = 'step_100', 'Step 100: Analysis ready!'

    name = models.CharField(max_length=255)

    dataset = models.ForeignKey(DataSetInfo,
                                on_delete=models.PROTECT)
    is_complete = models.BooleanField(default=False)
    user_step = models.CharField(max_length=128,
                                 choices=AnalystSteps.choices)
    variable_ranges = models.JSONField(null=True)
    variable_categories = models.JSONField(null=True)
    custom_variables = models.JSONField(null=True)
    dp_statistics = models.JSONField(null=True)

    def __str__(self):
        return f'{self.dataset} - {self.user_step}'

    def save(self):
        # Future: is_complete can be auto-filled based on either field values or the user_step
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        super(AnalysisPlan, self).save(*args, **kwargs)


# TODO: We already have parts of this in analysis/models.py, need to merge them
class ReleaseInfo(TimestampedModelWithUUID):
    """
    Release of differentially private result from an AnalysisPlan
    """
    dataset = models.ForeignKey(DataSetInfo,
                                on_delete=models.PROTECT)

    # redundant
    analysis_plan = models.ForeignKey(AnalysisPlan,
                                      on_delete=models.PROTECT)

    epsilon_used = models.FloatField(null=False, blank=False)
    dp_release = models.JSONField()

    class Meta:
        verbose_name = 'Release Information'
        verbose_name_plural = 'Release Information'
        ordering = ('dataset', '-created')

