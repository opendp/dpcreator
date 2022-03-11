from urllib.parse import urlencode
from typing import Union
import uuid

from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe

from rest_framework.reverse import reverse as drf_reverse

from django_cryptography.fields import encrypt


from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp

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
        self.dataverse_url = RegisteredDataverse.format_dv_url(self.dataverse_url)

        super(RegisteredDataverse, self).save(*args, **kwargs)

    class Meta:
        ordering = ('name',)

    @staticmethod
    def get_registered_dataverse(dv_url):
        """Based on the Dataverse url, return the RegisteredDataverse or None"""
        dv_url = RegisteredDataverse.format_dv_url(dv_url)

        if not dv_url:
            return None

        return RegisteredDataverse.objects.filter(dataverse_url=dv_url).first()

    @staticmethod
    def is_site_url_registered(dv_url):
        """Does the site_url match a RegisteredDataverse?"""
        dv_url = RegisteredDataverse.format_dv_url(dv_url)

        if not dv_url:
            return False

        if RegisteredDataverse.objects.filter(dataverse_url=dv_url).count() > 0:
            return True
        return False

    @staticmethod
    def hack_format_dv_url_http(dv_url):
        """Hack for DV external tools change; If the url does not start with http(s), add 'http://'"""
        if not isinstance(dv_url, str):
            return None

        dv_url = dv_url.lower().strip()

        if not dv_url:
            return None

        if dv_url.startswith('http://') or dv_url.startswith('https://'):
            return dv_url

        dv_url = f'http://{dv_url}'

        return dv_url

    @staticmethod
    def format_dv_url(dv_url):
        """Trim trailing "/" and make lowercase. If it's an empty string or None, return None"""
        if not isinstance(dv_url, str):
            return None

        dv_url = dv_url.strip()
        while dv_url and dv_url.endswith('/'):
            dv_url = dv_url[:-1]

        if not dv_url:
            return None

        return dv_url.lower()


class DataverseParams(TimestampedModelWithUUID):
    """
    Abstract class for Dataverse Params
    Reference: https://guides.dataverse.org/en/latest/api/external-tools.html
    # TODO: These should be snakecase rather than camelcase (PEP standard)
    """
    fileId = models.IntegerField()

    datasetPid = models.CharField(max_length=255,
                                  help_text='Dataset DOI')

    filePid = models.CharField(max_length=255,
                               blank=True,
                               help_text='File DOI')

    apiGeneralToken = encrypt(models.CharField(max_length=255))

    class Meta:
        abstract = True


    def as_dict(self):
        """
        Return the params as a Python dict
        """
        params = {dv_static.DV_PARAM_FILE_ID: self.fileId,
                  #dv_static.DV_PARAM_SITE_URL: self.site_url,
                  dv_static.DV_API_GENERAL_TOKEN: self.apiGeneralToken,
                  dv_static.DV_PARAM_DATASET_PID: self.datasetPid,
                  dv_static.DV_PARAM_FILE_PID: self.filePid}

        return params


class DataverseHandoff(DataverseParams):
    """
    Dataverse parameters passed to the OpenDP App
    """
    name = models.CharField(max_length=255, blank=True)
    dv_installation = models.ForeignKey(RegisteredDataverse,
                                        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Dataverse Handoff Parameter'
        verbose_name_plural = 'Dataverse Handoff Parameters'

    def __str__(self):
        return str(self.object_id)

    def save(self, *args, **kwargs):

        #if not self.dv_installation:
        #    self.dv_installation = DataverseHandoff.get_registered_dataverse(self.siteUrl)

        # Set then name to the File DOI or ID
        if not self.name:
            if self.filePid:
                self.name = f'{self.object_id} File DOI: {self.filePid}'
            else:
                self.name = f'{self.object_id} File ID: {self.fileId}'

        super(DataverseHandoff, self).save(*args, **kwargs)

    @staticmethod
    def delete_handoff(dv_handoff_id: Union[uuid.uuid4, str]) -> bool:
        """
        Delete a DataverseHandoff object.
        Returns True if the object is deleted or is not found
        """
        try:
            dv_handoff = DataverseHandoff.objects.get(object_id=dv_handoff_id)
            dv_handoff.delete()
        except DataverseHandoff.DoesNotExist:
            return True
        except ValidationError: # str is not a UUID, etc.
            return False

        return True

class ManifestTestParams(DataverseParams):
    """
    Used to to create test params for a mock "incoming" Dataverse request
    """
    # example: https://dataverse.harvard.edu/file.xhtml?fileId=4164587&datasetVersionId=215032
    # example: https://dataverse.harvard.edu/file.xhtml?persistentId=doi:10.7910/DVN/OLD7MB/ZI4N3J&version=4.2
    #
    # fileid=4164587&siteUrl=https://dataverse.harvard.edu&datasetid=4164585&datasetversion=1.0&locale=en
    #
    name = models.CharField(max_length=255, blank=True)

    site_url = models.CharField(max_length=255)
    use_mock_dv_api = models.BooleanField('Use Mock Dataverse API', default=False)

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


    def make_test_handoff_object(self):
        """For unit tests, make a DataverseHandoff object with the same params"""

        params = self.as_dict()
        if dv_static.DV_PARAM_SITE_URL in params:
            del params[dv_static.DV_PARAM_SITE_URL]

        dv_handoff = DataverseHandoff(**params)

        reg_dv = RegisteredDataverse.get_registered_dataverse(self.site_url)
        if not reg_dv:
            return err_resp('No RegisteredDataverse for site_url {self.site_url}')

        dv_handoff.dv_installation = reg_dv
        dv_handoff.save()

        return ok_resp(data=dv_handoff)


    def get_manifest_url_params(self, selected_params=None):
        """
        Build a url string with the params
        selected_params - optional, only return params in this list
                e.g. [dv_static.DV_API_GENERAL_TOKEN,
                      dv_static.DV_PARAM_SITE_URL]
        """
        params = self.as_dict()
        if selected_params:
            for key in list(params):
                if not key in selected_params:
                    del params[key]

        qstr = urlencode(params)

        return qstr

    @mark_safe
    def view_as_dict_link(self):
        """Link to return the params in JSON"""
        dataset_lnk = reverse('view_as_dict',
                              kwargs=dict(object_id=self.object_id))

        return f'<a href="{dataset_lnk}">API: Get Params as JSON</a>'

    view_as_dict_link.allow_tags = True


    @mark_safe
    def mock_user_info_link(self):
        """
        Link to the user info API
        """
        if not (self.use_mock_dv_api and self.apiGeneralToken):
            return 'n/a'

        user_lnk = reverse('view_get_user_info')
        return f'<a href="{user_lnk}">API: user info</a>'
    mock_user_info_link.allow_tags = True


    '''
    @mark_safe
    def ddi_info_link(self):
        """
        Retrieve the DDI information
        """
        if not (self.use_mock_dv_api and self.datasetPid):
            return 'n/a'

        dataset_lnk = reverse('view_get_dataset_export')
        return (f'<a href="{dataset_lnk}?persistentId={self.datasetPid}'
                f'&exporter={dv_static.EXPORTER_FORMAT_DDI}">ddi info</a>')
    ddi_info_link.allow_tags = True
    '''

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

    def as_dict(self):
        """
        Return the params as a Python dict
        """
        params = {dv_static.DV_PARAM_FILE_ID: self.fileId,
                  dv_static.DV_PARAM_SITE_URL: self.site_url,
                  dv_static.DV_API_GENERAL_TOKEN: self.apiGeneralToken,
                  dv_static.DV_PARAM_DATASET_PID: self.datasetPid,
                  dv_static.DV_PARAM_FILE_PID: self.filePid}

        return params

    def get_dataverse_ddi_url(self):
        """Mock url for retrieving the DDI"""
        if not self.datasetPid:
            # Requires the dataset Pid
            return None

        params = dict(exporter='ddi',
                      persistentId=self.datasetPid)
        qstr = urlencode(params)

        return reverse('view_get_dataset_export') + '?' + qstr

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

    @mark_safe
    def dataverse_handoff_test_link(self):
        """Mock an incoming Dataverse Call via the UI"""
        handoff_url = drf_reverse('dv-handoff-dv-orig-create', args=[], kwargs={})

        url_params = self.get_manifest_url_params()

        if self.use_mock_dv_api:
            return f'<a href="{handoff_url}?{url_params}" target="_blank">Handoff!: Mock Dataverse incoming link</a>'
        else:
            return f'<a href="{handoff_url}?{url_params}" target="_blank">Handoff!: Dataverse incoming link (public dataset)</a>'
    dataverse_handoff_test_link.allow_tags = True


