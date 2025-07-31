from django.core.management.base import BaseCommand, CommandError
from sale.models import QuotationPart,Quotation
from account.models import *

from card.models import Current,Company, Currency
from source.models import Bank

from account.utils.payment_utils import *

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
        payments = Payment.objects.select_related("currency").filter()

        for payment in payments:
            print(f"amount: {payment.amount} | curr.: {payment.currency} | invoices: {payment.invoices}")
            sendInvoices = payment.invoices["sendInvoices"]
            incomingInvoices = payment.invoices["incomingInvoices"]

            for sendInvoice in sendInvoices:
                invoice = SendInvoice.objects.filter(id = int(sendInvoice["invoice"])).first()
                paymentInvoice = PaymentInvoice.objects.create(
                    sourceCompany = payment.sourceCompany,
                    user = payment.user,
                    payment = payment,
                    type = "send_invoice",
                    sendInvoice = invoice,
                    invoicePaymentDate = invoice.paymentDate
                )
                paymentInvoice.save()

            for incomingInvoice in incomingInvoices:
                invoice = IncomingInvoice.objects.filter(id = int(incomingInvoice["invoice"])).first()
                paymentInvoice = PaymentInvoice.objects.create(
                    sourceCompany = payment.sourceCompany,
                    user = payment.user,
                    payment = payment,
                    type = "incoming_invoice",
                    incomingInvoice = invoice,
                    invoicePaymentDate = invoice.paymentDate
                )
                paymentInvoice.save()

            #####amount fix#####
            paymentInvoices = payment.paymentinvoice_set.all().order_by("invoicePaymentDate")

            payment_invoice_amount_fix(payment,paymentInvoices,payment.amount)
            #####amount fix-end#####