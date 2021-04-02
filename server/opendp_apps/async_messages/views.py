from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from opendp_apps.async_messages.consumers import ChatConsumer
from opendp_apps.async_messages import static_vals as mstatic

@login_required
def index(request):

    info = dict(ws_name=f'{request.user.object_id}')
    return render(request, 'async_messages/index.html')

@login_required
def room(request, room_name):

    info = dict(room_name=f'{room_name}',
                ws_name=f'{request.user.object_id}')
    return render(request, 'async_messages/room.html', info)


@login_required
def push_test(request):
    """Try to send a message"""
    websocket_id = request.user.object_id
    info = dict(websocket_id=websocket_id)

    from opendp_apps.async_messages.websocket_message import WebsocketMessage

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