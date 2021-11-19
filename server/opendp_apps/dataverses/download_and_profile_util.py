"""
Combine the functionality of these objects:
    - DataverseDownloadHandler (dataverses.dataverse_download_handler.DataverseDownloadHandler)
    - ProfileHandler (profiler.profile_handler.ProfileHandler)

Basic workflow:
    - input:
        - DatasetFileInfo
        - websocket_id (optional)
    - output:
        - If successful, updates the DatasetFileInfo.data_profile
        - If an error, has an error message available
"""
import json

from django.core.serializers.json import DjangoJSONEncoder

from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.async_messages.websocket_message import WebsocketMessage
from opendp_apps.async_messages import static_vals as async_static

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.dataset.models import DataSetInfo

from opendp_apps.dataverses.dataverse_download_handler import DataverseDownloadHandler
from opendp_apps.profiler.csv_reader import CsvReader
from opendp_apps.profiler.dataset_info_updater import DataSetInfoUpdater
from opendp_apps.profiler.profile_runner import run_profile


class DownloadAndProfileUtil(BasicErrCheck):

    def __init__(self, dataset_object_id, websocket_id=None, **kwargs):
        """Begin with a DataSetInfo.object_id and go from there"""
        self.dataset_object_id = dataset_object_id
        self.websocket_id = websocket_id

        # To gather
        self.dataset_info = None    # DataSetInfo object
        self.data_profile = None    # Profiler output; saved to DataSetInfo object
        self.profile_variables = None   # Formatted profiler output; saved to DataSetInfo object

        # Run
        self.run_process()

    def get_profile_variables(self):
        """Re-retrieve the DataSetInfo object which should have the profile_variables"""
        assert self.has_error() is False, "Check that .is_valid() is True before calling this method"
        try:
            dsi = DataSetInfo.objects.get(object_id=self.dataset_object_id)
        except DataSetInfo.DoesNotExist:
            return None

        return dsi.get_profile_variables()

    def send_websocket_profiler_err_msg(self, user_msg):
        """Send a websocket error message of type WS_MSG_TYPE_PROFILER"""
        if not self.websocket_id:
            return

        ws_msg = WebsocketMessage.get_fail_message( \
            async_static.WS_MSG_TYPE_PROFILER,
            user_msg)
        ws_msg.send_message(self.websocket_id)

    def send_websocket_success_msg(self, user_msg, profile_str=None):
        """Send a websocket success message of type WS_MSG_TYPE_PROFILER"""
        if not self.websocket_id:
            return

        if profile_str:
            data_dict = dict(profile_str=profile_str)
        else:
            data_dict = None

        ws_msg = WebsocketMessage.get_success_message( \
            async_static.WS_MSG_TYPE_PROFILER,
            user_msg,
            data=data_dict)

        ws_msg.send_message(self.websocket_id)

    def run_process(self):
        """Run the download/profile process"""
        if self.has_error():
            return

        try:
            self.dataset_info = DataSetInfo.objects.get(object_id=self.dataset_object_id)
        except DataSetInfo.DoesNotExist:
            user_msg = f'The DataSetInfo object was not found. {self.dataset_object_id}'
            self.add_err_msg(user_msg)
            self.send_websocket_profiler_err_msg(user_msg)
            return

        # Download file (in the case of Dataverse)
        #
        if not self.check_for_or_download_source_file():
            return

        # Profile file
        #
        self.send_websocket_success_msg('Start dataset profile...')
        self.profile_file()

    def check_for_or_download_source_file(self):
        """
        Is the "source_file" available? If not and it's a Dataverse dataset, try to download it
        """
        if self.has_error():
            return

        # ------------------------------------------------
        # Is the file already there?
        # ------------------------------------------------
        if self.dataset_info.source_file:  # File exists!
            return True

        # No file there....

        # ------------------------------------------------
        # If it's not a Dataverse file, then error ...
        # ------------------------------------------------
        if self.dataset_info.source != DataSetInfo.SourceChoices.Dataverse:
            user_msg = (f'The DataSetInfo source file is not available. (object_id: {self.dataset_object_id}, '
                        f'type: {self.dataset_info.source})')
            self.add_err_msg(user_msg)
            self.send_websocket_profiler_err_msg(user_msg)
            return False

        # ------------------------------------------------
        # It's a Dataverse file, try to download it
        # ------------------------------------------------
        self.send_websocket_success_msg('Copying the Dataverse file to DP Creator.')

        dhandler = DataverseDownloadHandler(self.dataset_info)
        if dhandler.has_error():
            user_msg = dhandler.get_err_msg()
            self.add_err_msg(user_msg)
            self.send_websocket_profiler_err_msg(user_msg)
            return False

        self.send_websocket_success_msg('The Dataverse file has been copied.')
        return True

    def profile_file(self):
        """"Profile the file"""
        try:
            ds_info = DataSetInfo.objects.get(object_id=self.dataset_object_id)
            filefield = ds_info.source_file
        except DataSetInfo.DoesNotExist:
            filefield = None
        try:
            df = CsvReader(filefield.path).read()
        except Exception as ex:
            print("EXCEPTION in profile_file: ", str(ex))
            self.add_err_msg(str(ex))
            self.send_websocket_profiler_err_msg(str(ex))
            if self.dataset_object_id:
                dataset_info = DataSetInfo.objects.get(object_id=self.dataset_object_id)
                dataset_info_updater = DataSetInfoUpdater(dataset_info)
                dataset_info_updater.update_step(DepositorSetupInfo.DepositorSteps.STEP_9300_PROFILING_FAILED)
            return
        ph = run_profile(df, self.dataset_object_id)

        #self.data_profile = ph.get_data_profile()
        self.profile_variables = ph.data_profile
        profile_str = json.dumps(self.profile_variables, cls=DjangoJSONEncoder, indent=4)

        self.send_websocket_success_msg('Profile complete!',
                                        profile_str=profile_str)
                                        # profile_str=self.get_data_profile())

    def get_data_profile(self):
        assert(self.has_error() is False), \
            "Check that .has_error() is False before accessing this method"


        return self.data_profile


    #def get_data_profile_as_json_str(self):
    #    assert (self.has_error() is False), \
    #        "Check that .has_error() is False before accessing this method"
    #
    #    profile_str = json.dumps(self.get_data_profile(), cls=DjangoJSONEncoder, indent=4)
    #
    #    return profile_str