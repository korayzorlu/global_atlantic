from django.core.management.base import BaseCommand, CommandError
from sale.models import QuotationPart,Quotation
from account.models import IncomingInvoice,IncomingInvoiceExpense,ProformaInvoicePart,ProformaInvoiceItem

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        proformaInvoiceParts = ProformaInvoicePart.objects.filter()
        
        for part in proformaInvoiceParts:
            if part.quotationPart:
                part.part = part.quotationPart.inquiryPart.requestPart.part
                part.save()
                
            item = ProformaInvoiceItem.objects.create(
                user = part.user,
                sessionKey = part.sessionKey,
                invoice = part.invoice,
                quotationPart = part.quotationPart,
                part = part.quotationPart.inquiryPart.requestPart.part,
                name = part.quotationPart.inquiryPart.requestPart.part.partNo,
                description = part.quotationPart.inquiryPart.requestPart.part.description,
                unit = part.quotationPart.inquiryPart.requestPart.part.unit,
                quantity = part.quantity,
                sequency = part.sequency,
                unitPrice = part.unitPrice,
                totalPrice = part.totalPrice,
                vat = part.vat,
                vatPrice = part.vatPrice
                
            )
            item.save()
                