"""
ASGI config for opendp_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendp_project.settings.azure_test_01')
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter

from opendp_apps.async_messages import routing as async_routing

application = ProtocolTypeRouter({
    "http": AsgiHandler(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            async_routing.websocket_urlpatterns  # ws://async_messages/ws
        )
    ),
})
