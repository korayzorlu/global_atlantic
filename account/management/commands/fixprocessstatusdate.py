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
        processStatuses = ProcessStatus.objects.filter()
        
        for processStatus in processStatuses:
            if processStatus.project:
                processStatus.created_date = processStatus.project.order_tracking.first().created_date
                processStatus.save()
                print(f"ps date: {processStatus.created_date} - p date: {processStatus.project.order_tracking.first().created_date}")
            elif processStatus.offer:
                processStatus.created_date = processStatus.offer.created_date
                processStatus.save()
                print(f"ps date: {processStatus.created_date} - p date: {processStatus.offer.created_date}")
            elif processStatus.purchasingProject:
                processStatus.created_date = processStatus.purchasingProject.purchasing_purchase_order.first().created_date
                processStatus.save()
                print(f"ps date: {processStatus.created_date} - p date: {processStatus.purchasingProject.purchasing_purchase_order.first().created_date}")