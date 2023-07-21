import json
import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from opendp_apps.async_messages import static_vals as async_static
from opendp_apps.async_messages.tasks import profile_dataset_info, send_test_msg
from opendp_apps.async_messages.utils import get_websocket_id
from opendp_apps.async_messages.websocket_message import WebsocketMessage
from opendp_apps.dataset.models import DatasetInfo

logger = logging.getLogger(settings.DEFAULT_LOGGER)


@user_passes_test(lambda u: u.is_superuser)
def view_profile_test(request):
    """Page to test profiler by clicking on it"""
    websocket_id = get_websocket_id(request)

    ds_info_objects = DatasetInfo.objects.all()

    info = dict(websocket_id=websocket_id,
                ds_info_objects=ds_info_objects,
                VUE_APP_WEBSOCKET_PREFIX=settings.VUE_APP_WEBSOCKET_PREFIX)

    return render(request, 'async_messages/view_profile_test.html', info)


@csrf_exempt
def ajax_profile_by_dataset_object_id(request):
    """Profile DatasetInfo based on ajax input from 'view_profile_test'
    In a POST, send 'dataset_object_id'
    """
    json_data = json.loads(request.body)
    logger.info(f'ajax_profile_by_dataset_object_id: json_data = {json_data}')

    websocket_id = get_websocket_id(request)
    logger.info(f'ajax_profile_by_dataset_object_id: websocket_id = {websocket_id}')

    if not 'dataset_object_id' in json_data:
        logger.info(f'ajax_profile_by_dataset_object_id: dataset_object_id not in json_data: {json_data}')
        ws_msg = WebsocketMessage.get_fail_message(
            async_static.WS_MSG_TYPE_PROFILER,
            f'({datetime.now()}) The dataset has been materialized {datetime.now()}')
    else:
        logger.info(f'ajax_profile_by_dataset_object_id: Success with json_data: {json_data}')
        ws_msg = WebsocketMessage.get_success_message(
            async_static.WS_MSG_TYPE_PROFILER,
            f'({datetime.now()}) Looking good, ready for the next step')

    ws_msg.send_message(websocket_id)
    # send_test_msg.delay(websocket_id)
    logger.info("ajax_profile_by_dataset_object_id: json_data['dataset_object_id'] = %s",
                json_data['dataset_object_id'])
    profile_dataset_info.delay(json_data['dataset_object_id'], websocket_id=websocket_id)

    return JsonResponse(dict(success=True, message='should be sending a websocket message...'))


@user_passes_test(lambda u: u.is_superuser)
def index(request):
    return render(request, 'async_messages/index.html')


@user_passes_test(lambda u: u.is_superuser)
def view_room(request):
    room_name = 'download-profile'
    info = dict(room_name=f'{room_name}',
                ws_name=f'{request.user.object_id}')
    return render(request, 'async_messages/room.html', info)


@user_passes_test(lambda u: u.is_superuser)
def view_push_test(request):
    """Try to send a message"""
    websocket_id = request.user.object_id
    info = dict(websocket_id=websocket_id)

    send_test_msg.delay(websocket_id)

    ws_msg = WebsocketMessage.get_success_message( \
        'TYPE_OF_MESSAGE',
        f'The dataset has been materialized {datetime.now()}',
        data=dict(dog=1))

    ws_msg.send_message(websocket_id)

    return render(request, 'async_messages/push.html', info)
