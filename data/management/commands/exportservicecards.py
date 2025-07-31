from django.core.management.base import BaseCommand, CommandError
from sale.models import Project,OrderTracking
from service.models import Offer
from purchasing.models import Project as PurchasingProject
from purchasing.models import PurchaseOrder as PurchasingPurchaseOrder
from account.models import ProcessStatus
from source.models import Company as SourceCompany
from data.models import ServiceCard

import os
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
        base_path = os.path.join(os.getcwd(), "media", "docs", str(4), "data", "service_card", "documents")
        
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        parts = ServiceCard.objects.filter(sourceCompany = 4).order_by("group")

        data = {
            "Group": [],
            "Serice Code": [],
            "Name": [],
            "About": []
            
        }
        
        seq = 0
        for part in parts:
            data["Group"].append(part.group)
            data["Serice Code"].append(part.code)
            data["Name"].append(part.name)
            data["About"].append(part.about)
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/service-card-list.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Service Card', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
    