from django.core.management.base import BaseCommand, CommandError
from card.models import Vessel, Company, Country, City, Currency, EnginePart
from data.models import Maker, MakerType

from django.contrib.auth.models import User

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        data = pd.read_excel("./excelfile/suppliers-data.xlsx", "system upload")
        df = pd.DataFrame(data)
        
        for i in range(len(df["Supplier"])):
            supplier = Company.objects.filter(name = df["Supplier"][i].upper()).first()
            
            if not supplier:
                if pd.isnull(df["Address"][i]):
                    address = ""
                else:
                    address = df["Address"][i]
                    
                if pd.isnull(df["Country"][i]):
                    country = None
                else:
                    country = Country.objects.get(iso3 = df["Country"][i])
                    
                if pd.isnull(df["City"][i]):
                    city = None
                else:
                    city = City.objects.filter(name = df["City"][i]).first()
                    if not city:
                        city = None
                    
                if pd.isnull(df["VatNo"][i]):
                    vatNo = ""
                else:
                    vatNo = df["VatNo"][i]
                    
                if pd.isnull(df["Phone"][i]):
                    phone1 = ""
                else:
                    phone1 = df["Phone"][i]
                    
                if pd.isnull(df["Fax"][i]):
                    fax = ""
                else:
                    fax = df["Fax"][i]
                    
                if pd.isnull(df["Email"][i]):
                    email = ""
                else:
                    email = df["Email"][i]
                    
                if pd.isnull(df["Credit Limit"][i]):
                    creditLimit = 0
                else:
                    if df["Credit Limit"][i] == "IN ADVANCE":
                        creditLimit = 0
                    else:
                        creditLimit = df["Credit Limit"][i]
                        
                if pd.isnull(df["Currency"][i]):
                    currency = None
                else:
                    currency = Currency.objects.filter(code = df["Currency"][i]).first()
                    
                if pd.isnull(df["Payment Term"][i]):
                    creditPeriot = ""
                else:
                    creditPeriot = df["Payment Term"][i]
                                
                supplier = Company.objects.create(
                    supplierCheck = True,
                    name = df["Supplier"][i].upper(),
                    address = address,
                    country = country,
                    city = city,
                    vatNo = vatNo,
                    phone1 = phone1,
                    fax = fax,
                    email = email,
                    creditLimit = creditLimit,
                    currency = currency,
                    creditPeriot = creditPeriot
                )
                supplier.save()
            else:
                print(supplier)