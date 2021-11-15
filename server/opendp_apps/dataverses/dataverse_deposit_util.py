"""
Utility for depositing Dataverse auxiliary files related to a ReleaseInfo object
"""

from os.path import basename
import requests
from rest_framework import status

from django.conf import settings

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.analysis.models import ReleaseInfo
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataverses import static_vals as dv_static


class DataverseDepositUtil(BasicErrCheck):
    """
    Given a ReleaseInfo, deposit any files to Dataverse
    """
    ERR_FAILED_TO_READ_DATASET = 'Failed to read the dataset.'
    ERR_DATASET_POINTER_NOT_SET = 'In order to profile the data, the "dataset_pointer" must be set.'

    def __init__(self, release_info: ReleaseInfo, **kwargs):
        """
        Initiate with a ReleaseInfo object

        param ReleaseInfo release_info: ReleaseInfo with objects to deposit
        """
        self.release_info = release_info
        self.dv_user = None  # to be populated in the deposit process
        self.dv_dataset = None

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

        # shortcut to dv_dataset
        #
        self.dv_dataset = self.release_info.dataset.get_dataverse_file_info()
        if self.dv_dataset is None:
            self.add_err_msg(dv_static.ERR_MSG_DEPOSIT_NO_DV_DATASET_INFO)
            return

        # Is the DataverseUser in the database?
        #
        self.dv_user = self.release_info.dataset.get_dataverse_user()
        if self.dv_user is None:
            self.add_err_msg(astatic.ERR_MSG_DEPOSIT_NO_DV_USER)
            return



        # Is the JSON release file available?
        #
        if not self.release_info.dp_release_json_file:
            self.add_err_msg(astatic.ERR_MSG_DEPOSIT_NO_JSON_FILE)
            return

        # Has the JSON release file already been deposited?
        #
        if self.release_info.dv_json_deposit_complete:
            self.add_err_msg(dv_static.ERR_MSG_JSON_DEPOSIT_ALREADY_COMPLETE)
            return

        # Is the PDF release file available?
        #
        #if not self.release_info.dp_release_pdf_file:
        #    self.add_err_msg(astatic.ERR_MSG_DEPOSIT_NO_PDF_FILE)
        #    return

        #if self.release_info.dv_pdf_deposit_complete:
        #    self.add_err_msg(dv_static.ERR_MSG_PDF_DEPOSIT_ALREADY_COMPLETE)
        #    return

    def deposit_files(self):
        """
        Deposit files to Dataverse!
        ref: https://guides.dataverse.org/en/latest/developers/aux-file-support.html
        """
        if self.has_error():
            return

        # Prepare Dataverse data
        headers = {dv_static.HEADER_KEY_DATAVERSE: self.dv_user.dv_general_token}

        file_info_list = [
            {
                'format_tag': dv_static.DV_DEPOSIT_TYPE_DP_JSON,
                'file_field': self.release_info.dp_release_json_file,
                'complete_field': self.release_info.dv_json_deposit_complete
            },
            {
                'format_tag': dv_static.DV_DEPOSIT_TYPE_DP_PDF,
                'file_field': self.release_info.dp_release_pdf_file,
                'complete_field': self.release_info.dv_pdf_deposit_complete
            }
        ]

        format_version = 'v1'   # hardcoded for now..

        for file_info in file_info_list:

            dv_url = (f'{self.dv_dataset.dv_installation.dataverse_url}'
                      f'/api/access/datafile'
                      f'/{self.dv_dataset.dataverse_file_id}/auxiliary'
                      f'/{file_info["format_tag"]}/{format_version}')
            #dv_url = (f'{dv_url}api/access/datafile/{dv_cred.FILE_ID}'
            #          f'/auxiliary/{FORMAT_TAG}/{FORMAT_VERSION}')

            payload = dict(origin=settings.DP_CREATOR_APP_NAME,
                           isPublic=True,
                           type=file_info["format_tag"])

            # Assuming actual filepath for initial pass;
            #   For azure/s3 update: https://github.com/jschneier/django-storages/tree/master/storages/backends
            file_field = file_info["file_field"]

            files = {'file': open(file_field.path, 'rb')}

            print('dv_url', dv_url)
            response = requests.post(dv_url,
                                     headers=headers,
                                     data=payload,
                                     files=files)

            print('status_code: ', response.status_code)
            print('response.text', response.text)
            print('-' * 40)
            if response.status_code == status.HTTP_200_OK:
                print('response json', response.json())

            if response.status_code == status.HTTP_200_OK:
                file_info["complete_field"] = True
                self.release_info.save()
            else:
                self.add_err_msg(dv_static.ERR_MSG_JSON_DEPOSIT_FAILED)

