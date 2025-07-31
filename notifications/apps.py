from django.apps import AppConfig
from django.db import ProgrammingError


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    
    def ready(self):
        import notifications.signals