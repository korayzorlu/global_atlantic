from django.core.management.base import BaseCommand, CommandError
from sale.models import QuotationPart,Quotation
from account.models import IncomingInvoice,IncomingInvoiceExpense,IncomingInvoicePart,IncomingInvoiceItem

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        incomingInvoiceParts = IncomingInvoicePart.objects.filter()
        
        for part in incomingInvoiceParts:
            if part.purchaseOrderPart:
                part.part = part.purchaseOrderPart.inquiryPart.requestPart.part
                part.save()
                
            item = IncomingInvoiceItem.objects.create(
                user = part.user,
                sessionKey = part.sessionKey,
                invoice = part.invoice,
                purchaseOrderPart = part.purchaseOrderPart,
                part = part.part,
                name = part.partNo,
                description = part.description,
                unit = part.unit,
                quantity = part.quantity,
                sequency = part.sequency,
                unitPrice = part.unitPrice,
                totalPrice = part.totalPrice,
                vat = part.vat,
                vatPrice = part.vatPrice
                
            )
            item.save()
                