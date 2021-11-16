"""
Utility for depositing Dataverse auxiliary files related to a ReleaseInfo object
"""

from os.path import basename
import requests
from rest_framework import status

from django.conf import settings
from django.template.loader import render_to_string

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.analysis.models import ReleaseInfo, AuxiliaryFileDepositRecord
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
                'dv_deposit_type': dv_static.DV_DEPOSIT_TYPE_DP_JSON,
                'file_field': self.release_info.dp_release_json_file,
                'complete_field': self.release_info.dv_json_deposit_complete
            },
            {
                'dv_deposit_type': dv_static.DV_DEPOSIT_TYPE_DP_PDF,
                'file_field': self.release_info.dp_release_pdf_file,
                'complete_field': self.release_info.dv_pdf_deposit_complete
            }
        ]

        format_version = 'v1'   # hardcoded for now..

        num_deposits = 0
        expected_num_deposits = 0
        for file_info in file_info_list:

            # build the deposit url
            #
            dv_deposit_url = (f'{self.dv_dataset.dv_installation.dataverse_url}'
                      f'/api/access/datafile'
                      f'/{self.dv_dataset.dataverse_file_id}/auxiliary'
                      f'/{file_info["dv_deposit_type"]}/{format_version}')

            # build the download url -- saved if the deposit works
            #            #
            dv_download_url = dv_deposit_url

            deposit_record = AuxiliaryFileDepositRecord(release_info=self.release_info,
                                                        dv_auxiliary_type=file_info["dv_deposit_type"],
                                                        dv_auxiliary_version=format_version,
                                                        dv_download_url=dv_download_url)

            payload = dict(origin=settings.DP_CREATOR_APP_NAME,
                           isPublic=True,
                           type=file_info["dv_deposit_type"])

            # Assuming actual filepath for initial pass;
            #   For azure/s3 update: https://github.com/jschneier/django-storages/tree/master/storages/backends
            file_field = file_info["file_field"]
            if not file_field:
                # file not available to deposit!
                continue
            expected_num_deposits += 1

            files = {'file': open(file_field.path, 'rb')}

            print('dv_url', dv_deposit_url)
            response = requests.post(dv_deposit_url,
                                     headers=headers,
                                     data=payload,
                                     files=files)

            # debug start
            print('status_code: ', response.status_code)
            print('response.text', response.text)
            print('-' * 40)
            if response.status_code == status.HTTP_200_OK:
                print('response json', response.json())
            # (debug end)

            # Record the HTTP status code and response text
            #
            deposit_record.http_status_code = response.status_code
            deposit_record.http_resp_text = response.text

            # Did the deposit work?
            #
            if response.status_code == status.HTTP_200_OK:
                # Successful deposit!
                deposit_record.http_resp_json = response.json()
                deposit_record.save()

                file_info["complete_field"] = True
                self.release_info.save()
                num_deposits += 1
            else:
                # Deposit failed
                #
                deposit_record.user_msg = dv_static.ERR_MSG_JSON_DEPOSIT_FAILED
                deposit_record.save()
                self.add_err_msg(dv_static.ERR_MSG_JSON_DEPOSIT_FAILED)

            # Format user messages
            #  - deposit_record needs to be saved before this is set--saving sets the "deposit_success" field
            #
            deposit_record.user_msg_text =  render_to_string('dataverses/auxiliary_deposit.txt',
                                                             {'deposit': deposit_record})

            deposit_record.user_msg_html = render_to_string('dataverses/auxiliary_deposit.html',
                                                            {'deposit': deposit_record})

            deposit_record.save()

        if num_deposits == 0:
            self.add_err_msg((f'No files were deposited. (Expected: '
                              f'{expected_num_deposits} deposit(s)'))
