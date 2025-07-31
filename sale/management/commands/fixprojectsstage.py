from django.core.management.base import BaseCommand, CommandError
from sale.models import Request, Inquiry, Quotation, PurchaseOrder, Collection, RequestPart, InquiryPart, QuotationPart,OrderConfirmation,OrderTracking,OrderNotConfirmation, PurchaseOrderPart, CollectionPart

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        requests = Request.objects.filter()
        for request in requests:
            project = request.project
            project.stage = "request"
            project.save()
        
        inquiries = Inquiry.objects.filter()
        for inquiry in inquiries:
            project = inquiry.project
            project.stage = "inquiry"
            project.save()
            
        quotations = Quotation.objects.filter()
        for quotation in quotations:
            project = quotation.project
            project.stage = "quotation"
            project.save()
            
        orderConfirmations = OrderConfirmation.objects.filter()
        for orderConfirmation in orderConfirmations:
            project = orderConfirmation.project
            project.stage = "order_confirmation"
            project.save()
            
        orderNotConfirmations = OrderNotConfirmation.objects.filter()
        for orderNotConfirmation in orderNotConfirmations:
            project = orderNotConfirmation.project
            project.stage = "order_not_confirmation"
            project.save()
            
        purchaseOrders = PurchaseOrder.objects.filter()
        for purchaseOrder in purchaseOrders:
            project = purchaseOrder.project
            project.stage = "purchase_order"
            project.save()
            
        orderTrackings = OrderTracking.objects.filter()
        for orderTracking in orderTrackings:
            project = orderTracking.project
            project.stage = "order_tracking"
            project.save()
            
        orderConfirmations = OrderConfirmation.objects.filter()
        for orderConfirmation in orderConfirmations:
            if orderConfirmation.status == "invoiced":
                project = orderConfirmation.project
                project.stage = "invoiced"
                project.save()