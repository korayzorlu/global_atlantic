from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import F 
from django.db import transaction

from django.core.signals import request_finished
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import InquiryItem, ProjectItem, Inquiry, Project
from card.models import Currency


from .tasks import *

import inspect

import sys

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


@receiver(pre_save, sender=InquiryItem)
def update_total_price_or_unit_price_inquiry(sender, instance, **kwargs):
    if sender.objects.select_related("inquiry__currency").filter(id=instance.id).exists():

        senderInquiryItem = sender.objects.select_related("inquiry__currency").filter(id=instance.id).first()
        
        inquiryCurrency = senderInquiryItem.inquiry.currency
            
        if getattr(senderInquiryItem, "quantity") != getattr(instance, "quantity"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
                
            instance.totalPrice = float(instance.unitPrice) * float(instance.quantity)
            
        if getattr(senderInquiryItem, "unitPrice") != getattr(instance, "unitPrice"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
                
            instance.totalPrice = float(instance.unitPrice) * float(instance.quantity)
            
        if getattr(senderInquiryItem, "totalPrice") != getattr(instance, "totalPrice"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
                instance.totalPrice = 0
                instance.unitPrice = float(instance.totalPrice) / float(instance.quantity)
                
        inquiry = instance.inquiry
        inquiryItems = inquiry.inquiryitem_set.select_related().filter(inquiry = instance.inquiry).exclude(id=instance.id)
        itemsTotalTotalPrice = 0
        for inquiryItem in inquiryItems:
            itemsTotalTotalPrice = itemsTotalTotalPrice + (inquiryItem.unitPrice * inquiryItem.quantity)
        inquiry.totalTotalPrice = round(itemsTotalTotalPrice + (instance.unitPrice * instance.quantity),2)
        inquiry.save()
        
        # Para miktarını belirtilen formatta gösterme
        totalTotalPriceFixed = "{:,.2f}".format(round(inquiry.totalTotalPrice,2))
        # Nokta ile virgülü değiştirme
        totalTotalPriceFixed = totalTotalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        totalPrices = {"inquiry":inquiry.id,
                        "totalTotalPrice":totalTotalPriceFixed,
                        "currency":inquiry.currency.symbol}
        
        updateDetail(totalPrices,"purchasing_inquiry_update")         
  