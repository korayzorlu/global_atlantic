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
        theRequests = Request.objects.filter()
        
        sequencyCount = 0
        for theRequest in theRequests:
            requestParts = RequestPart.objects.filter(theRequest = theRequest).order_by("id")
            sequencyCount = 0
            for requestPart in requestParts:
                requestPart.sequency = sequencyCount + 1
                requestPart.save()
                sequencyCount = sequencyCount + 1
            
            inquiries = Inquiry.objects.filter(theRequest = theRequest)
            sequencyCount = 0
            for inquiry in inquiries:
                inquiryParts = InquiryPart.objects.filter(inquiry = inquiry).order_by("requestPart__sequency")
                sequencyCount = 0
                for inquiryPart in inquiryParts:
                    inquiryPart.sequency = sequencyCount + 1
                    inquiryPart.save()
                    sequencyCount = sequencyCount + 1
            
            quotations = Quotation.objects.filter(project = theRequest.project)
            sequencyCount = 0
            for quotation in quotations:
                quotationParts = QuotationPart.objects.filter(quotation = quotation).order_by("inquiryPart__sequency")
                sequencyCount = 0
                for quotationPart in quotationParts:
                    quotationPart.sequency = sequencyCount + 1
                    quotationPart.save()
                    sequencyCount = sequencyCount + 1
            
            purchaseOrders = PurchaseOrder.objects.filter(project = theRequest.project)
            sequencyCount = 0
            for purchaseOrder in purchaseOrders:
                purchaseOrderParts = PurchaseOrderPart.objects.filter(purchaseOrder = purchaseOrder).order_by("inquiryPart__sequency")
                sequencyCount = 0
                for purchaseOrderPart in purchaseOrderParts:
                    purchaseOrderPart.sequency = sequencyCount + 1
                    purchaseOrderPart.save()
                    sequencyCount = sequencyCount + 1
            
                collections = Collection.objects.filter(purchaseOrder = purchaseOrder)
                sequencyCount = 0
                for collection in collections:
                    collectionParts = CollectionPart.objects.filter(collection = collection).order_by("purchaseOrderPart__sequency")
                    sequencyCount = 0
                    for collectionPart in collectionParts:
                        collectionPart.sequency = sequencyCount + 1
                        collectionPart.save()
                        sequencyCount = sequencyCount + 1