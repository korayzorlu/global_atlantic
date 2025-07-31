from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from ..models import *

from decimal import Decimal

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

def process_add(instance):
    if isinstance(instance, SendInvoice):
        process = Process.objects.create(
                sourceCompany = instance.sourceCompany,
                user = instance.user,
                company = instance.customer,
                sendInvoice = instance,
                companyName = instance.customer.name,
                sourceNo = instance.sendInvoiceNo,
                type = "send_invoice",
                amount = instance.totalPrice,
                currency = instance.currency,
                processDateTime = instance.created_date
        )
        process.save()
    elif isinstance(instance, IncomingInvoice):
        process = Process.objects.create(
                sourceCompany = instance.sourceCompany,
                user = instance.user,
                company = instance.seller,
                incomingInvoice = instance,
                companyName = instance.customer.name,
                sourceNo = instance.incomingInvoiceNo,
                type = "incoming_invoice",
                amount = instance.totalPrice,
                currency = instance.currency,
                processDateTime = instance.created_date
        )
        process.save()
    elif isinstance(instance, Payment):
        if instance.type == "in":
            type = "payment_in"
        elif instance.type == "out":
            type = "payment_out"
        process = Process.objects.create(
                sourceCompany = instance.sourceCompany,
                user = instance.user,
                company = instance.customer,
                payment = instance,
                companyName = instance.customer.name,
                sourceNo = instance.paymentNo,
                type = type,
                amount = instance.amount,
                currency = instance.currency,
                processDateTime = instance.created_date
        )
        process.save()
        
    identificationCode = "PRC"
    yearCode = int(str(datetime.today().date().year)[-2:])
    startCodeValue = 1
    
    lastProcess = Process.objects.filter(sourceCompany = instance.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
    
    if lastProcess:
        lastCode = lastProcess.code
    else:
        lastCode = startCodeValue - 1
    
    code = int(lastCode) + 1
    process.code = code
    
    process.yearCode = yearCode
    
    processNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
    process.processNo = processNo
    
    process.save()

def process_update(instance):
    if isinstance(instance, SendInvoice):
        process = instance.process_send_invoice.first()
        process.company = instance.customer
        process.companyName = instance.customer.name
        process.amount = instance.totalPrice
        process.sourceNo = instance.sendInvoiceNo
    elif isinstance(instance, IncomingInvoice):
        process = instance.process_incoming_invoice.first()
        process.company = instance.seller
        process.companyName = instance.seller.name
        process.amount = instance.totalPrice
        process.sourceNo = instance.incomingInvoiceNo
    elif isinstance(instance, Payment):
        process = instance.process_payment.first()
        process.company = instance.customer
        process.companyName = instance.customer.name
        process.amount = instance.amount
        process.sourceNo = instance.paymentNo
    
    process.save()