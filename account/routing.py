from django.urls import re_path, path

from .consumers import *

websocket_urlpatterns = [
    #re_path(r"ws/mikro_status/", StatusConsumer.as_asgi()),
    re_path(r"ws/payment_add/(?P<user_id>\w+)/$", PaymentAddConsumer.as_asgi()),
    #path("ws/chat/<str:room_name>", ChatConsumer.as_asgi()),
]