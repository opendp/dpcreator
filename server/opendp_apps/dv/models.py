from django.db import models
from opendp_apps.model_helpers.models import \
    (TimestampedModelWithUUID,)

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
    name = models.CharField(max_length=255, blank=True)
    fileId = models.IntegerField()
    apiSensitiveDataReadToken = models.CharField(max_length=255, blank=True)
    apiGeneralToken = models.CharField(max_length=255, blank=True)
    siteUrl = models.URLField(max_length=255, blank=True)
    filePid = models.CharField(max_length=255, blank=True)
    datasetPid = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            if self.filePid:
                self.name = self.filePid
            else:
                self.name = f'file id: {self.filePid}'

        super(ManifestTestParams, self).save(*args, **kwargs)

    #def

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