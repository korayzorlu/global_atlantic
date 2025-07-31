from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from sale.models import Request, Inquiry, Quotation, PurchaseOrder, Collection, RequestPart, InquiryPart, QuotationPart, PurchaseOrderPart, CollectionPart
from data.models import Maker

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        quotations = Quotation.objects.filter()
        
        for quotation in quotations:
            print(quotation)
        