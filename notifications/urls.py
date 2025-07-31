from django.urls import path,include

from notifications.views import *

app_name="notifications"

urlpatterns = [
     path('api/', include("notifications.api.urls")),
     path('<int:notification_id>', NotificationsDataView.as_view(), name="notification_project"),
     
     path('message_update_success/', MessageUpdateSuccessDataView.as_view(), name="message_update_success"),
     path('message_update_error/', MessageUpdateErrorDataView.as_view(), name="message_update_error"),
]