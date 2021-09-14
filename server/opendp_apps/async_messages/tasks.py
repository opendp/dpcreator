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
from opendp_apps.dataverses.dataverse_download_handler import DataverseDownloadHandler
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.model_helpers.basic_response import BasicResponse, ok_resp, err_resp
from opendp_apps.dataverses.download_and_profile_util import DownloadAndProfileUtil

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
def profile_dataset_info(dataset_object_id: DataSetInfo.object_id, websocket_id=None) -> BasicResponse:
    """
    Using the DataSetInfo object_id, download and profile a dataset.
    If the "websocket_id" is defined, send back websocket messages

    Assumes: if websocket_id is None, then assume this is being called w/o celery
        and can return complex objects such as the DownloadAndProfileUtil.

        If websocket_id is defined, this function returns a dict:
         {'success': True/False, 'message': "A user message"}
    """
    dp_util = DownloadAndProfileUtil(dataset_object_id, websocket_id)
    if dp_util.has_error():
        if websocket_id:
            return dict(success=False, messsage=dp_util.get_err_msg())
        return err_resp(dp_util.get_err_msg())  # direct error `message`

    if websocket_id:
        return dict(success=True, messsage='Profile in process')

    return ok_resp(dp_util)

@celery_app.task
def send_test_msg(websocket_id):
    filepath = join(TEST_DATA_DIR, 'fearonLaitin.csv')
    # dsi = DataSetInfo.objects.first()

    # with Celery:
    # profiler = ProfileHandler.run_profile_by_filepath.delay(filepath, dsi.object_id)

    profiler = profiler_tasks.run_profile_by_filepath(filepath)  # , dsi.object_id)
    if profiler.has_error():
        user_msg = f'error: {profiler.get_err_msg()}'
        print(user_msg)
        ws_msg = WebsocketMessage.get_fail_message( \
            async_static.WS_MSG_TYPE_PROFILER,
            user_msg)
    else:
        profile_str = json.dumps(profiler.data_profile, cls=DjangoJSONEncoder, indent=4)
        # print('-' * 40)
        # print(profile_str)
        ws_msg = WebsocketMessage.get_success_message( \
            async_static.WS_MSG_TYPE_PROFILER,
            f'Profile worked {datetime.now()}',
            data=dict(profile_str=profile_str))
        # print('profiled!')

    ws_msg.send_message(websocket_id)

    print('celery message sent...')

