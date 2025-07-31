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

def incoming_invoice_price_fix(invoice,items,expenses, instance=None):
    itemsTotal = 0
    
    if instance:
        itemsTotal = round(sum(Decimal(str(item.totalPrice)) for item in items) + sum(Decimal(str(expense.totalPrice)) for expense in expenses) + Decimal(str(instance.totalPrice)),2)
    else:
        itemsTotal = round(sum(Decimal(str(item.totalPrice)) for item in items) + sum(Decimal(str(expense.totalPrice)) for expense in expenses),2)

    if invoice.group == "order":
        if invoice.purchaseOrder:
            discountPrice = invoice.purchaseOrder.totalDiscountPrice
        else:
            discountPrice = 0
    elif invoice.group == "purchasing":
        if invoice.purchasingPurchaseOrder:
            discountPrice = invoice.purchasingPurchaseOrder.totalDiscountPrice
        else:
            discountPrice = 0
    print(invoice.vat)
    vatPrice = round((Decimal(str(itemsTotal)) - Decimal(str(discountPrice))) * (Decimal(str(invoice.vat))/100),2)
    print(vatPrice)
    totalPrice = Decimal(str(itemsTotal)) - Decimal(str(discountPrice)) + Decimal(str(vatPrice))
                

    invoice.netPrice = float(itemsTotal)
    invoice.discountPrice = float(discountPrice)
    invoice.vatPrice = float(vatPrice)
    invoice.totalPrice = float(totalPrice)
    invoice.save()

    if (invoice.totalPrice - invoice.paidPrice) <= 0:
        invoice.payed = True
        invoice.save()
    else:
        invoice.payed = False
        invoice.save()
