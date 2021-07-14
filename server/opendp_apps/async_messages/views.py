from datetime import datetime
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from rest_framework import status

from opendp_apps.async_messages.consumers import ChatConsumer
from opendp_apps.async_messages import static_vals as mstatic
from opendp_apps.dataset.models import DataSetInfo


from opendp_apps.async_messages import static_vals as async_static
from opendp_apps.async_messages.utils import get_websocket_id
from opendp_apps.async_messages.websocket_message import WebsocketMessage
from opendp_apps.async_messages.tasks import send_test_msg


@user_passes_test(lambda u: u.is_superuser)
def view_profile_test(request):
    """Page to test profiler by clicking on it"""
    websocket_id = get_websocket_id(request)

    ds_info_objects = DataSetInfo.objects.all()

    info = dict(websocket_id=websocket_id,
                ds_info_objects=ds_info_objects,
                WEBSOCKET_PREFIX=settings.WEBSOCKET_PREFIX)

    return render(request, 'async_messages/view_profile_test.html', info)

@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def ajax_profile_by_dataset_object_id(request):
    """Profile DataSetInfo based on ajax input from 'view_profile_test'
    In a POST, send 'dataset_object_id'
    """
    json_data = json.loads(request.body)
    print('json_data->>', json_data)

    if not request.user.is_superuser:
        return JsonResponse(dict(success=False, message='nope'),
                            status=status.HTTP_403_FORBIDDEN)

    websocket_id = get_websocket_id(request)

    if not 'dataset_object_id' in json_data:
        ws_msg = WebsocketMessage.get_fail_message(
            async_static.WS_MSG_TYPE_PROFILE,
            f'({datetime.now()}) The dataset has been materialized {datetime.now()}')
    else:
        ws_msg = WebsocketMessage.get_success_message(
            async_static.WS_MSG_TYPE_PROFILE,
            f'({datetime.now()}) Looking good, ready for the next step')

    ws_msg.send_message(websocket_id)
    send_test_msg.delay(websocket_id)


    return JsonResponse(dict(success=True, message='should be sending a websocket message...'))


@user_passes_test(lambda u: u.is_superuser)
def index(request):

    info = dict(ws_name=f'{request.user.object_id}')
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
    #send_test_msg(websocket_id)

    ws_msg = WebsocketMessage.get_success_message( \
        'TYPE_OF_MESSAGE',
        f'The dataset has been materialized {datetime.now()}',
        data=dict(dog=1))

    ws_msg.send_message(websocket_id)

    return render(request, 'async_messages/push.html', info)

"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_ws_message(websocket_id, text_data='hello'):
    channel_layer = get_channel_layer()

    group_name = ChatConsumer.get_group_name(websocket_id)
    print('group_name', group_name)
    async_to_sync(channel_layer.group_send)( \
        group_name,
        {
            'type': mstatic.MESSAGE_TYPE,
            'message': text_data
        })
"""