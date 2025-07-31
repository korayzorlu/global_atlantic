from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from hr.models import TheCompany
from beta_profile.models import Profile


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
