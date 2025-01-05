from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from chat.consumers import ChatConsumer, NotificationConsumer
from Bikes.consumers import GPSConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<trip_id>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/hardware/(?P<serial_number>\w+)/gps/$', GPSConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
