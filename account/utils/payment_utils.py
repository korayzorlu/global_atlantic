from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .account_utils import *

from decimal import Decimal

def updateDetail(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "update_detail",
            "message": message,
            "location" : location
        }
    )

def company_credit_fix(company):
    payments = company.payment_customer.select_related().all()
    creditTotal = 0
    for payment in payments:
        invoices = payment.paymentinvoice_set.select_related().all()
        if invoices:
            invoiceAmount = sum(invoice.amount for invoice in invoices)
        else:
            invoiceAmount = 0

        creditAmount = Decimal(str(payment.amount)) - Decimal(str(invoiceAmount))
        creditTotal += creditAmount
    
    company.credit = float(creditTotal)
    company.save()

def payment_amount_fix(payment,instance=None):
    paymentInvoices = payment.paymentinvoice_set.all()
    if paymentInvoices:
        if instance:
            invoiceAmount = sum(invoice.amount for invoice in paymentInvoices) + instance.amount
        else:
            invoiceAmount = sum(invoice.amount for invoice in paymentInvoices)
    else:
        invoiceAmount = 0
    creditAmount = payment.amount - invoiceAmount
    
    data = {
            "payment":payment.id,
            "invoiceAmount":invoiceAmount,
            "creditAmount":creditAmount,
            "totalAmount":payment.amount,
            "currency":payment.currency.symbol
    }
    updateDetail(data,"payment_update")

def payment_invoice_invoice_fix(invoice,payment,excludeId=None):
    invoice.paidPrice = 0

    if payment.type == "in":
        if excludeId:
            paymentInvoices = invoice.payment_invoice_send_invoice.all().exclude(id = excludeId)
        else:
            paymentInvoices = invoice.payment_invoice_send_invoice.all()
    elif payment.type == "out":
        if excludeId:
            paymentInvoices = invoice.payment_invoice_incoming_invoice.all().exclude(id = excludeId)
        else:
            paymentInvoices = invoice.payment_invoice_incoming_invoice.all()


    invoice.paidPrice = sum(paymentInvoice.invoiceCurrencyAmount for paymentInvoice in paymentInvoices)
    
    invoice.save()

    if (invoice.totalPrice - invoice.paidPrice) <= 0:
        invoice.payed = True
        invoice.save()
    else:
        invoice.payed = False
        invoice.save()


def payment_invoice_amount_fix(payment, paymentInvoices, remainingAmount, instance=None):
    paymentInvoices.update(amount = 0,invoiceCurrencyAmount = 0)
    if payment.type == "in":
        for paymentInvoice in paymentInvoices:
            payment_invoice_invoice_fix(paymentInvoice.sendInvoice,payment,excludeId=paymentInvoice.id)
            invoiceRemainingAmount = convert_currency((paymentInvoice.sendInvoice.totalPrice - paymentInvoice.sendInvoice.paidPrice),paymentInvoice.sendInvoice.currency.forexBuying,payment.currency.forexBuying)
            if remainingAmount == 0:
                break
            if remainingAmount >= invoiceRemainingAmount:
                # Fatura tamamen ödeniyor
                remainingAmount -= invoiceRemainingAmount
                paymentInvoice.amount = invoiceRemainingAmount
                #paymentInvoice.sendInvoice.paid = True
            else:
                # Fatura kısmen ödeniyor, işlem burada duracak
                paymentInvoice.amount = remainingAmount
                remainingAmount = 0
            
            paymentInvoice.invoiceCurrencyAmount = convert_currency(paymentInvoice.amount,payment.currency.forexBuying,paymentInvoice.sendInvoice.currency.forexBuying)
            paymentInvoice.save()

            payment_invoice_invoice_fix(paymentInvoice.sendInvoice,payment)


    elif payment.type == "out":
        for paymentInvoice in paymentInvoices:
            payment_invoice_invoice_fix(paymentInvoice.incomingInvoice,payment,excludeId=paymentInvoice.id)
            invoiceRemainingAmount = convert_currency((paymentInvoice.incomingInvoice.totalPrice - paymentInvoice.incomingInvoice.paidPrice),paymentInvoice.incomingInvoice.currency.forexBuying,payment.currency.forexBuying)
            if remainingAmount == 0:
                break
            if remainingAmount >= invoiceRemainingAmount:
                # Fatura tamamen ödeniyor
                remainingAmount -= invoiceRemainingAmount
                paymentInvoice.amount = invoiceRemainingAmount
                #paymentInvoice.incomingInvoice.paid = True
            else:
                # Fatura kısmen ödeniyor, işlem burada duracak
                paymentInvoice.amount = remainingAmount
                remainingAmount = 0

            paymentInvoice.invoiceCurrencyAmount = convert_currency(paymentInvoice.amount,payment.currency.forexBuying,paymentInvoice.incomingInvoice.currency.forexBuying)
            paymentInvoice.save()

            payment_invoice_invoice_fix(paymentInvoice.incomingInvoice,payment)



    





    