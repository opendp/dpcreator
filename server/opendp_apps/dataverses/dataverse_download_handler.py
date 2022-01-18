"""
Convenience class for handling Dataverse file transfers
"""
from os.path import basename
import pathlib
import requests
from tempfile import TemporaryFile
from urllib.parse import urlsplit

from django.core.files import File

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataverses import static_vals as dv_static


class DataverseDownloadHandler(BasicErrCheck):
    """Using DataverseFileInfo, download the Dataverse file"""

    def __init__(self, dv_file_info: DataverseFileInfo):
        """Download the Dataverse file"""
        self.dv_file_info = dv_file_info
        self.content_url = None
        self.new_file_name = None
        self.dv_user = None

        self.run_download_process()

    def get_source_file(self):
        """Return the "source_file" field connected to DataverseFileInfo"""
        assert (self.has_error() is True), 'Please check "has_error()" before calling this method.'

        return self.dv_file_info.source_file

    def set_depositor_info_status(self, new_step: DepositorSetupInfo.DepositorSteps) -> bool:
        """Update the status on the DepositorSetupInfo object.
        Only available if the dv_file_info is populated"""
        if not self.dv_file_info:
            return False

        # Update the step
        self.dv_file_info.depositor_setup_info.set_user_step(new_step)

        # save it
        self.dv_file_info.depositor_setup_info.save()

        return True

    def add_err_msg(self, err_msg):
        """Add an error message and update the DepositorSetupInfo status"""
        super().add_err_msg(err_msg)
        self.set_depositor_info_status(DepositorSetupInfo.DepositorSteps.STEP_9200_DATAVERSE_DOWNLOAD_FAILED)

    def run_download_process(self):
        """Run the download process!"""
        if self.has_error():  # currently does nothing, but if code added prior to this
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

            headers = {'X-Dataverse-key': self.dv_user.dv_general_token}

            r = requests.get(self.content_url, headers=headers, stream=True)
            if r.status_code != 200:
                user_msg = (f'Dataset download attempt failed with'
                            f' HTTP status code "{r.status_code}"')
                self.add_err_msg(user_msg)
                return

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
        if dv_static.SCHEMA_KEY_CONTENTURL not in self.dv_file_info.file_schema_info:
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
        # Is an access token available for download?
        # --------------------------------------
        if not self.dv_file_info.creator:
            self.add_err_msg((f'The DataverseFileInfo does not have a "creator" attribute.'
                              f' (code: dv_download_060)'))
            return False

        self.dv_user = self.dv_file_info.get_dataverse_user()
        if self.dv_user is None:
            self.add_err_msg((f'The DataverseUser is not available.'
                              f' (code: dv_download_070)'))
            return False

        if not self.dv_user.dv_general_token:
            self.add_err_msg((f'The DataverseUser ({self.dv_user.id}) does not have access permissions.'
                              f' (code: dv_download_080)'))
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


'''
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses.dataverse_download_handler import DataverseDownloadHandler

dfi = DataverseFileInfo.objects.get(pk=3)
dhandler = DataverseDownloadHandler(dfi)
'''
