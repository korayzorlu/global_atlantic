from django.core.management.base import BaseCommand, CommandError
from sale.models import Project,OrderTracking
from service.models import Offer
from purchasing.models import Project as PurchasingProject
from purchasing.models import PurchaseOrder as PurchasingPurchaseOrder
from account.models import ProcessStatus
from source.models import Company as SourceCompany

import pandas as pd
import requests as rs
import xmltodict
import json
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        sourceCompanies = SourceCompany.objects.filter()
        
        for sourceCompany in sourceCompanies:
            print(f"##### {sourceCompany.name} #####")
            orderTrackings = OrderTracking.objects.filter(sourceCompany = sourceCompany)
            offers = Offer.objects.exclude(status = "offer").filter(sourceCompany = sourceCompany)
            purchasingPurchaseOrders = PurchasingPurchaseOrder.objects.filter(sourceCompany = sourceCompany)
            
            #sale
            print(f"Processing sale for {len(orderTrackings)} items...")
            for orderTracking in orderTrackings:
                identificationCode = "PS"
                yearCode = int(str(datetime.today().date().year)[-2:])
                startCodeValue = 1
                
                lastProcessStatus = ProcessStatus.objects.filter(sourceCompany = sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                
                if lastProcessStatus:
                    lastCode = lastProcessStatus.code
                else:
                    lastCode = startCodeValue - 1
                
                code = int(lastCode) + 1
                processStatusNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
                
                processStatus = ProcessStatus.objects.create(
                    sourceCompany = sourceCompany,
                    code = code,
                    yearCode = yearCode,
                    processStatusNo = processStatusNo,
                    project = orderTracking.project,
                    type = "order"
                )
                
                processStatus.save()
            print(f"Sale done!")
            
            #service
            print(f"Processing service for {len(offers)} items...")
            for offer in offers:
                identificationCode = "PS"
                yearCode = int(str(datetime.today().date().year)[-2:])
                startCodeValue = 1
                
                lastProcessStatus = ProcessStatus.objects.filter(sourceCompany = sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                
                if lastProcessStatus:
                    lastCode = lastProcessStatus.code
                else:
                    lastCode = startCodeValue - 1
                
                code = int(lastCode) + 1
                processStatusNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
                
                processStatus = ProcessStatus.objects.create(
                    sourceCompany = sourceCompany,
                    code = code,
                    yearCode = yearCode,
                    processStatusNo = processStatusNo,
                    offer = offer,
                    type = "service"
                )
                
                processStatus.save()
            print(f"Service done!")
                
            #purchasing
            print(f"Processing purchasing for {len(purchasingPurchaseOrders)} items...")
            for purchasingPurchaseOrder in purchasingPurchaseOrders:
                identificationCode = "PS"
                yearCode = int(str(datetime.today().date().year)[-2:])
                startCodeValue = 1
                
                lastProcessStatus = ProcessStatus.objects.filter(sourceCompany = sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                
                if lastProcessStatus:
                    lastCode = lastProcessStatus.code
                else:
                    lastCode = startCodeValue - 1
                
                code = int(lastCode) + 1
                processStatusNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
                
                processStatus = ProcessStatus.objects.create(
                    sourceCompany = sourceCompany,
                    code = code,
                    yearCode = yearCode,
                    processStatusNo = processStatusNo,
                    purchasingProject = purchasingPurchaseOrder.project,
                    type = "purchasing"
                )
                
                processStatus.save()
            print(f"Service done!\n")
        print(f"All done!")
        
# if obj.type == "order":
    
# elif obj.type == "service":
    
# elif obj.type == "purchasing":
    