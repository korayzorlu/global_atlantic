from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from card.models import Current
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

def current_fix(company,currency,instance=None):
    current = Current.objects.filter(company = company, currency = currency).first()

    sendInvoices = company.send_invoice_customer.select_related().filter(currency = currency)
    incomingInvoices = company.incoming_invoice_customer.select_related().filter(currency = currency)
    paymentIns = company.payment_customer.select_related().filter(type = "in", currency = currency)
    paymentOuts = company.payment_customer.select_related().filter(type = "out", currency = currency)

    invoiceTotal = sum(Decimal(str(sendInvoice.totalPrice)) for sendInvoice in sendInvoices) - sum(Decimal(str(incomingInvoice.totalPrice)) for incomingInvoice in incomingInvoices)
    paymentTotal = sum(Decimal(str(paymentIn.amount)) for paymentIn in paymentIns) - sum(Decimal(str(paymentOut.amount)) for paymentOut in paymentOuts)

    if not current:
        current = Current.objects.create(
            sourceCompany = company.sourceCompany,
            company = company,
            currency = currency
        )
        current.save()

    current.debt = float(invoiceTotal)
    current.credit = float(paymentTotal)
    current.save()