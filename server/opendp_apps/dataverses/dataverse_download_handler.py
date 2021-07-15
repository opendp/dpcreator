"""
Convenience class for handling Dataverse file transfers
"""
from os.path import basename
import pathlib
import requests
from tempfile import TemporaryFile
from urllib.parse import urlsplit

from django.conf import settings
from django.core.files import File

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses import static_vals as dv_static


class DataverseDownloadHandler(BasicErrCheck):

    ERR_FAILED_TO_READ_DATASET = 'Failed to read the dataset.'
    ERR_DATASET_POINTER_NOT_SET = 'In order to profile the data, the "dataset_pointer" must be set.'

    def __init__(self, dv_file_info: DataverseFileInfo, **kwargs):
        """
        Download the Dataverse file
        """
        self.dv_file_info = dv_file_info
        self.content_url = None
        self.new_file_name = None

        self.run_download_process()


    def get_source_file(self):
        """Return the "source_file" field connected to DataverseFileInfo"""
        assert(self.has_error() is True), 'Please check "has_error()" before calling this method.'

        return self.dv_file_info.source_file


    def run_download_process(self):
        """Run the download process!"""
        if self.has_error():    # currently does nothing, but if code added prior to this
            return

        if not self.run_basic_checks_setup():
            return

        # Does the source file already exist?
        #
        if self.dv_file_info.source_file:
            # Yes! All Done!
            return

        # Download to a TemporaryFile
        with TemporaryFile() as tf:
            r = requests.get(self.content_url, stream=True)
            for chunk in r.iter_content(chunk_size=4096):
                tf.write(chunk)

            # Rewind to beginning of the TemporaryFile
            tf.seek(0)

            # Save the file to the DataverseFileInfo object
            # note: self.new_file_name determined in "run_basic_checks_setup()"
            django_file_obj = File(tf)
            self.dv_file_info.source_file.save(self.new_file_name, django_file_obj)



    def run_basic_checks_setup(self):
        """Run basic pre-download checks and create a new file name"""
        if self.has_error():
            return False

        # --------------------------------------
        # Is there a "dv_file_info"?
        # --------------------------------------
        if not self.dv_file_info:
            self.add_err_msg('The DataverseFileInfo was not found. (code: dv_download_010)')
            return False

        # --------------------------------------
        # Does it have a "file_schema_info"?
        # --------------------------------------
        if not self.dv_file_info.file_schema_info:
            self.add_err_msg(('The File Schema Info was not found for'
                              ' this dataset. (code: dv_download_020)'))
            return False

        # --------------------------------------
        # Does the "file_schema_info" have a contentURL?
        # --------------------------------------
        if not dv_static.SCHEMA_KEY_CONTENTURL in self.dv_file_info.file_schema_info:
            self.add_err_msg((f'The file schema info does not contain a'
                             f' {dv_static.SCHEMA_KEY_CONTENTURL} parameter. (code: dv_download_040)'))
            return False

        # --------------------------------------
        # Set the content_url (used for download)
        # --------------------------------------
        self.content_url = self.dv_file_info.file_schema_info[dv_static.SCHEMA_KEY_CONTENTURL]
        if self.content_url:
            self.content_url = self.content_url.strip()

        if not self.content_url:
            self.add_err_msg((f'The file schema info does not contain well-formed'
                              f' {dv_static.SCHEMA_KEY_CONTENTURL}. (code: dv_download_050)'))
            return False

        # --------------------------------------
        # Set the file name
        # --------------------------------------

        # Is there a file name in the file_schema_info?
        #
        if dv_static.SCHEMA_KEY_NAME in self.dv_file_info.file_schema_info:
            self.new_file_name = self.dv_file_info.file_schema_info[dv_static.SCHEMA_KEY_NAME]

        # Nope, use the ending of the content_url -- usually the fileId
        #
        if not self.new_file_name:
            self.new_file_name = basename(urlsplit(self.content_url).path)

        # Does the filename have an extension?
        # DV download files should be .tab
        file_ext = pathlib.Path(self.new_file_name).suffix
        if file_ext == '':
            self.new_file_name = f'{self.new_file_name}.tab'

        return True