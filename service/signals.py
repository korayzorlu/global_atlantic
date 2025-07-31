from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from django.core.signals import request_finished

from .models import OfferServiceCard, OfferExpense, OfferPart

import inspect

@receiver(pre_save, sender=OfferServiceCard)
def update_total_price_or_unit_price_offer(sender, instance, **kwargs):
    if sender.objects.filter(id=instance.id).exists():
        senderOfferServiceCard = sender.objects.get(id=instance.id)
        
        if getattr(senderOfferServiceCard, "quantity") != getattr(instance, "quantity"):
            if float(instance.quantity) == 0:
                instance.totalPrice = 0
            else:
                instance.totalPrice = round((float(instance.unitPrice3) + float(instance.taxPrice)) * float(instance.quantity), 2)
        
        elif getattr(senderOfferServiceCard, "unitPrice1") != getattr(instance, "unitPrice1"):
            if float(instance.unitPrice1) == 0:
                instance.profit = 0
                instance.unitPrice2 = 0
            instance.unitPrice2 = round(float(instance.unitPrice1) * float(1 + (float(instance.profit)/100)), 2)
            instance.unitPrice3 = round(float(instance.unitPrice2) * float(1 - (float(instance.discount)/100)), 2)
            instance.taxPrice = round(float(instance.unitPrice3) * float(float(instance.tax)/100), 2)
            instance.totalPrice = round((float(instance.unitPrice3) + float(instance.taxPrice)) * float(instance.quantity), 2)
        
        elif getattr(senderOfferServiceCard, "profit") != getattr(instance, "profit"):
            instance.unitPrice2 = round(float(instance.unitPrice1) * float(1 + (float(instance.profit)/100)), 2)
            instance.unitPrice3 = round(float(instance.unitPrice2) * float(1 - (float(instance.discount)/100)), 2)
            instance.taxPrice = round(float(instance.unitPrice3) * float(float(instance.tax)/100), 2)
            instance.totalPrice = round((float(instance.unitPrice3) + float(instance.taxPrice)) * float(instance.quantity), 2)
            
        elif getattr(senderOfferServiceCard, "discount") != getattr(instance, "discount"):
            instance.unitPrice3 = round(float(instance.unitPrice2) * float(1 - (float(instance.discount)/100)), 2)
            instance.taxPrice = round(float(instance.unitPrice3) * float(float(instance.tax)/100), 2)
            instance.totalPrice = round((float(instance.unitPrice3) + float(instance.taxPrice)) * float(instance.quantity), 2)
            
        elif getattr(senderOfferServiceCard, "tax") != getattr(instance, "tax"):
            instance.taxPrice = round(float(instance.unitPrice3) * float(float(instance.tax)/100), 2)
            instance.totalPrice = round((float(instance.unitPrice3) + float(instance.taxPrice)) * float(instance.quantity), 2)
            
@receiver(pre_save, sender=OfferExpense)
def update_total_price_or_unit_price_expense(sender, instance, **kwargs):
    if sender.objects.filter(id=instance.id).exists():
        senderOfferExpense = sender.objects.get(id=instance.id)
        
        if getattr(senderOfferExpense, "quantity") != getattr(instance, "quantity"):
            if float(instance.quantity) == 0:
                instance.totalPrice = 0
            else:
                instance.totalPrice = round(float(instance.unitPrice) * float(instance.quantity), 2)
        
        elif getattr(senderOfferExpense, "unitPrice") != getattr(instance, "unitPrice"):
            if float(instance.unitPrice) == 0:
                instance.totalPrice = 0
            instance.totalPrice = round(float(instance.unitPrice) * float(instance.quantity), 2)
            
@receiver(pre_save, sender=OfferPart)
def update_total_price_or_unit_price_part(sender, instance, **kwargs):
    if sender.objects.filter(id=instance.id).exists():
        senderOfferPart = sender.objects.get(id=instance.id)
        
        if getattr(senderOfferPart, "quantity") != getattr(instance, "quantity"):
            if float(instance.quantity) == 0:
                instance.totalPrice = 0
            else:
                instance.totalPrice = round(float(instance.unitPrice) * float(instance.quantity), 2)
        
        elif getattr(senderOfferPart, "unitPrice") != getattr(instance, "unitPrice"):
            if float(instance.unitPrice) == 0:
                instance.totalPrice = 0
            instance.totalPrice = round(float(instance.unitPrice) * float(instance.quantity), 2)