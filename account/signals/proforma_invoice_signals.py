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
from administration.models import ActionLog

from core.middleware import get_current_user

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




@receiver(pre_save, sender=ProformaInvoiceItem)
def update_total_price_or_unit_price_proforma_invoice(sender, instance, **kwargs):
    if sender.objects.filter(id=instance.id).exists():

        senderProformaInvoicePart = sender.objects.get(id=instance.id)
        proformaInvoice = senderProformaInvoicePart.invoice

        if getattr(senderProformaInvoicePart, "quantity") != getattr(instance, "quantity"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
            instance.totalPrice = (float(instance.unitPrice) * float(instance.quantity)) + float(instance.vatPrice)
            
        if getattr(senderProformaInvoicePart, "unitPrice") != getattr(instance, "unitPrice"):
            instance.totalPrice = float(instance.unitPrice) * float(instance.quantity)
            
        if getattr(senderProformaInvoicePart, "totalPrice") != getattr(instance, "totalPrice"):
            if float(instance.totalPrice) == 0:
                instance.unitPrice = 0
            else:
                instance.unitPrice = float(instance.totalPrice) / float(instance.quantity)
            
        parts = ProformaInvoiceItem.objects.filter(invoice = proformaInvoice)
        expenses = ProformaInvoiceExpense.objects.filter(invoice = proformaInvoice)
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
            
        if proformaInvoice.orderConfirmation:
            if proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount > 0:
                partsTotals["totalDiscount"] = proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (proformaInvoice.orderConfirmation.quotation.manuelDiscount/100)
        else:
            partsTotals["totalDiscount"] = 0
        
        
        for expense in expenses:
            partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
            
        partsTotals["totalExpense"] = partsTotals["totalExpense"] + (instance.totalPrice - senderProformaInvoicePart.totalPrice)
        
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
        partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (proformaInvoice.vat/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
        
        proformaInvoice.vatPrice = round(partsTotals["totalVat"],2)
        proformaInvoice.netPrice = round(partsTotals["totalTotalPrice3"],2)
        proformaInvoice.totalPrice = round(partsTotals["totalFinal"],2)
        proformaInvoice.save()

@receiver(pre_save, sender=ProformaInvoiceExpense)
def update_proforma_invoice_expense(sender, instance, **kwargs):
    if sender.objects.filter(id=instance.id).exists():

        senderExpense = sender.objects.filter(id=instance.id).first()
        proformaInvoice = senderExpense.invoice
        
        if getattr(senderExpense, "quantity") != getattr(instance, "quantity"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
            instance.totalPrice = float(instance.unitPrice) * float(instance.quantity)
            
        if getattr(senderExpense, "unitPrice") != getattr(instance, "unitPrice"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
            instance.totalPrice = float(instance.unitPrice) * float(instance.quantity)
            
        if getattr(senderExpense, "totalPrice") != getattr(instance, "totalPrice"):
            if float(instance.quantity) == 0:
                instance.unitPrice = 0
                instance.totalPrice = 0
            else:
                instance.unitPrice = float(instance.totalPrice) / float(instance.quantity)

        parts = ProformaInvoicePart.objects.filter(invoice = proformaInvoice)
        expenses = ProformaInvoiceExpense.objects.filter(invoice = proformaInvoice)
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
        partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (proformaInvoice.orderConfirmation.quotation.manuelDiscount/100)
        for expense in expenses:
            partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
            
        partsTotals["totalExpense"] = partsTotals["totalExpense"] + (instance.totalPrice - senderExpense.totalPrice)
        
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
        partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (proformaInvoice.vat/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
        
        proformaInvoice.totalPrice = round(partsTotals["totalFinal"], 2)
        proformaInvoice.save()
        
  