from urllib.parse import urlencode

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe
from opendp_apps.dataverses import static_vals as dv_static

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
    use_mock_dv_api = models.BooleanField('Use Mock Dataverse API', default=False)


    apiSensitiveDataReadToken = models.CharField(max_length=255, blank=True)
    apiGeneralToken = models.CharField(max_length=255, blank=True)
    filePid = models.CharField(max_length=255, blank=True)
    datasetPid = models.CharField(max_length=255, blank=True)

    ddi_content = models.TextField(help_text='Use XML', blank=True)

    schema_org_content = models.JSONField(null=True, blank=True)

    user_info = models.JSONField(null=True, blank=True)

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

    @mark_safe
    def user_info_link(self):
        """
        Link to the user info API
        """
        if not (self.use_mock_dv_api and self.apiGeneralToken):
            return 'n/a'

        user_lnk = reverse('view_get_user_info')
        return f'<a href="{user_lnk}">API: user info</a>'
    user_info_link.allow_tags = True


    @mark_safe
    def ddi_info_link(self):
        """
        Retrieve the DDI information
        """
        if not (self.use_mock_dv_api and self.ddi_content and self.datasetPid):
            return 'n/a'

        dataset_lnk = reverse('view_get_dataset_export')
        return (f'<a href="{dataset_lnk}?persistentId={self.datasetPid}'
                f'&exporter={dv_static.EXPORTER_FORMAT_DDI}">ddi info</a>')
    ddi_info_link.allow_tags = True


    @mark_safe
    def schema_org_info_link(self):
        """
        Retrieve the schema.org information
        """
        if not (self.use_mock_dv_api and self.schema_org_content and self.datasetPid):
            return 'n/a'

        dataset_lnk = reverse('view_get_dataset_export')
        return (f'<a href="{dataset_lnk}?persistentId={self.datasetPid}'
                f'&exporter={dv_static.EXPORTER_FORMAT_SCHEMA_ORG}">schema.org info</a>')
    schema_org_info_link.allow_tags = True



    def get_dataverse_ddi_url(self):
        """Mock url for retrieving the DDI"""
        if not self.datasetPid:
            # Requires the dataset Pid
            return None

        params = dict(exporter='ddi',
                      persistentId=self.datasetPid)
        qstr = urlencode(params)

        return reverse('view_get_dataset_export') + '?' + qstr

    def as_dict(self):
        """
        Return the params as a Python dict
        """
        params = dict(fileId=self.fileId,
                      siteUrl=self.siteUrl,
                      apiSensitiveDataReadToken=self.apiSensitiveDataReadToken,
                      apiGeneralToken=self.apiGeneralToken,
                      datasetPid=self.datasetPid, )
        return params

    def get_manifest_url_params(self):
        """
        Build a url string with the params
        """
        params = self.as_dict()

        qstr = urlencode(params)

        return qstr

    @mark_safe
    def dataverse_incoming_link(self):
        """
        link to mimic incoming DV
        """
        #if not (self.use_mock_dv_api and self.apiGeneralToken):
        #    return 'n/a'

        user_lnk = reverse('view_dataverse_incoming_1')
        url_params = self.get_manifest_url_params()

        if self.use_mock_dv_api:
            return f'<a href="{user_lnk}?{url_params}" target="_blank">Mock: Dataverse incoming link</a>'
        else:
            return f'<a href="{user_lnk}?{url_params}" target="_blank">Dataverse incoming link (public dataset)</a>'

    dataverse_incoming_link.allow_tags = True

    @mark_safe
    def dataverse_incoming_link_2(self):
        """
        link to mimic incoming DV
        """
        #if not (self.use_mock_dv_api and self.apiGeneralToken):
        #    return 'n/a'

        user_lnk = reverse('view_dataverse_incoming_2')
        url_params = self.get_manifest_url_params()

        if self.use_mock_dv_api:
            return f'<a href="{user_lnk}?{url_params}" target="_blank">Test 2: Mock Dataverse incoming link</a>'
        else:
            return f'<a href="{user_lnk}?{url_params}" target="_blank">Test 2: Dataverse incoming link (public dataset)</a>'

    dataverse_incoming_link_2.allow_tags = True