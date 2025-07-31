from django.urls import re_path
from .consumers import *

websocket_urlpatterns = [
    re_path(r"ws/socket/(?P<user>\w+)/$", MainConsumer.as_asgi()),
    #re_path(r"ws/notify/", NotificationConsumer.as_asgi()),
    re_path(r"ws/bar/(?P<room_name>\w+)/(?P<temperature>\w+)/$",ProgressBarConsumer.as_asgi(),),
    re_path(r"ws/alert/(?P<user_id>\w+)/$", AlertConsumer.as_asgi()),
]