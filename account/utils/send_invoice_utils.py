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

def send_invoice_price_fix(invoice,items,expenses, instance=None):
    itemsTotal = 0
    
    if instance:
        itemsTotal = round(sum(Decimal(str(item.totalPrice)) for item in items) + sum(Decimal(str(expense.totalPrice)) for expense in expenses) + Decimal(str(instance.totalPrice)),2)
    else:
        itemsTotal = round(sum(Decimal(str(item.totalPrice)) for item in items) + sum(Decimal(str(expense.totalPrice)) for expense in expenses),2)

    if invoice.group == "order":
        if invoice.orderConfirmation:
            discountPrice = invoice.orderConfirmation.quotation.totalDiscountPrice
        else:
            discountPrice = 0
    elif invoice.group == "service":
        if invoice.offer:
            discountPrice = invoice.offer.totalDiscountPrice
        else:
            discountPrice = 0

    vatPrice = round((Decimal(str(itemsTotal)) - Decimal(str(discountPrice)) - Decimal(str(invoice.extraDiscountPrice))) * (Decimal(str(invoice.vat))/100),2)

    totalPrice = Decimal(str(itemsTotal)) - Decimal(str(discountPrice)) - Decimal(str(invoice.extraDiscountPrice)) + Decimal(str(vatPrice))
                
    invoice.netPrice = float(itemsTotal)
    invoice.discountPrice = float(discountPrice)
    invoice.vatPrice = float(vatPrice)
    invoice.totalPrice = float(totalPrice)
    invoice.save()

    if (invoice.totalPrice - invoice.paidPrice) <= 0:
        invoice.payed = True
        invoice.save()

        data = {
            "blocks":[
                {
                    "id" : f"payed-container-sendInvoice-{invoice.id}",
                    "value" : "<div class='alert p-1 mb-0 mr-2 me-3' role='alert' data-mdb-color='success'><i class='fas fa-circle-check me-3'></i>Paid</div>",
                    "type" : "html"
                }
            ],
            "currency":invoice.currency.symbol
        }
        updateDetail(data,"default")
    else:
        invoice.payed = False
        invoice.save()

        data = {
            "blocks":[
                {
                    "id" : f"payed-container-sendInvoice-{invoice.id}",
                    "value" : "<div class='alert p-1 mb-0 mr-2 me-3' role='alert' data-mdb-color='warning'><i class='fas fa-exclamation-triangle me-3'></i>Waiting for payment</div>",
                    "type" : "html"
                }
            ],
            "currency":invoice.currency.symbol
        }
        updateDetail(data,"default")
