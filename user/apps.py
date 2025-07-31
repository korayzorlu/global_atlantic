from django.apps import AppConfig
from django.db import ProgrammingError


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    def ready(self):
        import user.signals
        try:
            from . import updater
            #updater.start()
        except ProgrammingError as e:
            print(str(e).strip())
            print("If you are using makemigrations or migrate, don't pay attention to this ^\n")
