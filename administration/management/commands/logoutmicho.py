from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.sessions.models import Session

from django.core.management.base import BaseCommand, CommandError

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def reloadMicho(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "reload_micho",
            "message": message
        }
    )

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None
        
    def add_arguments(self, parser):
        parser.add_argument('user', type=int, help='User Id')


    def handle(self, *args, **kwargs):
        userId = kwargs['user']

        user = User.objects.select_related().filter(id = userId).first()

        if user:
            sessions = Session.objects.filter(session_data__contains=user.id)

            # Oturumları sonlandır
            for session in sessions:
                session.delete()
        elif userId == 0:
            users = User.objects.select_related().filter()

            for user in users:
                sessions = Session.objects.filter(session_data__contains=user.id)

                # Oturumları sonlandır
                for session in sessions:
                    session.delete()
        
