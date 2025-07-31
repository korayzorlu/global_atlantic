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
        quotation = Quotation.objects.get(id = 135)
        inquiryPart = InquiryPart.objects.get(id = 2190)
        user = User.objects.get(id = 28)
        maker = Maker.objects.get(id = 180)
        
        quotationPart = QuotationPart.objects.create(user = user,quotation = quotation,inquiryPart = inquiryPart,maker = maker)
        quotationPart.save()