from datetime import datetime
from os.path import abspath, dirname, isdir, join

CURRENT_DIR = dirname(abspath(__file__))
SERVER_DIR = dirname(CURRENT_DIR)
TEST_DATA_DIR = join(dirname(SERVER_DIR), 'test_data')

import json
from django.core.serializers.json import DjangoJSONEncoder

from opendp_project.celery import celery_app

from opendp_apps.async_messages import static_vals as async_static
from opendp_apps.async_messages.websocket_message import WebsocketMessage
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.profiler.tasks import ProfileHandler
from opendp_apps.dataverses.dataverse_download_handler import DataverseDownloadHandler
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.utils.view_helper import get_json_err, get_json_success

def send_websocket_profiler_err_msg(user_msg, websocket_id):
    """Send a websocket error message of type WS_MSG_TYPE_PROFILER"""
    ws_msg = WebsocketMessage.get_fail_message( \
        async_static.WS_MSG_TYPE_PROFILER,
        user_msg)
    ws_msg.send_message(websocket_id)

def send_websocket_success_msg(user_msg, websocket_id, profile_str=None):

    if profile_str:
        data_dict = dict(profile_str=profile_str)
    else:
        data_dict = None

    ws_msg = WebsocketMessage.get_success_message( \
                async_static.WS_MSG_TYPE_PROFILER,
                user_msg,
                data=data_dict)

    ws_msg.send_message(websocket_id)


@celery_app.task
def profile_dataset_info(ds_info_object_id, websocket_id=None):
    """
    Using the DataSetInfo object_id, download and profile a dataset.
    If the "websocket_id" is defined, send back websocket messages
    - Used w/o a websocket, this function also returns a dict:
         {'success': True/False, 'message': "A user message"}
    """

    # (1) retrieve the DataSetInfo object
    try:
        dsi = DataSetInfo.objects.get(object_id=ds_info_object_id)
    except DataSetInfo.DoesNotExist:
        user_msg = f'The DataSetInfo object was not found. (object_id: {ds_info_object_id}'
        send_websocket_profiler_err_msg(user_msg)   # websocket error message
        return get_json_err(user_msg)               # direct error message


    # (2) Is the file downloaded?
    if not dsi.source_file:
        # If it's not a Dataverse file, then error ...
        if not dsi.source == DataSetInfo.SourceChoices.Dataverse:
            user_msg = f'The DataSetInfo source file is not available. (object_id: {ds_info_object_id}'
            send_websocket_profiler_err_msg(user_msg)   # websocket error message
            return get_json_err(user_msg)               # direct error message
        else:
            # It's a Dataverse file, retrieve it
            user_msg = 'Copying the Dataverse file to DP Creator.'
            send_websocket_success_msg(user_msg)

            download_handler = DataverseDownloadHandler(dsi)
            if download_handler.has_error():
                user_msg = download_handler.get_error_message()
                send_websocket_profiler_err_msg(user_msg)  # websocket error message
                return get_json_err(user_msg)  # direct error message

            # Send successful download message
            #
            user_msg = 'The Dataverse file has been copied.'
            send_websocket_success_msg(user_msg)
    else:
        # Already downloaded
        # Send successful message
        #
        user_msg = 'The Dataverse file had already been copied to DP Creator.'
        send_websocket_success_msg(user_msg)

    user_msg = 'File profile starting...'
    send_websocket_success_msg(user_msg)
    #profiler = ProfileHandler.run_profile_by_filepath.delay(filepath, dsi.object_id)


@celery_app.task
def send_test_msg(websocket_id):


    filepath = join(TEST_DATA_DIR, 'fearonLaitin.csv')
    #dsi = DataSetInfo.objects.first()

    # with Celery:
    # profiler = ProfileHandler.run_profile_by_filepath.delay(filepath, dsi.object_id)

    profiler = profiler_tasks.run_profile_by_filepath(filepath) #, dsi.object_id)
    if profiler.has_error():
        user_msg = f'error: {profiler.get_err_msg()}'
        print(user_msg)
        ws_msg = WebsocketMessage.get_fail_message( \
             async_static.WS_MSG_TYPE_PROFILER,
            user_msg)
    else:
        profile_str = json.dumps(profiler.data_profile, cls=DjangoJSONEncoder, indent=4)
        #print('-' * 40)
        #print(profile_str)
        ws_msg = WebsocketMessage.get_success_message( \
             async_static.WS_MSG_TYPE_PROFILER,
            f'Profile worked {datetime.now()}',
            data=dict(profile_str=profile_str))
        #print('profiled!')

    ws_msg.send_message(websocket_id)

    print('celery message sent...')
    
