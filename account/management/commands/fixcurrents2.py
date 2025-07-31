from django.core.management.base import BaseCommand, CommandError
from sale.models import QuotationPart,Quotation
from account.models import ProformaInvoicePart, SendInvoicePart, ProformaInvoice, SendInvoice,Payment, IncomingInvoice, Process

from card.models import Current,Company, Currency
from source.models import Bank

from account.utils.send_invoice_utils import *
from account.utils.incoming_invoice_utils import *
from account.utils.current_utils import *
from account.utils.payment_utils import *
from account.utils.process_utils import *


import pandas as pd
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None

    def add_arguments(self, parser):
        parser.add_argument('company', type=int, help='Company Id')

    def handle(self, *args, **kwargs):
        app = kwargs['company']

        if app == 0:
            companies = Company.objects.select_related().filter()
        else:
            companies = Company.objects.select_related().filter(id = app)

        for company in companies:
            company.debt = 0
            company.credit = 0

            sendInvoices = company.send_invoice_customer.select_related().all()
            incomingInvoices = company.incoming_invoice_seller.select_related().all()
            payments = company.payment_customer.select_related().all()
            theCompanyCurrencies = []

            for sendInvoice in sendInvoices:
                items = sendInvoice.sendinvoiceitem_set.select_related().all()
                expenses = sendInvoice.sendinvoiceexpense_set.select_related().all()
                send_invoice_price_fix(sendInvoice,items,expenses)
                process_update(sendInvoice)
                theCompanyCurrencies.append(sendInvoice.currency)

            for incomingInvoice in incomingInvoices:
                items = incomingInvoice.incominginvoiceitem_set.select_related().all()
                expenses = incomingInvoice.incominginvoiceexpense_set.select_related().all()
                incoming_invoice_price_fix(incomingInvoice,items,expenses)
                process_update(incomingInvoice)
                theCompanyCurrencies.append(incomingInvoice.currency)

            for payment in payments:
                process_update(payment)

            theCompanyCurrencies = list(set(theCompanyCurrencies))

            for currency in theCompanyCurrencies:
                current_fix(company,currency)

            company_credit_fix(company)

