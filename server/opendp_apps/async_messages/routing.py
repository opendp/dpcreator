# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/profile/(?P<ws_identifier>(\w|-)+)/$', consumers.ChatConsumer.as_asgi()),
]
