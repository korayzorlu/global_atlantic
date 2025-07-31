from rest_framework import generics

from notifications.models import Notification
from notifications.api.serializers import NotificationUpdateSerializer

class NotificationUpdateAPI(generics.UpdateAPIView):
    """
    Update Notification
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationUpdateSerializer
