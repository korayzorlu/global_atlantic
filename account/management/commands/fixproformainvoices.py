from django.core.management.base import BaseCommand, CommandError
from sale.models import QuotationPart,Quotation
from account.models import ProformaInvoice,ProformaInvoiceExpense,ProformaInvoicePart,ProformaInvoiceItem

import pandas as pd
import requests as rs
import xmltodict
import json

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        proformaInvoices = ProformaInvoice.objects.filter()
        for proformaInvoice in proformaInvoices:
            firstDate = str(proformaInvoice.proformaInvoiceDate.year).zfill(4) + str(proformaInvoice.proformaInvoiceDate.month).zfill(2)
            secondDate = str(proformaInvoice.proformaInvoiceDate.day).zfill(2) + str(proformaInvoice.proformaInvoiceDate.month).zfill(2) + str(proformaInvoice.proformaInvoiceDate.year).zfill(4)
            currencyCode = proformaInvoice.currency.code
            
            if rs.get("https://www.tcmb.gov.tr/kurlar/" + firstDate + "/" + secondDate + ".xml").status_code == 200:
                ratesSource = rs.get("https://www.tcmb.gov.tr/kurlar/" + firstDate + "/" + secondDate + ".xml").content
                rates = xmltodict.parse(ratesSource)
                
                rates = rates["Tarih_Date"]["Currency"]
                
                theRate = next((rate for rate in rates if rate['@Kod'] == currencyCode), None)
                
                proformaInvoice.exchangeRate = theRate["ForexBuying"]
                proformaInvoice.save()