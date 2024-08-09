import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from .consumers import TextConsumer,NotificationConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feewock.settings')

# WebSocket URL patterns
websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>[\w_]+)/$', TextConsumer.as_asgi()),
    re_path(r'^ws/notifications/(?P<room_name>[\w_]+)/$', NotificationConsumer.as_asgi()),
    # Add more patterns if needed
]

# Application instance
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
