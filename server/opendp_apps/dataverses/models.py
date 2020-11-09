from urllib.parse import urlencode

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.conf import settings
from django.urls import reverse

from opendp_apps.model_helpers.models import \
    (TimestampedModelWithUUID,)

UPLOADED_FILE_STORAGE = FileSystemStorage(location=settings.UPLOADED_FILE_STORAGE_ROOT)


class RegisteredDataverse(TimestampedModelWithUUID):
    """
    Dataverses that are allowed to use the OpenDP App
    - This is not a substitute for a whitelist but contains a list of Dataverses
      which have external tools pointing to application instance
    """
    name = models.CharField(max_length=255, unique=True)
    dataverse_url = models.URLField(unique=True,
                                    help_text='No trailing slash.')
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text='optional')

    def __str__(self):
        return '%s (%s)' % (self.name, self.dataverse_url)

    def save(self, *args, **kwargs):
        # remove any trailing slashes
        while self.dataverse_url.endswith('/'):
            self.dataverse_url = self.dataverse_url[:-1]

        self.dataverse_url = self.dataverse_url.lower()

        super(RegisteredDataverse, self).save(*args, **kwargs)

    class Meta:
        ordering = ('name',)


class ManifestTestParams(TimestampedModelWithUUID):
    """
    Used to to create test params for a mock "incoming" Dataverse request
    """
    # example: https://dataverse.harvard.edu/file.xhtml?fileId=4164587&datasetVersionId=215032
    # example: https://dataverse.harvard.edu/file.xhtml?persistentId=doi:10.7910/DVN/OLD7MB/ZI4N3J&version=4.2
    #
    # fileid=4164587&siteUrl=https://dataverse.harvard.edu&datasetid=4164585&datasetversion=1.0&locale=en
    #
    name = models.CharField(max_length=255, blank=True)
    fileId = models.IntegerField()
    siteUrl = models.URLField(max_length=255, blank=True)
    apiSensitiveDataReadToken = models.CharField(max_length=255, blank=True)
    apiGeneralToken = models.CharField(max_length=255, blank=True)
    filePid = models.CharField(max_length=255, blank=True)
    datasetPid = models.CharField(max_length=255, blank=True)

    ddi_content = models.TextField(help_text='Use XML', blank=True)

    raw_file = models.FileField(storage=UPLOADED_FILE_STORAGE,
                                upload_to='mock-files/%Y/%m/%d/',
                                blank=True, null=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            if self.filePid:
                self.name = self.filePid
            else:
                self.name = f'file id: {self.filePid}'

        super(ManifestTestParams, self).save(*args, **kwargs)

    class Meta:
        verbose_name = ('Manifest Test Parameter')
        verbose_name_plural = ('Manifest Test Parameters')

    def get_dataverse_ddi_url(self):
        """Mock url for retrieving the DDI"""
        if not self.datasetPid:
            # Requires the dataset Pid
            return None

        params = dict(exporter='ddi',
                      persistentId=self.datasetPid)
        qstr = urlencode(params)

        return reverse('view_get_dataset_export') + '?' + qstr


"""
 {
        "fileId":"{fileId}"
      },
      {
        "apiSensitiveDataReadToken":"{apiToken}"
      },
      {
        "apiGeneralToken":"{apiToken}"
      },
      {
        "siteUrl":"{siteUrl}"
      },
      {
        "filePid":"{filePid}"
      },
      {
        "datasetPid":"{datasetPid}"
      },
      {
        "datasetVersion":"{datasetVersion}"
      }
"""