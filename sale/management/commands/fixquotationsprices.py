from django.core.management.base import BaseCommand, CommandError
from sale.models import Request, Inquiry, Quotation, PurchaseOrder, Collection, RequestPart, InquiryPart, QuotationPart, PurchaseOrderPart, CollectionPart

import pandas as pd

class Command(BaseCommand):
    help = 'Fix Quotations Prices'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        quotations = Quotation.objects.filter()
        
        for quotation in quotations:
            parts = QuotationPart.objects.filter(quotation = quotation)
            partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
            partsTotal = 0
            
            for part in parts:
                partsTotal  = partsTotal + part.totalPrice3
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice1
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice2
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice3
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice1
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice2
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice3
            
            if quotation.manuelDiscountAmount > 0:
                partsTotals["totalDiscount"] = quotation.manuelDiscountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (quotation.manuelDiscount/100)
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
            
            quotation.totalDiscountPrice = round(partsTotals["totalDiscount"],2)
            quotation.totalBuyingPrice = round(partsTotals["totalTotalPrice1"],2)
            quotation.totalSellingPrice = round(partsTotals["totalFinal"],2)
            quotation.save()
            