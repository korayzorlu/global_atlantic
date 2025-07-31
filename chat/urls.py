from django.urls import path, include

from . import views
from .views import *

app_name = "chat"

urlpatterns = [
    path('chat_data/', ChatDataView.as_view(), name="chat_data"),
    path('<str:room_name>/', RoomDataView.as_view(), name="room"),
]
