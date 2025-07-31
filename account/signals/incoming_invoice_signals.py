from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.core.signals import request_finished

from ..models import *
from ..tasks import *
from ..utils.payment_utils import *
from ..utils.current_utils import *
from ..utils.process_utils import *
from ..utils.incoming_invoice_utils import *
from card.models import Current
from administration.models import ActionLog

from core.middleware import get_current_user,get_current_request

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

@receiver(post_save, sender=IncomingInvoice)
def incoming_invoice_post(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():
            if created:
                data = {
                    "blocks":[
                        {"id" : f"incomingInvoiceTotalNetPrice-{instance.id}", "value" : instance.netPrice, "type" : "price"},
                        {"id" : f"incomingInvoiceTotalDiscountPrice-{instance.id}", "value" : instance.discountPrice, "type" : "price"},
                        {"id" : f"incomingInvoiceTotalVatPrice-{instance.id}", "value" : instance.vatPrice, "type" : "price"},
                        {"id" : f"incomingInvoiceTotalTotalPrice-{instance.id}", "value" : instance.totalPrice, "type" : "price"},
                        {"id" : f"incomingInvoiceTotalPayment-{instance.id}", "value" : instance.paidPrice, "type" : "price"},
                        {"id" : f"incomingInvoiceTotalBalance-{instance.id}", "value" : instance.totalPrice - instance.paidPrice, "type" : "price"}
                    ],
                    "currency":instance.currency.symbol
                }
                updateDetail(data,"default")
                data = {"tableName":"incomingInvoice"}       
                reloadTable(data,"default")

                process_add(instance)
                ActionLog.objects.create(user=get_current_user(),action="create",modelName=sender.__name__,objectId=instance.pk,objectName = instance.incomingInvoiceNo)
            else:
                print(instance.paymentDate.strftime("%d/%m/%Y"))
                data = {
                    "blocks":[
                        {"id" : f"incomingInvoiceTotalNetPrice-{instance.id}", "value" : instance.netPrice, "type" : "price"},
                        {"id" : f"incomingInvoiceTotalDiscountPrice-{instance.id}", "value" : instance.discountPrice, "type" : "price"},
                        {"id" : f"incomingInvoiceTotalVatPrice-{instance.id}", "value" : instance.vatPrice, "type" : "price"},
                        {"id" : f"incomingInvoiceTotalTotalPrice-{instance.id}", "value" : instance.totalPrice, "type" : "price"},
                        {"id" : f"incomingInvoiceTotalPayment-{instance.id}", "value" : instance.paidPrice, "type" : "price"},
                        {"id" : f"incomingInvoiceTotalBalance-{instance.id}", "value" : instance.totalPrice - instance.paidPrice, "type" : "price"},
                        {"id" : f"formOutline-incomingInvoice-paymentDate-{instance.id}", "value" : instance.paymentDate.strftime("%d/%m/%Y"), "type" : "date"}
                    ],
                    "currency":instance.currency.symbol
                }
                updateDetail(data,"default")
                data = {"tableName":"incomingInvoice"}       
                reloadTable(data,"default")

                current_fix(instance.seller,instance.currency)
                process_update(instance)
                ActionLog.objects.create(user=get_current_user(),action="update",modelName=sender.__name__,objectId=instance.pk,objectName = instance.incomingInvoiceNo)
             
    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)
        print(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")

@receiver(pre_save, sender=IncomingInvoice)
def incoming_invoice_pre(sender, instance, **kwargs):
    try:
        pre_save.disconnect(incoming_invoice_pre, sender=IncomingInvoice)
        with transaction.atomic():
            if instance.id:
                items = instance.incominginvoiceitem_set.select_for_update().all()
                expenses = instance.incominginvoiceexpense_set.select_for_update().all()
                incoming_invoice_price_fix(instance, items, expenses)


             
    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")
    
    finally:
        # Sinyali yeniden etkinleştiriyoruz
        pre_save.connect(incoming_invoice_pre, sender=IncomingInvoice)

@receiver(post_delete, sender=IncomingInvoice)
def incoming_invoice_delete(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            current_fix(instance.customer,instance.currency)
            ActionLog.objects.create(user=get_current_user(),action="delete",modelName=sender.__name__,objectId=instance.pk,objectName = instance.incomingInvoiceNo)

    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")

@receiver(post_save, sender=IncomingInvoiceItem)
def incoming_invoice_item_post(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():
            if created:
                pass
            else:
                request = get_current_request()

                data = {
                    "block":f"message-container-incomingInvoice-{instance.invoice.id}",
                    "icon":"",
                    "message":"Updating invoice...",
                    "stage" : "loading",
                    "buttons": f"tabPane-incomingInvoice-{instance.invoice.id} .modal-header .tableTopButtons"
                }
                    
                sendAlert(data,"form")

                incomingInvoicePdfTask.delay(instance.sourceCompany.id, instance.invoice.id,request.build_absolute_uri(),"incomingInvoice")
    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")

@receiver(pre_save, sender=IncomingInvoiceItem)
def incoming_invoice_item_pre(sender, instance, **kwargs):
    try:
        pre_save.disconnect(incoming_invoice_item_pre, sender=IncomingInvoiceItem)
        with transaction.atomic():
            if sender.objects.filter(id=instance.id).exists():

                senderIncomingInvoicePart = sender.objects.get(id=instance.id)
                incomingInvoice = senderIncomingInvoicePart.invoice

                if getattr(senderIncomingInvoicePart, "quantity") != getattr(instance, "quantity"):
                    if float(instance.quantity) == 0:
                        instance.unitPrice = 0
                    instance.totalPrice = (float(instance.unitPrice) * float(instance.quantity)) + float(instance.vatPrice)
                    
                if getattr(senderIncomingInvoicePart, "unitPrice") != getattr(instance, "unitPrice"):
                    instance.totalPrice = float(instance.unitPrice) * float(instance.quantity)
                    
                if getattr(senderIncomingInvoicePart, "totalPrice") != getattr(instance, "totalPrice"):
                    if float(instance.totalPrice) == 0:
                        instance.unitPrice = 0
                    else:
                        instance.unitPrice = float(instance.totalPrice) / float(instance.quantity)

                items = instance.invoice.incominginvoiceitem_set.select_for_update().all().exclude(id = instance.id)
                expenses = instance.invoice.incominginvoiceexpense_set.select_for_update().all()
                incoming_invoice_price_fix(instance.invoice, items, expenses,instance)
    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")

    finally:
        # Sinyali yeniden etkinleştiriyoruz
        pre_save.connect(incoming_invoice_item_pre, sender=IncomingInvoiceItem)


@receiver(post_save, sender=IncomingInvoiceExpense)
def incoming_invoice_expense_post(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():
            if created:
                senderExpense = sender.objects.filter(id=instance.id).first()
                incomingInvoice = senderExpense.invoice

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
                        
                items = instance.invoice.incominginvoiceitem_set.select_for_update().all()
                expenses = instance.invoice.incominginvoiceexpense_set.select_for_update().all().exclude(id = instance.id)
                incoming_invoice_price_fix(instance.invoice, items, expenses,instance)
            else:
                request = get_current_request()

                incomingInvoicePdfTask.delay(instance.sourceCompany.id, instance.invoice.id,request.build_absolute_uri(),"incomingInvoice")

    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")


@receiver(pre_save, sender=IncomingInvoiceExpense)
def incoming_invoice_expense_pre(sender, instance, **kwargs):
    try:
        pre_save.disconnect(incoming_invoice_expense_pre, sender=IncomingInvoiceExpense)
        with transaction.atomic():
            if sender.objects.filter(id=instance.id).exists():

                senderExpense = sender.objects.filter(id=instance.id).first()
                incomingInvoice = senderExpense.invoice

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
                        
                items = instance.invoice.incominginvoiceitem_set.select_for_update().all()
                expenses = instance.invoice.incominginvoiceexpense_set.select_for_update().all().exclude(id = instance.id)
                incoming_invoice_price_fix(instance.invoice, items, expenses,instance)
    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")

    finally:
        # Sinyali yeniden etkinleştiriyoruz
        pre_save.connect(incoming_invoice_expense_pre, sender=IncomingInvoiceExpense)
