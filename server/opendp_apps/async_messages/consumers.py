# chat/consumers.py
import json
import logging
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings

from opendp_apps.async_messages import static_vals as mstatic

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class ChatConsumer(WebsocketConsumer):

    @staticmethod
    def get_group_name(ws_identifier):
        """Method for """
        return f"{ws_identifier}-{datetime.now().strftime('%Y-%m-%d')}"

    def connect(self):
        self.ws_identifier = self.scope['url_route']['kwargs']['ws_identifier']
        self.room_group_name = ChatConsumer.get_group_name(self.ws_identifier)
        logger.info(f'connect: {self.room_group_name}')
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        logger.info(f'disconnect: {self.room_group_name}')
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': mstatic.MESSAGE_TYPE,
                'message': dict(user_message=message)
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
