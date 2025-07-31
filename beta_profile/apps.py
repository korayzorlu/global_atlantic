from django.apps import AppConfig
from django.db import ProgrammingError


class BetaProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'beta_profile'

    def ready(self):
        import beta_profile.signals
        try:
            from . import updater
            #updater.start()
        except ProgrammingError as e:
            print(str(e).strip())
            print("If you are using makemigrations or migrate, don't pay attention to this ^\n")
