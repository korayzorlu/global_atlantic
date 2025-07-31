from django.urls import re_path, path

from .consumers import *

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    #path("ws/chat/<str:room_name>", ChatConsumer.as_asgi()),
]