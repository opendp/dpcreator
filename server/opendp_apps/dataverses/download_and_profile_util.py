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

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.serializers.json import DjangoJSONEncoder

from opendp_apps.async_messages import static_vals as async_static
from opendp_apps.async_messages.websocket_message import WebsocketMessage
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.dataverses.dataverse_download_handler import DataverseDownloadHandler
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.profiler.tasks import run_profile_by_filefield


class DownloadAndProfileUtil(BasicErrCheck):

    def __init__(self, dataset_object_id, websocket_id=None, **kwargs):
        """Begin with a DataSetInfo.object_id and go from there"""
        self.dataset_object_id = dataset_object_id
        self.websocket_id = websocket_id

        # To gather
        self.dataset_info = None  # DataSetInfo object
        self.data_profile = None  # Profiler output; saved to DataSetInfo object
        self.profile_variables = None  # Formatted profiler output; saved to DataSetInfo object

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

        ws_msg = WebsocketMessage.get_fail_message(
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

        ws_msg = WebsocketMessage.get_success_message(
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
        except DjangoValidationError as ex_obj:
            user_msg = f'Invalid DataSetInfo object id. ({self.dataset_object_id}) ({ex_obj})'
            self.add_err_msg(user_msg)
            self.send_websocket_profiler_err_msg(user_msg)
            return
        except ValueError as ex_obj:
            user_msg = f'Invalid DataSetInfo object id. (z) ({self.dataset_object_id}) ({ex_obj})'
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
        """
        1. Get the DataSetInfo object by id
        2. Read the associated filefield
        3. Parse it into a dataframe
        4. Run the variable profiler on the dataframe
        5. Send results back via websocket
        """
        if self.has_error():
            return

        prunner = run_profile_by_filefield(self.dataset_info.object_id,
                                           max_num_features=settings.PROFILER_COLUMN_LIMIT)

        if prunner.has_error():
            user_msg = prunner.get_err_msg()
            self.add_err_msg(user_msg)
            self.send_websocket_profiler_err_msg(user_msg)
            return

        # self.data_profile = ph.get_data_profile()
        self.profile_variables = prunner.data_profile
        profile_str = json.dumps(self.profile_variables, cls=DjangoJSONEncoder, indent=4)

        self.send_websocket_success_msg('Profile complete!',
                                        profile_str=profile_str)

    def get_data_profile(self):
        assert (self.has_error() is False), "Check that .has_error() is False before accessing this method"
        return self.data_profile
