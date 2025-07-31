from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.core.signals import request_finished

from ..models import *
from ..utils.account_utils import *
from ..utils.payment_utils import *
from ..utils.current_utils import *
from ..utils.process_utils import *
from card.models import Current
from administration.models import ActionLog

from core.middleware import get_current_user

import inspect
import logging
import traceback

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


@receiver(post_save, sender=Payment)
def payment_post(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():
            if created:
                if instance.type == "in":
                    #####bank#####
                    sourceBank = SourceBank.objects.select_related().select_for_update().filter(id = instance.sourceBank.id).first()
                    sourceBank.balance += instance.amount
                    sourceBank.save()
                    #####bank-end#####

                    #####current#####
                    current = Current.objects.select_related().select_for_update().filter(
                        sourceCompany = instance.sourceCompany,
                        company = instance.customer,
                        currency = instance.currency
                    ).first()
                    if current:
                        current.credit += instance.amount
                        current.save()
                    else:
                        current = Current.objects.create(
                            sourceCompany = instance.sourceCompany,
                            company = instance.customer,
                            currency = instance.currency
                        )
                        current.save()
                        current.credit += instance.amount
                        current.save()
                    #####current-end#####

                    process_add(instance)
                    payment_amount_fix(instance)
                    company_credit_fix(instance.customer)
                elif instance.type == "out":
                    #####bank#####
                    sourceBank = SourceBank.objects.select_related().select_for_update().filter(id = instance.sourceBank.id).first()
                    sourceBank.balance -= instance.amount
                    sourceBank.save()
                    #####bank-end#####

                    #####current#####
                    current = Current.objects.select_related().select_for_update().filter(
                        sourceCompany = instance.sourceCompany,
                        company = instance.customer,
                        currency = instance.currency
                    ).first()
                    if current:
                        current.credit -= instance.amount
                        current.save()
                    else:
                        current = Current.objects.create(
                            sourceCompany = instance.sourceCompany,
                            company = instance.customer,
                            currency = instance.currency
                        )
                        current.save()
                        current.credit -= instance.amount
                        current.save()
                    #####current-end#####

                    process_add(instance)
                    payment_amount_fix(instance)
                    company_credit_fix(instance.customer)

                ActionLog.objects.create(user=get_current_user(),action="create",modelName=sender.__name__,objectId=instance.pk,objectName = instance.paymentNo)
            else:
                paymentInvoices = instance.paymentinvoice_set.all().order_by("invoicePaymentDate")
                #payment_invoice_amount_fix(instance,paymentInvoices,instance.amount)
                process_update(instance)
                payment_amount_fix(instance)
                company_credit_fix(instance.customer)

                ActionLog.objects.create(user=get_current_user(),action="update",modelName=sender.__name__,objectId=instance.pk,objectName = instance.paymentNo)
                
    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)
        logger.error(traceback.format_exc())

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")

@receiver(pre_save, sender=Payment)
def payment_pre(sender, instance, **kwargs):
    try:
        data = {"tableName":f"paymentPart-{instance.id}"}       
        reloadTable(data,"start")
        with transaction.atomic():
            if instance.id:
                if instance.type == "in":
                    oldPaymet = Payment.objects.select_related().select_for_update().filter(id=instance.id).first()
                    oldPaymentAmount = oldPaymet.amount
                    newPaymentAmount = instance.amount

                    #####bank#####
                    oldBank = SourceBank.objects.select_related().select_for_update().filter(id = oldPaymet.sourceBank.id).first()
                    newBank = SourceBank.objects.select_related().select_for_update().filter(id = instance.sourceBank.id).first()
                    if oldBank != newBank:
                        oldBank.balance -= oldPaymentAmount
                        oldBank.save()

                        newBank.balance += newPaymentAmount
                        newBank.save()
                    else:
                        sourceBank = SourceBank.objects.select_related().select_for_update().filter(id = instance.sourceBank.id).first()
                        sourceBank.balance = sourceBank.balance - oldPaymentAmount + newPaymentAmount
                        sourceBank.save()
                    #####bank-end#####

                    #####current#####
                    current = Current.objects.select_related().select_for_update().filter(
                        sourceCompany = instance.sourceCompany,
                        company = instance.customer,
                        currency = instance.currency
                    ).first()
                    if current:
                        current.credit = current.credit - oldPaymentAmount + newPaymentAmount
                        current.save()
                    else:
                        current = Current.objects.create(
                            sourceCompany = instance.sourceCompany,
                            company = instance.customer,
                            currency = instance.currency
                        )
                        current.save()
                        current.credit = current.credit - oldPaymentAmount + newPaymentAmount
                        current.save()
                    #####current-end#####

                    #####process güncelleme#####
                    process = Process.objects.select_related().select_for_update().filter(
                        sourceCompany = instance.sourceCompany,
                        company = instance.customer,
                        payment = instance
                    ).first()
                    process.amount = instance.amount
                    process.save()
                    #####process güncelleme-end#####
                    
                elif instance.type == "out":
                    oldPaymet = Payment.objects.select_related().select_for_update().filter(id=instance.id).first()
                    oldPaymentAmount = oldPaymet.amount
                    newPaymentAmount = instance.amount

                    #####bank#####
                    oldBank = SourceBank.objects.select_related().select_for_update().filter(id = oldPaymet.sourceBank.id).first()
                    newBank = SourceBank.objects.select_related().select_for_update().filter(id = instance.sourceBank.id).first()
                    if oldBank != newBank:
                        oldBank.balance += oldPaymentAmount
                        oldBank.save()

                        newBank.balance -= newPaymentAmount
                        newBank.save()
                    else:
                        sourceBank = SourceBank.objects.select_related().select_for_update().filter(id = instance.sourceBank.id).first()
                        sourceBank.balance = sourceBank.balance + oldPaymentAmount - newPaymentAmount
                        sourceBank.save()
                    #####bank-end#####

                    #####current#####
                    current = Current.objects.select_related().select_for_update().filter(
                        sourceCompany = instance.sourceCompany,
                        company = instance.customer,
                        currency = instance.currency
                    ).first()
                    if current:
                        current.credit = current.credit + oldPaymentAmount - newPaymentAmount
                        current.save()
                    else:
                        current = Current.objects.create(
                            sourceCompany = instance.sourceCompany,
                            company = instance.customer,
                            currency = instance.currency
                        )
                        current.save()
                        current.credit = current.credit + oldPaymentAmount - newPaymentAmount
                        current.save()
                    #####current-end#####

                    #####process güncelleme#####
                    process = Process.objects.select_related().select_for_update().filter(
                        sourceCompany = instance.sourceCompany,
                        company = instance.customer,
                        payment = instance
                    ).first()
                    process.amount = instance.amount
                    process.save()
                    #####process güncelleme-end#####

                paymentInvoicesTotal = 0
                paymentInvoices = instance.paymentinvoice_set.all().order_by("invoicePaymentDate")
                paymentInvoicesTotal = sum(Decimal(str(paymentInvoice.amount)) for paymentInvoice in paymentInvoices)
                if newPaymentAmount < paymentInvoicesTotal:
                    payment_invoice_amount_fix(instance,paymentInvoices,newPaymentAmount)
                #####currency#####
                oldCurrency = Currency.objects.select_related().select_for_update().filter(id = oldPaymet.currency.id).first()
                newCurrency = Currency.objects.select_related().select_for_update().filter(id = instance.currency.id).first()
                if oldCurrency != newCurrency:
                    payment_invoice_amount_fix(instance,paymentInvoices,newPaymentAmount)
                #####currency-end#####

        data = {"tableName":f"paymentPart-{instance.id}"}       
        reloadTable(data,"stop")
    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")

@receiver(post_delete, sender=Payment)
def payment_delete(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            if instance.type == "in":
                #####bank#####
                sourceBank = SourceBank.objects.select_related().select_for_update().filter(id = instance.sourceBank.id).first()
                sourceBank.balance -= instance.amount
                sourceBank.save()
                #####bank-end#####

                #####current#####
                current = Current.objects.select_related().select_for_update().filter(
                    sourceCompany = instance.sourceCompany,
                    company = instance.customer,
                    currency = instance.currency
                ).first()
                if current:
                    current.credit -= instance.amount
                    current.save()
                else:
                    current = Current.objects.create(
                        sourceCompany = instance.sourceCompany,
                        company = instance.customer,
                        currency = instance.currency
                    )
                    current.save()
                    current.credit -= instance.amount
                    current.save()
                #####current-end#####
                company_credit_fix(instance.customer)
                
            elif instance.type == "out":
                #####bank#####
                sourceBank = SourceBank.objects.select_related().select_for_update().filter(id = instance.sourceBank.id).first()
                sourceBank.balance += instance.amount
                sourceBank.save()
                #####bank-end#####

                #####current#####
                current = Current.objects.select_related().select_for_update().filter(
                    sourceCompany = instance.sourceCompany,
                    company = instance.customer,
                    currency = instance.currency
                ).first()
                if current:
                    current.credit += instance.amount
                    current.save()
                else:
                    current = Current.objects.create(
                        sourceCompany = instance.sourceCompany,
                        company = instance.customer,
                        currency = instance.currency
                    )
                    current.save()
                    current.credit += instance.amount
                    current.save()
                #####current-end#####
                company_credit_fix(instance.customer)
                
            ActionLog.objects.create(user=get_current_user(),action="delete",modelName=sender.__name__,objectId=instance.pk,objectName = instance.paymentNo)

    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")



@receiver(post_save, sender=PaymentInvoice)
def payment_invoice_post(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():
            if created:
                if instance.payment.type == "in":
                    company_credit_fix(instance.sendInvoice.customer)
                    ActionLog.objects.create(user=get_current_user(),action="create",modelName=sender.__name__,objectId=instance.pk,objectName = instance.sendInvoice.sendInvoiceNo)
                elif instance.payment.type == "out":
                    company_credit_fix(instance.incomingInvoice.seller)
                    ActionLog.objects.create(user=get_current_user(),action="create",modelName=sender.__name__,objectId=instance.pk,objectName = instance.incomingInvoice.incomingInvoiceNo)
                payment_amount_fix(instance.payment)
                
            else:
                if instance.payment.type == "in":
                    payment_invoice_invoice_fix(instance.sendInvoice,instance.payment)
                    company_credit_fix(instance.sendInvoice.customer)
                    ActionLog.objects.create(user=get_current_user(),action="update",modelName=sender.__name__,objectId=instance.pk,objectName = instance.sendInvoice.sendInvoiceNo)
                elif instance.payment.type == "out":
                    payment_invoice_invoice_fix(instance.incomingInvoice,instance.payment)
                    company_credit_fix(instance.incomingInvoice.seller)
                    ActionLog.objects.create(user=get_current_user(),action="update",modelName=sender.__name__,objectId=instance.pk,objectName = instance.incomingInvoice.incomingInvoiceNo)

                payment_amount_fix(instance.payment)
        data = {"tableName":f"paymentPart-{instance.payment.id}"}       
        reloadTable(data,"default")
    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")

@receiver(pre_save, sender=PaymentInvoice)
def payment_invoice_pre(sender, instance, **kwargs):
    try:
        data = {"tableName":f"paymentPart-{instance.payment.id}"}       
        reloadTable(data,"start")
        pre_save.disconnect(payment_invoice_pre, sender=PaymentInvoice)
        with transaction.atomic():
            if instance.id:
                if instance.payment.type == "in":
                    oldPaymentInvoice = PaymentInvoice.objects.select_related().select_for_update().filter(id=instance.id).first()
                    oldPaymentInvoiceAmount = oldPaymentInvoice.amount
                    newPaymentInvoiceAmount = instance.amount
                    instance.invoiceCurrencyAmount = convert_currency(instance.amount,instance.payment.currency.forexBuying,instance.sendInvoice.currency.forexBuying)
                    payment_invoice_invoice_fix(instance.sendInvoice,instance.payment,excludeId=instance.id)
                    if newPaymentInvoiceAmount < 0:
                            instance.amount = 0
                            instance.invoiceCurrencyAmount = 0
                    elif convert_currency(newPaymentInvoiceAmount,instance.payment.currency.forexBuying,instance.sendInvoice.currency.forexBuying) > (instance.sendInvoice.totalPrice - instance.sendInvoice.paidPrice):
                            instance.amount = convert_currency((instance.sendInvoice.totalPrice - instance.sendInvoice.paidPrice),instance.sendInvoice.currency.forexBuying,instance.payment.currency.forexBuying)
                            instance.invoiceCurrencyAmount = instance.sendInvoice.totalPrice - instance.sendInvoice.paidPrice

                    if oldPaymentInvoiceAmount != newPaymentInvoiceAmount:
                        paymentInvoices = instance.payment.paymentinvoice_set.all().exclude(id=instance.id).order_by("invoicePaymentDate")
                        remainingAmount = instance.payment.amount - instance.amount
                        
                        payment_invoice_amount_fix(instance.payment,paymentInvoices,remainingAmount,instance=instance)

                    
                elif instance.payment.type == "out":
                    oldPaymentInvoice = PaymentInvoice.objects.select_related().select_for_update().filter(id=instance.id).first()
                    oldPaymentInvoiceAmount = oldPaymentInvoice.amount
                    newPaymentInvoiceAmount = instance.amount
                    instance.invoiceCurrencyAmount = convert_currency(instance.amount,instance.payment.currency.forexBuying,instance.incomingInvoice.currency.forexBuying)
                    payment_invoice_invoice_fix(instance.incomingInvoice,instance.payment,excludeId=instance.id)
                    if newPaymentInvoiceAmount < 0:
                            instance.amount = 0
                            instance.invoiceCurrencyAmount = 0
                    elif convert_currency(newPaymentInvoiceAmount,instance.payment.currency.forexBuying,instance.incomingInvoice.currency.forexBuying) > (instance.incomingInvoice.totalPrice - instance.incomingInvoice.paidPrice):
                            instance.amount = convert_currency((instance.incomingInvoice.totalPrice - instance.incomingInvoice.paidPrice),instance.incomingInvoice.currency.forexBuying,instance.payment.currency.forexBuying)
                            instance.invoiceCurrencyAmount = instance.incomingInvoice.totalPrice - instance.incomingInvoice.paidPrice
                
                    if oldPaymentInvoiceAmount != newPaymentInvoiceAmount:
                        paymentInvoices = instance.payment.paymentinvoice_set.all().exclude(id=instance.id).order_by("invoicePaymentDate")
                        remainingAmount = instance.payment.amount - instance.amount

                        payment_invoice_amount_fix(instance.payment,paymentInvoices,remainingAmount,instance=instance)

                   
        data = {"tableName":f"paymentPart-{instance.payment.id}"}       
        reloadTable(data,"stop")
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
        pre_save.connect(payment_invoice_pre, sender=PaymentInvoice)
        
@receiver(post_delete, sender=PaymentInvoice)
def payment_invoice_delete(sender, instance, **kwargs):
    try:
        data = {"tableName":f"paymentPart-{instance.payment.id}"}       
        reloadTable(data,"start")
        with transaction.atomic():
            if instance.payment.type == "in":
                try:
                    payment_invoice_invoice_fix(instance.sendInvoice,instance.payment)
                except:
                    pass
                company_credit_fix(instance.sendInvoice.customer)
                ActionLog.objects.create(user=get_current_user(),action="delete",modelName=sender.__name__,objectId=instance.pk,objectName = instance.sendInvoice.sendInvoiceNo)
            elif instance.payment.type == "out":
                try:
                    payment_invoice_invoice_fix(instance.incomingInvoice,instance.payment)
                except:
                    pass
                company_credit_fix(instance.incomingInvoice.seller)
                ActionLog.objects.create(user=get_current_user(),action="delete",modelName=sender.__name__,objectId=instance.pk,objectName = instance.incomingInvoice.incomingInvoiceNo)
            paymentInvoices = instance.payment.paymentinvoice_set.all().order_by("invoicePaymentDate").exclude(id = instance.id)
            payment_invoice_amount_fix(instance.payment,paymentInvoices,instance.payment.amount)

        data = {"tableName":f"paymentPart-{instance.payment.id}"}       
        reloadTable(data,"stop")      
                

    except Exception as e:
        logger = logging.getLogger("django")
        logger.error(e)

        data = {
                "status":"danger",
                "icon":"triangle-exclamation",
                "message":"Error!"
        }
    
        sendAlert(data,"default")
