from django.core.management.base import BaseCommand, CommandError
from sale.models import QuotationPart,Quotation
from account.models import ProformaInvoicePart, SendInvoicePart, ProformaInvoice, SendInvoice

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        proformaInvoices = ProformaInvoice.objects.filter()
        for proformaInvoice in proformaInvoices:
            quotation = proformaInvoice.orderConfirmation.quotation
            quotationParts = QuotationPart.objects.filter(quotation = quotation).order_by("sequency")
            for quotationPart in quotationParts:
                proformaInvoicePart = ProformaInvoicePart.objects.filter(invoice = proformaInvoice, quotationPart = quotationPart).first()
                proformaInvoicePart.sequency = quotationPart.sequency
                proformaInvoicePart.save()
                
        sendInvoices = SendInvoice.objects.filter()
        for sendInvoice in sendInvoices:
            quotation = sendInvoice.orderConfirmation.quotation
            quotationParts = QuotationPart.objects.filter(quotation = quotation).order_by("sequency")
            for quotationPart in quotationParts:
                sendInvoicePart = SendInvoicePart.objects.filter(invoice = sendInvoice, quotationPart = quotationPart).first()
                sendInvoicePart.sequency = quotationPart.sequency
                sendInvoicePart.save()
                