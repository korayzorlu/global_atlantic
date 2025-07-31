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

@receiver(pre_save, sender=CommericalInvoiceItem)
def update_total_price_or_unit_price_commerical_invoice(sender, instance, **kwargs):
    if sender.objects.filter(id=instance.id).exists():

        senderCommericalInvoicePart = sender.objects.get(id=instance.id)
        commericalInvoice = senderCommericalInvoicePart.invoice

        if getattr(senderCommericalInvoicePart, "quantity") != getattr(instance, "quantity"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
            instance.totalPrice = (float(instance.unitPrice) * float(instance.quantity)) + float(instance.vatPrice)
            
        if getattr(senderCommericalInvoicePart, "unitPrice") != getattr(instance, "unitPrice"):
            instance.totalPrice = float(instance.unitPrice) * float(instance.quantity)
            
        if getattr(senderCommericalInvoicePart, "totalPrice") != getattr(instance, "totalPrice"):
            if float(instance.totalPrice) == 0:
                instance.unitPrice = 0
            else:
                instance.unitPrice = float(instance.totalPrice) / float(instance.quantity)
            
        parts = CommericalInvoiceItem.objects.filter(invoice = commericalInvoice)
        expenses = CommericalInvoiceExpense.objects.filter(invoice = commericalInvoice)
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
        
        partsTotal = 0
        
        for part in parts:
            partsTotal  = partsTotal + part.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
            
        if commericalInvoice.orderTracking:
            if commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscountAmount > 0:
                partsTotals["totalDiscount"] = commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscount/100)
        else:
            partsTotals["totalDiscount"] = 0
        
        
        for expense in expenses:
            partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
            
        partsTotals["totalExpense"] = partsTotals["totalExpense"] + (instance.totalPrice - senderCommericalInvoicePart.totalPrice)
        
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
        partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (commericalInvoice.vat/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
        
        commericalInvoice.vatPrice = round(partsTotals["totalVat"],2)
        commericalInvoice.netPrice = round(partsTotals["totalTotalPrice3"],2)
        commericalInvoice.totalPrice = round(partsTotals["totalFinal"],2)
        commericalInvoice.save()

  