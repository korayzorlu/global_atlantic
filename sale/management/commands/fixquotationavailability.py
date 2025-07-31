from django.core.management.base import BaseCommand, CommandError
from sale.models import Request, Inquiry, Quotation, PurchaseOrder, Collection, RequestPart, InquiryPart, QuotationPart, PurchaseOrderPart, CollectionPart

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        quotationParts = QuotationPart.objects.filter()
        
        for quotationPart in quotationParts:
            quotationPart.availabilityChar = str(quotationPart.availability)
            quotationPart.save()