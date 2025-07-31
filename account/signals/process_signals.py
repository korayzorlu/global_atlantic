from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.core.signals import request_finished

from ..models import *
from ..utils.payment_utils import *
from ..utils.current_utils import *
from ..utils.process_utils import *
from card.models import Current

import inspect
import logging

def sendAlert(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "send_alert",
            "message": message,
            "location" : location
        }
    )

def reloadTable(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "reload_table",
            "message": message,
            "location" : location
        }
    )

def updateDetail(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "update_detail",
            "message": message,
            "location" : location
        }
    )


          
             

@receiver(post_save, sender=Process)
def pocess_add(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():
            if created:
                pass
    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")



        
        