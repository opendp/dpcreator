import json
from collections import OrderedDict
from datetime import datetime

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.reverse import reverse as drf_reverse

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataset import static_vals as dstatic
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.model_helpers.models import TimestampedModelWithUUID
from opendp_apps.utils.extra_validators import validate_not_negative, validate_epsilon_or_none
from opendp_apps.utils.variable_info_formatter import format_variable_info

RELEASE_FILE_STORAGE = FileSystemStorage(location=settings.RELEASE_FILE_STORAGE_ROOT)


class ReleaseInfo(TimestampedModelWithUUID):
    """
    Release of differentially private result from an AnalysisPlan
    """
    dataset = models.ForeignKey('dataset.DatasetInfo',
                                on_delete=models.CASCADE)

    epsilon_used = models.FloatField(null=False,
                                     blank=False,
                                     validators=[validate_not_negative])
    dp_release = models.JSONField()

    dp_release_json_file = models.FileField( \
        storage=settings.RELEASE_FILE_STORAGE,
        upload_to='release-files/%Y/%m/%d/',
        blank=True, null=True)

    dp_release_pdf_file = models.FileField(
        storage=settings.RELEASE_FILE_STORAGE,
        upload_to='release-files/%Y/%m/%d/',
        blank=True, null=True)

    dataverse_deposit_info = models.JSONField(blank=True,
                                              null=True,
                                              help_text='Only applies to Dataverse files')

    dv_json_deposit_complete = models.BooleanField(
        default=False,
        help_text='Only applies to Dataverse datasets')

    dv_pdf_deposit_complete = models.BooleanField(
        default=False,
        help_text='Only applies to Dataverse datasets')

    class Meta:
        verbose_name = 'Release Information'
        verbose_name_plural = 'Release Information'
        ordering = ('dataset', '-created')

    def __str__(self):
        return f'{self.dataset}'

    def save(self, *args, **kwargs):
        """Error check the dataverse_deposit_complete flag"""
        super(ReleaseInfo, self).save(*args, **kwargs)

    @mark_safe
    def dp_release_json(self):
        """Return JSON string"""
        if self.dp_release:
            return '<pre>' + json.dumps(self.dp_release, indent=4) + '</pre>'
        return ''

    @mark_safe
    def dataverse_deposit_info_json(self):
        """Return JSON string"""
        if self.dataverse_deposit_info:
            return '<pre>' + json.dumps(self.dataverse_deposit_info, indent=4) + '</pre>'
        return ''

    def download_pdf_url(self):
        """
        URL to download the PDF file
        """
        if (not self.object_id) or (not self.dp_release_pdf_file):
            return None

        # see opendp_app/analysis/views/release_view.py
        #
        download_url = drf_reverse('release-download-pdf', args=[], kwargs={'pk': str(self.object_id)})
        return download_url

    def download_json_url(self):
        """
        URL to download the PDF file
        """
        if (not self.object_id) or (not self.dp_release_json_file):
            return None

        # see opendp_app/analysis/views/release_view.py
        #
        download_url = drf_reverse('release-download-json', args=[], kwargs={'pk': str(self.object_id)})
        return download_url

    def get_analysis_plan_or_None(self):
        """Return the AnalysisPlan object, a reverse lookup of a OneToOneField"""
        try:
            return self.analysisplan
        except ReleaseInfo.analysisplan.RelatedObjectDoesNotExist as _err_obj:
            return None

class ReleaseEmailRecord(TimestampedModelWithUUID):
    """Record the sending of release emails"""
    release_info = models.ForeignKey(ReleaseInfo, on_delete=models.CASCADE)

    success = models.BooleanField(help_text='Did the mail go through?')

    subject = models.CharField(max_length=255)
    to_email = models.CharField(max_length=255)
    from_email = models.CharField(max_length=255)

    email_content = models.TextField(blank=True)

    pdf_attached = models.BooleanField()
    json_attached = models.BooleanField()

    note = models.TextField(blank=True,
                            help_text='Populated if mail not sent successfully')

    def __str__(self):
        return f'{self.release_info}'


class AuxiliaryFileDepositRecord(TimestampedModelWithUUID):
    """Used to record the depositing of ReleaseInfo files to Dataverse as Auxiliary Files"""
    name = models.CharField(max_length=255, blank=True, help_text='auto-filled on save')
    release_info = models.ForeignKey(ReleaseInfo, on_delete=models.CASCADE)

    deposit_success = models.BooleanField(default=False)
    dv_auxiliary_type = models.CharField(max_length=100, choices=dv_static.DV_DEPOSIT_CHOICES)
    dv_auxiliary_version = models.CharField(max_length=50, default='v1', help_text='e.g. "v1", "v2", etc')

    http_status_code = models.IntegerField(help_text='HTTP code', default=-1)
    http_resp_text = models.TextField(blank=True)
    http_resp_json = models.JSONField(null=True, blank=True)
    dv_err_msg = models.CharField(max_length=255, blank=True)

    user_msg_text = models.TextField(blank=True, help_text='text version')
    user_msg_html = models.TextField(blank=True, help_text='HTML version')

    dv_download_url = models.URLField(blank=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return f'{self.release_info} - {self.dv_auxiliary_version} ({self.dv_auxiliary_type})'

    def save(self, *args, **kwargs):
        self.name = AuxiliaryFileDepositRecord.format_name(self)

        if self.http_status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED):
            self.deposit_success = True
        else:
            self.deposit_success = False

        super(AuxiliaryFileDepositRecord, self).save(*args, **kwargs)

    def as_dict(self):
        """Return in dict format for API Use"""

        # Note: the upload/download urls are the same
        #   Don't show the download url on and unsuccessful deposit
        #
        dv_upload_url = dv_download_url_blank_if_fail = self.dv_download_url
        if not self.deposit_success:
            dv_download_url_blank_if_fail = None

        info_dict = OrderedDict({
            'name': self.name,
            'object_id': str(self.object_id),
            'deposit_success': self.deposit_success,

            'dv_download_url': dv_download_url_blank_if_fail,

            'dv_auxiliary_type': self.dv_auxiliary_type,
            'dv_auxiliary_version': self.dv_auxiliary_version,

            'dv_upload_url': dv_upload_url,
            'http_status_code': self.http_status_code,
            'http_resp_text': self.http_resp_text,
            'http_resp_json': self.http_resp_json,
            'dv_err_msg': self.dv_err_msg,

            'user_msg_text': self.user_msg_text,
            'user_msg_html': self.user_msg_html,

            'created': self.created.isoformat(),
            'updated': self.updated.isoformat(),
        })

        return info_dict

    def as_json_string(self, indent=4):
        """Return JSON string"""
        return json.dumps(self.as_dict(), cls=DjangoJSONEncoder, indent=indent)

    @mark_safe
    def json_string_html(self):
        """Return JSON string"""
        return '<pre>' + self.as_json_string() + '</pre>'

    @staticmethod
    def format_name(deposit_rec) -> str:
        """
        Name formatting for the AuxiliaryFileDepositRecord

        :param deposit_rec AuxiliaryFileDepositRecord
        """
        return (f'{deposit_rec.release_info} - {deposit_rec.dv_auxiliary_version}'
                f' ({deposit_rec.dv_auxiliary_type})')


class AnalysisPlan(TimestampedModelWithUUID):
    """
    Details of request for a differentially private release
    ! Do we want another object to monitor the plan once it is sent to the execution engine?
    """

    class AnalystSteps(models.TextChoices):
        """
        Enumeration for statuses during the analysis process
        """
        STEP_0000_INITIALIZED = 'step_100', 'Step 0: Initialized'
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

    name = models.CharField(max_length=255,
                            help_text='Name of the analysis plan')

    description = models.TextField(blank=True, null=True,
                                   help_text='Description of the analysis plan')

    dataset = models.ForeignKey('dataset.DatasetInfo',
                                on_delete=models.CASCADE)

    is_complete = models.BooleanField(default=False)

    user_step = models.CharField(max_length=128,
                                 choices=AnalystSteps.choices,
                                 default=AnalystSteps.STEP_0000_INITIALIZED)

    # Includes variable ranges and categories
    variable_info = models.JSONField(blank=True,
                                     null=True,
                                     help_text='Default value taken from DepositorSetupInfo')

    dp_statistics = models.JSONField(blank=True,
                                     null=True)

    release_info = models.OneToOneField(ReleaseInfo,
                                        on_delete=models.SET_NULL,
                                        # on_delete=models.PROTECT,
                                        null=True,
                                        blank=True)

    wizard_step = models.CharField(max_length=128,
                                   default=dstatic.WIZARD_STEP_DEFAULT_VAL,
                                   help_text='Used by the UI to track the wizard step')

    epsilon = models.FloatField(null=True, blank=True,
                                help_text=('Used for OpenDP operations, starts as the "default_epsilon"'
                                           ' value but may be overridden by the user.'),
                                validators=[validate_epsilon_or_none])

    delta = models.FloatField(null=True,
                              blank=True,
                              default=astatic.DELTA_0,
                              help_text=('Used for OpenDP operations, starts as the "default_delta"'
                                         ' value but may be overridden by the user.'),
                              validators=[validate_not_negative])

    confidence_level = models.FloatField(choices=astatic.CL_CHOICES,
                                         default=astatic.CL_95)

    expiration_date = models.DateTimeField(null=True, blank=True,
                                           help_text='The date the analysis plan expires')

    class Meta:
        ordering = ['dataset', 'name', '-created']

    def __str__(self):
        return f'{self.name}'

    def is_plan_expired(self) -> bool:
        """
        Is the current date past the expiration date?
        @return:
        """
        return make_aware(datetime.now()) > self.expiration_date

    def save(self, *args, **kwargs):
        # Future: is_complete can be auto-filled based on either field values or the user_step
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        if self.user_step == self.AnalystSteps.STEP_1200_PROCESS_COMPLETE:
            self.is_complete = True
        else:
            self.is_complete = False

        if self.variable_info:
            self.variable_info = format_variable_info(self.variable_info)

        super(AnalysisPlan, self).save(*args, **kwargs)

    @mark_safe
    def variable_info_display(self):
        """For admin display of the variable info"""
        if not self.variable_info:
            return 'n/a'

        try:
            info_str = json.dumps(self.variable_info, indent=4)
            return f'<pre>{info_str}</pre>'
        except Exception as ex_obj:
            return f'Failed to convert to JSON string {ex_obj}'
