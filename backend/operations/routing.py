from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/messaging/(?P<user_id>\w+)/$', consumers.MessageConsumer.as_asgi()),
    re_path(r'ws/queue/(?P<department>\w+)/(?P<user_id>\w+)/$', consumers.QueueStatusConsumer.as_asgi()),
    re_path(r'ws/queue/(?P<department>\w+)/$', consumers.QueueStatusConsumer.as_asgi()),
]
