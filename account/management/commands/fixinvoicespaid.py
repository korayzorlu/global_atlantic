from django.core.management.base import BaseCommand, CommandError
from sale.models import QuotationPart,Quotation
from account.models import *

from card.models import Current,Company, Currency
from source.models import Bank

from account.utils.payment_utils import *
from account.utils.send_invoice_utils import *
from account.utils.incoming_invoice_utils import *

import pandas as pd
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None
        
    def handle(self, *args, **kwargs):
        sendInvoices = SendInvoice.objects.filter()
        incomingInvoices = IncomingInvoice.objects.filter()
        print("Processing...")
        print("Send invocies processing...")
        for sendInvoice in sendInvoices:
            items = sendInvoice.sendinvoiceitem_set.all()
            expenses = sendInvoice.sendinvoiceexpense_set.all()
            send_invoice_price_fix(sendInvoice,items,expenses)
        print("Send invoices done!")
        print("Incoming invocies processing...")
        for incomingInvoice in incomingInvoices:
            items = incomingInvoice.incominginvoiceitem_set.all()
            expenses = incomingInvoice.incominginvoiceexpense_set.all()
            incoming_invoice_price_fix(incomingInvoice, items, expenses)
        print("Incoming invoices done!")
        print("All done!")