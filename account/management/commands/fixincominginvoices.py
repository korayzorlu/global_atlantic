from django.core.management.base import BaseCommand, CommandError
from sale.models import QuotationPart,Quotation
from account.models import IncomingInvoice,IncomingInvoiceExpense,IncomingInvoicePart,IncomingInvoiceItem

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
        incomingInvoices = IncomingInvoice.objects.filter()
        for incomingInvoice in incomingInvoices:
            firstDate = str(incomingInvoice.incomingInvoiceDate.year).zfill(4) + str(incomingInvoice.incomingInvoiceDate.month).zfill(2)
            secondDate = str(incomingInvoice.incomingInvoiceDate.day).zfill(2) + str(incomingInvoice.incomingInvoiceDate.month).zfill(2) + str(incomingInvoice.incomingInvoiceDate.year).zfill(4)
            currencyCode = incomingInvoice.currency.code
            
            if rs.get("https://www.tcmb.gov.tr/kurlar/" + firstDate + "/" + secondDate + ".xml").status_code == 200:
                ratesSource = rs.get("https://www.tcmb.gov.tr/kurlar/" + firstDate + "/" + secondDate + ".xml").content
                rates = xmltodict.parse(ratesSource)
                
                rates = rates["Tarih_Date"]["Currency"]
                
                theRate = next((rate for rate in rates if rate['@Kod'] == currencyCode), None)
                
                incomingInvoice.exchangeRate = theRate["ForexBuying"]
                incomingInvoice.save()