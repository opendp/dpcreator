"""
Utility for depositing Dataverse auxiliary files related to a ReleaseInfo object
"""

from os.path import basename
import pathlib
import requests
from tempfile import TemporaryFile
from urllib.parse import urlsplit

from django.conf import settings
from django.core.files import File

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.analysis.models import ReleaseInfo
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.user.models import DataverseUser


class DataverseDepositUtil(BasicErrCheck):

    ERR_FAILED_TO_READ_DATASET = 'Failed to read the dataset.'
    ERR_DATASET_POINTER_NOT_SET = 'In order to profile the data, the "dataset_pointer" must be set.'

    def __init__(self, release_info: ReleaseInfo, **kwargs):
        """Initiate with a ReleaseInfo object"""
        self.release_info = release_info
        self.dataverse_user = None

        self.run_basic_check()
        self.deposit_files()

    def run_basic_check(self):
        """Make sure the correct data is available and the release can be deposited"""
        if self.has_error():
            return

        # Is this a Dataverse dataset?
        #
        if not self.release_info.dataset.is_dataverse_dataset():
            self.add_err_msg(astatic.ERR_MSG_DEPOSIT_NOT_DATAVERSE)
            return

        # Is the DataverseUser in the database?
        #
        dv_user = self.release_info.dataset.get_dataverse_user()
        if dv_user is None:
            self.add_err_msg(astatic.ERR_MSG_DEPOSIT_NO_DV_USER)
            return


        # Is the JSON release file available?
        #
        if not self.release_info.dp_release_json_file:
            self.add_err_msg(astatic.ERR_MSG_DEPOSIT_NO_JSON_FILE)
            return

        # Is the PDF release file available?
        #
        #if not self.release_info.dp_release_pdf_file:
        #    self.add_err_msg(astatic.ERR_MSG_DEPOSIT_NO_PDF_FILE)
        #    return


    def deposit_files(self):
        """Deposit files to Dataverse"""
        if self.has_error():
            return

        # https://guides.dataverse.org/en/latest/developers/aux-file-support.html
