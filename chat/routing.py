from django.urls import re_path
from .consumers import TextConsumer, NotificationConsumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>[\w_]+)/$', TextConsumer.as_asgi()),
    re_path(r'^ws/notifications/(?P<room_name>[\w_]+)/$', NotificationConsumer.as_asgi()),
]