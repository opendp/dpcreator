from collections import OrderedDict
from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import CASCADE
from django.conf import settings
from django_cryptography.fields import encrypt

from polymorphic.models import PolymorphicModel

from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.model_helpers.models import \
    (TimestampedModelWithUUID,)


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

    # Switch to encryption!
    #
    data_profile = encrypt(models.JSONField(default=None, null=True, encoder=DjangoJSONEncoder))

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


class DataverseFileInfo(DataSetInfo):
    """
    Refers to a DV file from within a DV dataset
    """
    # TODO: This should have all fields from DV API response
    dv_installation = models.ForeignKey(RegisteredDataverse, on_delete=models.PROTECT)
    dataverse_file_id = models.IntegerField()
    dataset_doi = models.CharField(max_length=255)
    file_doi = models.CharField(max_length=255, blank=True)
    dataset_schema_info = models.JSONField(blank=True)
    file_schema_info = models.JSONField(blank=True)

    class Meta:
        verbose_name = 'Dataverse File Information'
        verbose_name_plural = 'Dataverse File Information'
        ordering = ('name', '-created')
        constraints = [
            models.UniqueConstraint(fields=['dv_installation', 'dataverse_file_id'],
                                    name='unique Dataverse file')
        ]

    def __str__(self):
        return f'{self.name} ({self.installation_name})'

    def save(self, *args, **kwargs):
        # Future: is_complete can be auto-filled based on either field values or the STEP
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        self.source = DataSetInfo.SourceChoices.Dataverse
        super(DataverseFileInfo, self).save(*args, **kwargs)

    def as_dict(self):
        """
        Return as dict
        """
        info = dict(id=self.id,
                    name=self.name,
                    creator=str(self.creator),
                    source=str(self.source),
                    installation_name=self.installation_name,
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

    # user uploaded files, keep them off of the web path
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
                    data_file=self.data_file,
                    updated=str(self.updated),
                    created=str(self.created),
                    object_id=self.object_id.hex)

        return info
