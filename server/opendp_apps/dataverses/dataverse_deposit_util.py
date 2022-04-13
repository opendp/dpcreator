"""
Utility for depositing Dataverse auxiliary files related to a ReleaseInfo object
"""
import logging

from collections import OrderedDict
from os.path import basename

import requests
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework import status

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.models import ReleaseInfo, AuxiliaryFileDepositRecord
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck


logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DataverseDepositUtil(BasicErrCheck):
    """
    Given a ReleaseInfo, deposit any files to Dataverse
    """

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
        self.update_release_info()

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
        qparams = dict(release_info=self.release_info,
                       dv_auxiliary_type=dv_static.DV_DEPOSIT_TYPE_DP_JSON)
        json_rec1 = AuxiliaryFileDepositRecord.objects.filter(**qparams).first()
        if json_rec1 is not None:
            self.add_err_msg(dv_static.ERR_MSG_JSON_DEPOSIT_ALREADY_COMPLETE)
            return

        """
        # Is the PDF release file available?
        #
        if not self.release_info.dp_release_pdf_file:
            self.add_err_msg(astatic.ERR_MSG_DEPOSIT_NO_PDF_FILE)
            return
        """

        # Has the PDF release file already been deposited?
        #
        qparams = dict(release_info=self.release_info,
                       dv_auxiliary_type=dv_static.DV_DEPOSIT_TYPE_DP_PDF)
        json_rec2 = AuxiliaryFileDepositRecord.objects.filter(**qparams).first()
        if json_rec2 is not None:
            self.add_err_msg(dv_static.ERR_MSG_PDF_DEPOSIT_ALREADY_COMPLETE)
            return

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
                'TYPE': 'DP',
                'FILETYPE': 'application/json',
            },
            {
                'dv_deposit_type': dv_static.DV_DEPOSIT_TYPE_DP_PDF,
                'file_field': self.release_info.dp_release_pdf_file,
                'TYPE': 'DP',
                'FILETYPE': 'application/pdf',
            }
        ]

        format_version = 'v1'  # hardcoded for now..

        num_deposits = 0
        expected_num_deposits = 0
        for file_info in file_info_list:

            # build the deposit/download url
            #
            dv_deposit_url = (f'{self.dv_dataset.dv_installation.dataverse_url}'
                              f'/api/access/datafile'
                              f'/{self.dv_dataset.dataverse_file_id}/auxiliary'
                              f'/{file_info["dv_deposit_type"]}/{format_version}')

            dv_download_url = dv_deposit_url

            # Create a AuxiliaryFileDepositRecord to log the attempt
            #
            deposit_record = AuxiliaryFileDepositRecord(release_info=self.release_info,
                                                        dv_auxiliary_type=file_info["dv_deposit_type"],
                                                        dv_auxiliary_version=format_version,
                                                        dv_download_url=dv_download_url)

            # Reference: https://github.com/IQSS/dataverse/issues/8241#issuecomment-988812491
            #
            payload = dict(origin=settings.DP_CREATOR_APP_NAME,
                           isPublic=True,
                           type=file_info["dv_deposit_type"],
                           )

            # Assuming actual filepath for initial pass;
            #   For azure/s3 update: https://github.com/jschneier/django-storages/tree/master/storages/backends
            file_field = file_info["file_field"]
            if not file_field:
                # No file to deposit. Save AuxiliaryFileDepositRecord for
                #   logging and go to the next file
                #
                deposit_record.http_status_code = -99
                ftype = {file_info["dv_deposit_type"]}
                user_deposit_msg = f'A "{ftype}" file for this Release was not generated. Deposit not attempted.'
                deposit_record.dv_err_msg = user_deposit_msg
                self.set_deposit_record_user_messages_and_save(deposit_record)
                continue

            expected_num_deposits += 1

            # Dataverse includes an optional "filetype" parameter
            # b/c it doesn't detect JSON directly
            #  - The value for "file" is a tuple:
            #    - format:   ("filename_as_str.json",
            #                 ["file contents"],
            #                 "filetype_as_str")
            #
            #    - example: ('release_01.json",
            #                open(file_field.path, 'rb'),
            #                "application/json")
            #
            files = {'file': (basename(file_field.name),
                              open(file_field.path, 'rb'),
                              file_info['FILETYPE'])}

            try:
                response = requests.post(dv_deposit_url,
                                         headers=headers,
                                         data=payload,
                                         files=files)
            except requests.exceptions.ConnectionError as _ex_obj:
                # Connection error, log message
                deposit_record.http_status_code = -99
                user_msg = (f'Failed to connect to Dataverse at server:'
                            f' {self.dv_dataset.dv_installation.dataverse_url}.')
                deposit_record.dv_err_msg = user_msg
                self.set_deposit_record_user_messages_and_save(deposit_record)
                continue
            except Exception as _ex_obj:
                # Deposit failed, log message
                deposit_record.http_status_code = -99
                deposit_record.dv_err_msg = f'Error connecting to Dataverse.'
                self.set_deposit_record_user_messages_and_save(deposit_record)
                continue

            logger.info('Dataverse status_code: %s', response.status_code)

            if response.status_code == status.HTTP_200_OK:
                logger.info('Dataverse response json: %s', response.json())

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
                num_deposits += 1
            elif response.status_code == status.HTTP_403_FORBIDDEN:
                # Forbidden
                user_msg = (f'The deposit failed. Dataverse returned a "Forbidden" error.'
                            f' (Dataverse url: {self.dv_dataset.dv_installation.dataverse_url}).')
                deposit_record.dv_err_msg = user_msg
                logger.error(user_msg)
            else:
                # Deposit failed
                try:
                    # Check for a DV deposit error message:
                    # {"status":"ERROR","message":"File not found based on id 29."}
                    #
                    deposit_record.http_resp_json = response.json()
                    if 'status' in deposit_record.http_resp_json and \
                            deposit_record.http_resp_json['status'] == 'ERROR' and \
                            'message' in deposit_record.http_resp_json:
                        deposit_record.dv_err_msg = deposit_record.http_resp_json['message']
                    # self.add_err_msg(dv_static.ERR_MSG_JSON_DEPOSIT_FAILED)
                except Exception as _ex_obj:
                    # could not convert response to JSON
                    deposit_record.dv_err_msg = (f'Could not convert response to JSON.'
                                                 f' Status code: {response.status_code}')
                    logger.error(deposit_record.dv_err_msg)

            self.set_deposit_record_user_messages_and_save(deposit_record)

    def set_deposit_record_user_messages_and_save(self, deposit_record: AuxiliaryFileDepositRecord):
        """
        Given an AuxiliaryFileDepositRecord object, set the user messages
        :param deposit_record AuxiliaryFileDepositRecord
        """
        deposit_record.user_msg_text = render_to_string('dataverses/auxiliary_deposit.txt',
                                                        {'deposit': deposit_record})

        deposit_record.user_msg_html = render_to_string('dataverses/auxiliary_deposit.html',
                                                        {'deposit': deposit_record})

        # Saving sets the "deposit_success" field
        #
        deposit_record.save()

    def update_release_info(self):
        """
        On the ReleaseInfo object, update the "dataverse_deposit_info" field
        """
        if self.has_error():
            return

        # Get the latest JSON record--assumes there are no records earlier than a success record!
        #
        json_rec = AuxiliaryFileDepositRecord.objects.filter(
            release_info=self.release_info,
            dv_auxiliary_type=dv_static.DV_DEPOSIT_TYPE_DP_JSON,
        ).order_by('-created').first()

        if json_rec:
            json_rec_dict = json_rec.as_dict()
            self.release_info.dv_json_deposit_complete = json_rec.deposit_success
        else:
            self.release_info.dv_json_deposit_complete = False
            no_rec_err_msg = 'JSON file not found for deposit. (status:-97)'
            json_rec_dict = dict(deposit_success=False,
                                 user_msg_text=no_rec_err_msg,
                                 user_msg_html=no_rec_err_msg)
            logger.error(no_rec_err_msg)

        # Get the latest PDF record--assumes there are no records earlier than a success record!
        #
        pdf_rec = AuxiliaryFileDepositRecord.objects.filter(
            release_info=self.release_info,
            dv_auxiliary_type=dv_static.DV_DEPOSIT_TYPE_DP_PDF,
        ).order_by('-created').first()
        if pdf_rec:
            pdf_rec_dict = pdf_rec.as_dict()
            self.release_info.dv_pdf_deposit_complete = pdf_rec.deposit_success
        else:
            self.release_info.dv_pdf_deposit_complete = False
            no_rec_err_msg = 'PDF file not found for deposit. (status:-98)'
            pdf_rec_dict = dict(deposit_success=False,
                                user_msg_text=no_rec_err_msg,
                                user_msg_html=no_rec_err_msg)
            logger.error(no_rec_err_msg)

        deposit_info_dict = OrderedDict({
            'json_deposit_record': json_rec_dict,
            'pdf_deposit_record': pdf_rec_dict,
        })

        self.release_info.dataverse_deposit_info = deposit_info_dict

        self.release_info.save()


"""

"""
