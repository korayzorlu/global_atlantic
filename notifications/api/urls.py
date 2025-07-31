from django.urls import path

from notifications.api.views import *

urlpatterns = [
        path('<int:pk>/update', NotificationUpdateAPI.as_view(), name="notification_update_api"),
]