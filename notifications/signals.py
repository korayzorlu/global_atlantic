from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import F 
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from django.core.signals import request_finished

from .models import Notify
from data.models import Part

@receiver(post_save, sender=Notify)
def notify_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            'public_room',
            {
                "type": "send_notification",
                "message": instance.message
            }
        )
        

@receiver(post_delete, sender=Notify)
def notify_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "send_notification",
            "message": "deleted"
        }
    )