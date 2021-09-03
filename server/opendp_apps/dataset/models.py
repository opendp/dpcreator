from collections import OrderedDict
import json

from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.conf import settings
from django_cryptography.fields import encrypt

from polymorphic.models import PolymorphicModel

from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.model_helpers.models import \
    (TimestampedModelWithUUID,)


UPLOADED_FILE_STORAGE = FileSystemStorage(location=settings.UPLOADED_FILE_STORAGE_ROOT)


class DataSetInfo(TimestampedModelWithUUID, PolymorphicModel):
    """
    Base type for table that either holds DV data
    or a file upload
    """
    class SourceChoices(models.TextChoices):
        UserUpload = 'upload', 'Upload'
        Dataverse = 'dataverse', 'Dataverse'

    name = models.CharField(max_length=128)

    # user who initially added/uploaded data
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT)

    source = models.CharField(max_length=128,
                              choices=SourceChoices.choices)

    # Switch to encryption!
    #
    data_profile = models.JSONField(default=None,
                                    null=True, blank=True,
                                    encoder=DjangoJSONEncoder)

    profile_variables = models.JSONField(default=None,
                                    null=True, blank=True,
                                    encoder=DjangoJSONEncoder)

    #data_profile = encrypt(models.JSONField(default=None, null=True, blank=True, encoder=DjangoJSONEncoder))

    # Formatted version of the "data_profile"
    # profile_variables = encrypt(models.JSONField(default=None, null=True, blank=True, encoder=DjangoJSONEncoder))

    # Switch to encryption!
    #
    source_file = models.FileField(storage=UPLOADED_FILE_STORAGE,
                                   upload_to='source-file/%Y/%m/%d/',
                                   blank=True, null=True)

    class Meta:
        verbose_name = 'Dataset Information'
        verbose_name_plural = 'Dataset Information'
        ordering = ('name', '-created')

    def __str__(self):
        return self.name

    def as_dict(self):
        """
        Return as dict
        """
        info = dict(id=self.id,
                    creator=str(self.creator),
                    source=str(self.source),
                    updated=str(self.updated),
                    created=str(self.created),
                    object_id=self.object_id.hex)

        return info

    def get_profile_variables(self):
        """Return the profile_variables and DataSetInfo object_id as an OrderedDict or None."""
        if not self.profile_variables:
            return None

        od = OrderedDict(dict(object_id=self.object_id))
        od.update(self.profile_variables)

        return od

    def data_profile_as_dict(self):
        """Return the dataprofile as a dict or None. Messy in that this is an encrypted JSONField"""
        if not self.data_profile:
            return None

        try:
            if isinstance(self.data_profile, str):  # messy; decode escaped string to JSON string
                load1 = json.loads(self.data_profile, object_pairs_hook=OrderedDict)
            else:
                load1 = self.data_profile

            if isinstance(load1, dict):
                return load1

            return json.loads(load1, object_pairs_hook=OrderedDict) # JSON string to OrderedDict

        except json.JSONDecodeError:
            return None

    def data_profile_as_json_str(self):
        """Return the dataprofile as a dict or None. Messy in that this is an encrypted JSONField"""
        if not self.data_profile:
            return None

        try:
            return json.loads(self.data_profile)
        except json.JSONDecodeError:
            return None


class DataverseFileInfo(DataSetInfo):
    """
    Refers to a DV file from within a DV dataset
    """
    dv_installation = models.ForeignKey(RegisteredDataverse, on_delete=models.PROTECT)
    dataverse_file_id = models.IntegerField()
    dataset_doi = models.CharField(max_length=255)
    file_doi = models.CharField(max_length=255, blank=True)
    dataset_schema_info = models.JSONField(null=True, blank=True)
    file_schema_info = models.JSONField(null=True, blank=True)
    depositor_setup_info = models.OneToOneField('analysis.DepositorSetupInfo', on_delete=models.PROTECT, null=True)

    class Meta:
        verbose_name = 'Dataverse File Information'
        verbose_name_plural = 'Dataverse File Information'
        ordering = ('name', '-created')
        constraints = [
            models.UniqueConstraint(fields=['dv_installation', 'dataverse_file_id'],
                                    name='unique Dataverse file')
        ]

    def __str__(self):
        return f'{self.name} ({self.dv_installation.name})'

    def save(self, *args, **kwargs):
        # Future: is_complete can be auto-filled based on either field values or the STEP
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        if not self.depositor_setup_info:
            dsi = DepositorSetupInfo.objects.create(creator=self.creator)
            self.depositor_setup_info = dsi
        if not self.name:
            self.name = f'{self.dataset_doi} ({self.dv_installation})'
        self.source = DataSetInfo.SourceChoices.Dataverse
        super(DataverseFileInfo, self).save(*args, **kwargs)

    @property
    def status(self):
        """
        """
        try:
            return self.depositor_setup_info.user_step
        except DepositorSetupInfo.DoesNotExist:
            return DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED

    @property
    def status_name(self):
        """
        """
        try:
            return self.depositor_setup_info.user_step.label
        except DepositorSetupInfo.DoesNotExist:
            return DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED.label

    def as_dict(self):
        """
        Return as dict
        """
        info = dict(id=self.id,
                    name=self.name,
                    creator=str(self.creator),
                    source=str(self.source),
                    dv_installation=self.dv_installation,
                    dataverse_file_id=self.dataverse_file_id,
                    dataset_doi=self.dataset_doi,
                    file_doi=self.file_doi,
                    updated=str(self.updated),
                    created=str(self.created),
                    object_id=self.object_id.hex)

        return info


class UploadFileInfo(DataSetInfo):
    """
    Refers to a file uploaded independently of DV
    """
    depositor_setup_info = models.OneToOneField('analysis.DepositorSetupInfo', on_delete=models.PROTECT, null=True)

    def save(self, *args, **kwargs):
        # Future: is_complete can be auto-filled based on either field values or the STEP
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        self.source = DataSetInfo.SourceChoices.UserUpload
        super(UploadFileInfo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Upload File Information'
        verbose_name_plural = 'Upload File Information'
        ordering = ('name', '-created')

    def __str__(self):
        return f'{self.name} ({self.source})'

    def as_dict(self):
        """
        Return as dict
        """
        info = dict(self.id,
                    name=self.name,
                    creator=str(self.creator),
                    source=str(self.source),
                    #data_file=self.data_file,
                    updated=str(self.updated),
                    created=str(self.created),
                    object_id=self.object_id.hex)

        return info
