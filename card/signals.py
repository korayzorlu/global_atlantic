from django.db.models.signals import m2m_changed, pre_save, post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async

from card.models import Company

@receiver(pre_save, sender = Company)
def my_callback(sender, instance, *args, **kwargs):
    newObjId = instance.id

# @receiver(pre_save, sender=Company)
# def notify_created(sender, instance, *args, **kwargs):
#     if sender.objects.filter(id=instance.id).exists():

#         senderCompany = sender.objects.filter(id=instance.id).first()
        
#         channel_layer = get_channel_layer()
#         cariKod = senderCompany.hesapKodu
        
#         if getattr(senderCompany, "hesapKodu") != getattr(instance, "hesapKodu"):
        
#             async_to_sync(channel_layer.group_send)(
#                 "mikro_status",
#                 {
#                     "type": "check_connection_signal",
#                     "cariKod": instance.hesapKodu
#                 }
#             )
            
#         if getattr(senderCompany, "name") != getattr(instance, "name"):
        
#             async_to_sync(channel_layer.group_send)(
#                 "mikro_status",
#                 {
#                     "type": "change_company_name",
#                     "cariKod": instance.hesapKodu,
#                     "cariName": instance.name
#                 }
#             )