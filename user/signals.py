from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from hr.models import TheCompany
from user.models import Profile, Notification


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates the profile after user created.
    @param sender:
    @param instance:
    @param created:
    @param kwargs:
    """
    if created:
        Profile.objects.create(user=instance)
        if instance.is_superuser:
            TheCompany.objects.get_or_create(id=1)
    else:
        pass

@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'public_room',
            {
                "type": "send_notification",
                "message": instance.message
            }
        )