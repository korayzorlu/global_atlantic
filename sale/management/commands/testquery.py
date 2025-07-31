from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from sale.models import Request, Inquiry, Quotation,OrderConfirmation, PurchaseOrder, OrderTracking, Collection, RequestPart, InquiryPart, QuotationPart, PurchaseOrderPart, CollectionPart
from data.models import Maker,Part

import pandas as pd
import time

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        start = time.perf_counter()
        
        custom_related_fields = ["project","theRequest"]
        queryset = OrderTracking.objects.select_related(*custom_related_fields).prefetch_related().all()
    
        objects = []
        for object in queryset:
            objects.append({'id': object.id, 'name': object.project.projectNo, 'project': object.theRequest.requestNo, 'purchaseOrders': object.purchaseOrders})
            
        endt = time.perf_counter()
        
        print(f"Finished in : {(endt- start):.2f}s")
