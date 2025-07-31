from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa
from django.template.loader import get_template 
import json
from itertools import chain
import xmltodict
import requests as rs
from django.utils import timezone
from datetime import datetime, timedelta

from ..forms import *
from ..tasks import *

from sale.models import Inquiry
from source.models import Bank as SourceBank
from ..utils.payment_utils import payment_invoice_amount_fix,payment_invoice_invoice_fix


def sendAlert(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "send_alert",
            "message": message,
            "location" : location
        }
    )



def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

class PaymentDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Payment")
        elementTag = "payment"
        elementTagSub = "paymentPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/payments.html', context)
    
class PaymentAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Payment")
        elementTag = "payment"
        elementTagSub = "paymentPart"
        elementTagId = "new"
        
        sourceBanks = SourceBank.objects.filter(company = request.user.profile.sourceCompany)
        defaultSourceBank = SourceBank.objects.filter(company = request.user.profile.sourceCompany, currency = 106).first()
        
        form = PaymentForm(request.POST or None, request.FILES or None, user=request.user)

        if is_ajax(request=request):
            term = request.GET.get("term")
            list_type = request.GET.get("type", "")
            
            if list_type == 'company':
                companies = Company.objects.filter(
                    sourceCompany = request.user.profile.sourceCompany
                ).filter(
                    Q(name__icontains = term)
                )
                response_content = list(companies.values("id","name"))
            elif list_type == 'bank':
                banks = SourceBank.objects.filter(
                    company = request.user.profile.sourceCompany
                )

                if term:
                    banks = banks.filter(
                        Q(bankName__icontains=term) |
                        Q(ibanNo__icontains=term) |
                        Q(currency__code__icontains=term)
                    )
                response_content = list(banks.values("id","bankName","ibanNo","currency__code"))
            else:
                response_content = []
            
            return JsonResponse(response_content, safe=False)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "sourceBanks" : sourceBanks,
                "defaultSourceBank" : defaultSourceBank,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/payment_add_new.html', context)
    
    def post(self, request, *args, **kwargs):
        form = PaymentForm(request.POST, request.FILES or None, user=request.user)
        
        if form.is_valid():
            payment = form.save(commit = False)
            payment.sourceCompany = request.user.profile.sourceCompany

            #####hata durumu#####
            if payment.currency.id != payment.sourceBank.currency.id:
                
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Payment curr. and bank curr. must be same!"
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=200)
            elif not payment.type:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Payment type must be selected!"
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=200)
            elif not payment.customer:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Company must be selected!"
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=200)
            elif not payment.sourceBank:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Bank account must be selected!"
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=200)
            elif not payment.paymentDate:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Date must be selected!"
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=200)
            ####hata durumu-end#####
            
            payment.user = request.user
            
            identificationCode = request.user.profile.sourceCompany.accountPaymentCode
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastPayment = Payment.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            if lastPayment:
                lastCode = lastPayment.code
            else:
                lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            payment.code = code
            
            payment.yearCode = yearCode
            
            paymentNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
            payment.paymentNo = paymentNo
            payment.sessionKey = request.session.session_key
            payment.save()

            invoiceJSON = {"sendInvoices" : [], "incomingInvoices" : []}
            payment.invoices = invoiceJSON
            payment.save()
            
            """
            if payment.type == "in":
                #####bank update#####
                sourceBank = payment.sourceBank
                sourceBank.balance = float(sourceBank.balance) + float(payment.amount)
                sourceBank.save()
                #####bank update-end#####
                
                #####invoices#####
                invoices = request.POST.getlist("sendInvoices")
                if len(invoices) > 0:
                    paidPrice = payment.amount
                    paidAmount = 0
                    invoiceJSON = {"sendInvoices" : [], "incomingInvoices" : []}
                    overPaidJSON = {}
                    extraPaidTotal = 0
                    for invoice in invoices:
                        if paidPrice > 0:
                            sendInvoice = SendInvoice.objects.filter(id = invoice).first()
                            paidAmount = paidPrice
                            paidPrice = float(paidPrice) - float((sendInvoice.totalPrice - sendInvoice.paidPrice))
                            if paidPrice >= 0:
                                sendInvoice.paidPrice = sendInvoice.totalPrice
                                sendInvoice.payed = True
                                invoiceJSON["sendInvoices"].append({"invoice" : sendInvoice.id,"paymentAmount" : sendInvoice.paidPrice,"type" : sendInvoice.group})
                            else:
                                #sendInvoice.paidPrice = float(sendInvoice.paidPrice) + float(abs(float(paidPrice) + float(sendInvoice.totalPrice)))
                                sendInvoice.paidPrice = sendInvoice.paidPrice + paidAmount
                                sendInvoice.save()
                                invoiceJSON["sendInvoices"].append({"invoice" : sendInvoice.id,"paymentAmount" : paidAmount,"type" : sendInvoice.group})
                                break
                            sendInvoice.save()
                        
                    payment.invoices = invoiceJSON
                    payment.save()
                    
                    if paidPrice > 0:
                        extraPaidTotal = extraPaidTotal + paidPrice
                    
                    paymentCustomer = payment.customer
                    
                    if paymentCustomer.overPaid[payment.currency.code]:     
                        paymentCustomer.overPaid[payment.currency.code] = paymentCustomer.overPaid[payment.currency.code] + extraPaidTotal
                        
                    # if paidPrice > 0:
                    #     customer = payment.customer
                    #     customer.creditLimit = customer.creditLimit + paidPrice
                    #     customer.save()
                        
                    #current güncelleme
                    sendInvoicess = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,customer = sendInvoice.customer, currency = sendInvoice.currency)
                    sendInvoiceTotal = 0
                    for sendInvoicee in sendInvoicess:
                        sendInvoiceTotal = sendInvoiceTotal + sendInvoicee.totalPrice
                        
                    invoiceTotal = sendInvoiceTotal
                        
                    current = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = sendInvoice.customer, currency = sendInvoice.currency).first()
                    if current:
                        current.credit = current.credit + payment.amount
                        current.save()
                    else:
                        current = Current.objects.create(
                            sourceCompany = request.user.profile.sourceCompany,
                            company = sendInvoice.customer,
                            currency = sendInvoice.currency
                        )
                        current.save()
                        current.credit = current.credit + payment.amount
                        current.save()
                    
                    sendInvoice.customer.debt = sendInvoice.customer.debt - payment.amount
                    sendInvoice.customer.save()
                    #current güncelleme-end
            
                else:
                    paidPrice = payment.amount
                    paidAmount = 0
                    invoiceJSON = {"sendInvoices" : [], "incomingInvoices" : []}
                    
                    payment.invoices = invoiceJSON
                    payment.save()
                    
                    # if paidPrice > 0:
                    #     customer = payment.customer
                    #     customer.creditLimit = customer.creditLimit + paidPrice
                    #     customer.save()
                        
                    #current güncelleme
                    current = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = payment.customer, currency = payment.currency).first()
                    if current:
                        current.credit = current.credit + payment.amount
                        current.save()
                    else:
                        current = Current.objects.create(
                            sourceCompany = request.user.profile.sourceCompany,
                            company = payment.customer,
                            currency = payment.currency
                        )
                        current.save()
                        current.credit = current.credit + payment.amount
                        current.save()
                    #current güncelleme-end
                #####invoices-end#####

            
            elif payment.type == "out":
                sourceBank = payment.sourceBank
                sourceBank.balance = float(sourceBank.balance) - float(payment.amount)
                sourceBank.save()
                
                #####invoices#####
                invoices = request.POST.getlist("incomingInvoices")
                if len(invoices) > 0:
                    paidPrice = payment.amount
                    paidAmount = 0
                    invoiceJSON = {"sendInvoices" : [], "incomingInvoices" : []}
                    for invoice in invoices:
                        incomingInvoice = IncomingInvoice.objects.get(id = invoice)
                        paidAmount = paidPrice
                        paidPrice = float(paidPrice) - float(incomingInvoice.totalPrice)
                        if paidPrice >= 0:
                            incomingInvoice.paidPrice = incomingInvoice.totalPrice
                            incomingInvoice.payed = True
                            invoiceJSON["incomingInvoices"].append({"invoice" : incomingInvoice.id,"paymentAmount" : incomingInvoice.paidPrice,"type" : incomingInvoice.group})
                        else:
                            #sendInvoice.paidPrice = float(sendInvoice.paidPrice) + float(abs(float(paidPrice) + float(sendInvoice.totalPrice)))
                            incomingInvoice.paidPrice = incomingInvoice.paidPrice + paidAmount
                            incomingInvoice.save()
                            invoiceJSON["incomingInvoices"].append({"invoice" : incomingInvoice.id,"paymentAmount" : paidAmount,"type" : incomingInvoice.group})
                            break
                        incomingInvoice.save()
                        
                    payment.invoices = invoiceJSON
                    payment.save()
                        
                    if paidPrice > 0:
                        customer = payment.customer
                        customer.debt = customer.debt + paidPrice
                        customer.save()
                        
                    #current güncelleme
                    incomingInvoices = IncomingInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,seller = incomingInvoice.seller, currency = incomingInvoice.currency)
                    incomingInvoiceTotal = 0
                    for incomingInvoice in incomingInvoices:
                        incomingInvoiceTotal = incomingInvoiceTotal + incomingInvoice.totalPrice
                        
                    invoiceTotal = incomingInvoiceTotal
                        
                    current = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = incomingInvoice.seller, currency = incomingInvoice.currency).first()
                    if current:
                        current.credit = current.credit - payment.amount
                        current.save()
                    else:
                        current = Current.objects.create(
                            sourceCompany = request.user.profile.sourceCompany,
                            company = incomingInvoice.seller,
                            currency = incomingInvoice.currency
                        )
                        current.save()
                        current.credit = current.credit - payment.amount
                        current.save()
                    
                    incomingInvoice.seller.debt = incomingInvoice.seller.debt + payment.amount
                    incomingInvoice.seller.save()
                    #current güncelleme-end
            
                else:
                    paidPrice = payment.amount
                    paidAmount = 0
                    invoiceJSON = {"sendInvoices" : [], "incomingInvoices" : []}
                    
                    payment.invoices = invoiceJSON
                    payment.save()
                    
                    if paidPrice > 0:
                        customer = payment.customer
                        customer.debt = customer.debt + paidPrice
                        customer.save()
                        
                    #current güncelleme
                    current = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = payment.customer, currency = payment.currency).first()
                    if current:
                        current.credit = current.credit - payment.amount
                        current.save()
                    else:
                        current = Current.objects.create(
                            sourceCompany = request.user.profile.sourceCompany,
                            company = payment.customer,
                            currency = payment.currency
                        )
                        current.save()
                        current.credit = current.credit - payment.amount
                        current.save()
                #####invoices-end#####


            
            """
            
            return HttpResponse(status=204)
        else:
            print(form.errors)
            for item in form.errors:
                newDict = dict(form.errors.items())
                
                if item == "paymentDate":
                    data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Enter a valid date."
                        }
            
                    sendAlert(data,"default")
            
            
            return HttpResponse(status=404)
        
class PaymentCurrentAddView(LoginRequiredMixin, View):
    def get(self, request, id, type, *args, **kwargs):
        tag = _("Add Payment Current")
        elementTagSub = "paymentPart"
        
        if type == "in":
            customer = Company.objects.get(id = id)
            theRequests = Request.objects.filter(sourceCompany = request.user.profile.sourceCompany,customer = customer)
            sendInvoices = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,customer = customer, payed = False).order_by("created_date")
            
            sendInvoicesList = []
            mainInvoiceTotal = 0
            for sendInvoice in sendInvoices:
                sendInvoiceParts = SendInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = sendInvoice)
                sendInvoiceExpenses = SendInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = sendInvoice)
                partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
                
                partsTotal = 0
                
                for part in sendInvoiceParts:
                    partsTotal  = partsTotal + part.totalPrice
                    partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
                    partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
                    partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
                    partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
                    partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
                    partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
                for expense in sendInvoiceExpenses:
                    partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
                
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
                
                if sendInvoice.group == "order":
                    if sendInvoice.orderConfirmation.quotation.manuelDiscountAmount > 0:
                        partsTotals["totalDiscount"] = sendInvoice.orderConfirmation.quotation.manuelDiscountAmount
                    else:
                        partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (sendInvoice.orderConfirmation.quotation.manuelDiscount/100)
                elif sendInvoice.group == "service":
                    if sendInvoice.offer.discountAmount > 0:
                        partsTotals["totalDiscount"] = sendInvoice.offer.discountAmount
                    else:
                        partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (sendInvoice.offer.discount/100)
                    
                partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (sendInvoice.vat/100)
                partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
                
                remainingPrice = float(sendInvoice.totalPrice) - float(sendInvoice.paidPrice)
                sendInvoicesList.append({
                    "sendInvoice" : sendInvoice,
                    "total" : float(partsTotals["totalFinal"]),
                    "remainingPrice" : remainingPrice,
                    "type" : "sale"
                })
                
            context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "customer" : customer,
                "theRequests" : theRequests,
                "sendInvoices" : sendInvoices,
                "sendInvoicesList" : sendInvoicesList,
                "mainInvoiceTotal" : mainInvoiceTotal
            }    
        elif type == "out":
            supplier = Company.objects.get(id = id)
            inquiries = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany,supplier = supplier)
            incomingInvoices = IncomingInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,seller = supplier, payed = False)
            
            incomingInvoicesList = []
            mainInvoiceTotal = 0
            for incomingInvoice in incomingInvoices:
                incomingInvoiceParts = IncomingInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = incomingInvoice)
                incomingInvoiceExpenses = IncomingInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = incomingInvoice)
                partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
                
                partsTotal = 0
                
                for part in incomingInvoiceParts:
                    partsTotal  = partsTotal + part.totalPrice
                    partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
                    partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
                    partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
                    partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
                    partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
                    partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
                for expense in incomingInvoiceExpenses:
                    partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
                
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
                if incomingInvoice.purchaseOrder:
                    partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (incomingInvoice.purchaseOrder.discount/100)
                    if incomingInvoice.purchaseOrder.discountAmount > 0:
                        partsTotals["totalDiscount"] = incomingInvoice.purchaseOrder.discountAmount
                    else:
                        partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (incomingInvoice.purchaseOrder.discount/100)
                else:
                    partsTotals["totalDiscount"] = 0
                partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (incomingInvoice.vat/100)
                partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
                
                remainingPrice = float(partsTotals["totalFinal"]) - float(incomingInvoice.paidPrice)
                incomingInvoicesList.append({
                    "incomingInvoice" : incomingInvoice,
                    "total" : float(partsTotals["totalFinal"]),
                    "remainingPrice" : remainingPrice,
                    "type" : "sale"
                })
                
            context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "supplier" : supplier,
                "incomingInvoices" : incomingInvoices,
                "incomingInvoicesList" : incomingInvoicesList,
                "mainInvoiceTotal" : mainInvoiceTotal
            }   
        
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/payment_add_current.html', context)
    
class PaymentUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Payment Detail")
        elementTag = "payment"
        elementTagSub = "paymentPart"
        elementTagId = id

        payment = get_object_or_404(Payment, id = id)

        invoices = payment.paymentinvoice_set.select_related().all()

        if invoices:
            invoiceAmount = sum(invoice.amount for invoice in invoices)
        else:
            invoiceAmount = 0

        creditAmount = payment.amount - invoiceAmount


        """
        if payment.type == "in":
            invoicesTotal = 0
            invoices = {"sendInvoices" : [],"incomingInvoices" : []}
            for invoice in payment.invoices["sendInvoices"]:
                if invoice["type"] == "order":
                    sendInvoice = SendInvoice.objects.filter(id = int(invoice["invoice"])).first()
                    invoicesTotal = invoicesTotal + sendInvoice.totalPrice
                    invoices["sendInvoices"].append({'type': invoice["type"], 'invoice': sendInvoice, 'paymentAmount': invoice["paymentAmount"]})
        
        elif payment.type == "out":
            invoicesTotal = 0
            invoices = {"sendInvoices" : [],"incomingInvoices" : []}
            for invoice in payment.invoices["incomingInvoices"]:
                if invoice["type"] == "order":
                    incomingInvoice = IncomingInvoice.objects.filter(id = int(invoice["invoice"])).first()
                    invoicesTotal = invoicesTotal + incomingInvoice.totalPrice
                    invoices["incomingInvoices"].append({'type': invoice["type"], 'invoice': incomingInvoice, 'paymentAmount': invoice["paymentAmount"]})
        
        """
        
        
        
        
        form = PaymentForm(request.POST or None, request.FILES or None, instance = payment, user=request.user)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "payment" : payment,
                "invoiceAmount" : invoiceAmount,
                "creditAmount" : creditAmount,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        return render(request, 'account/payment_detail_new.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "payment"
        elementTagSub = "paymentPart"
        elementTagId = id

        payment = get_object_or_404(Payment, id = id)
        user = payment.user
        type = payment.type
        customer = payment.customer
        identificationCode = payment.identificationCode
        yearCode = payment.yearCode
        code = payment.code
        paymentNo = payment.paymentNo
        invoices = payment.invoices
        sessionKey = payment.sessionKey
        sourceBank = payment.sourceBank
        sourceCompany = payment.sourceCompany
        
        form = PaymentForm(request.POST, request.FILES or None, instance = payment, user=request.user)
        if form.is_valid():
            payment = form.save(commit = False)
            payment.sourceCompany = sourceCompany
            
            #####hata durumu#####
            if payment.currency.id != payment.sourceBank.currency.id:
                
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Payment curr. and bank curr. must be same!"
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=200)
            elif not payment.type:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Payment type must be selected!"
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=200)
            elif not payment.sourceBank:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Bank account must be selected!"
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=200)
            elif not payment.paymentDate:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Date must be selected!"
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=200)
            ####hata durumu-end#####
            
            payment.user = user
            payment.type = type
            payment.customer = customer
            payment.identificationCode = identificationCode
            payment.yearCode = yearCode
            payment.code = code
            payment.paymentNo = paymentNo
            payment.invoices = invoices
            payment.sessionKey = sessionKey
            payment.save()
            
            """
            if payment.sourceBank != sourceBank:
                sourceBank.balance = sourceBank.balance - payment.amount
                sourceBank.save()
                
                newSourceBank = payment.sourceBank
                newSourceBank.balance = newSourceBank.balance + payment.amount
                newSourceBank.save()

            """

            data = {
                        "block":f"message-container-{elementTag}-{elementTagId}",
                        "icon":"circle-check",
                        "message":"Saved"
                }
            
            sendAlert(data,"form")
            return HttpResponse(status=204)
            
        else:
            data = {
                        "block":f"message-container-{elementTag}-{elementTagId}",
                        "icon":"triangle-exclamation",
                        "message":form.errors
                }
            
            sendAlert(data,"form")
            print(form.errors)
            for item in form.errors:
                
                if item == "paymentDate":
                    data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Enter a valid date."
                        }
            
                    sendAlert(data,"default")
            return HttpResponse(status=404)
        
class PaymentDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Payment")
        
        elementTag = "paymentInvoice"
        elementTagSub = "paymentInvoicePart"
        
        idList = list.split(",")
        
        elementTagId = idList[0]
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/payment_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            payment = get_object_or_404(Payment, id = int(id))
            # sendInvoices = payment.sendInvoices.all()
            # for sendInvoice in sendInvoices:
            #     if sendInvoice.paidPrice < sendInvoice.totalPrice:
            #         sendInvoice.paidPrice
            payment.delete()

            """

            if payment.type == "in":
                items = payment.invoices["sendInvoices"]
                if len(items) > 0:
                    for item in items:
                        try:
                            sendInvoice = SendInvoice.objects.filter(id = item["invoice"]).first()
                        except:
                            sendInvoice = ServiceSendInvoice.objects.filter(id = item["invoice"]).first()
                        if sendInvoice:
                            sendInvoice.paidPrice = sendInvoice.paidPrice - item["paymentAmount"]
                            sendInvoice.payed = False
                            sendInvoice.save()
                            
                            #current güncelleme
                            sendInvoicess = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,customer = sendInvoice.customer, currency = sendInvoice.currency)
                            sendInvoiceTotal = 0
                            for sendInvoicee in sendInvoicess:
                                sendInvoiceTotal = sendInvoiceTotal + (sendInvoicee.totalPrice - sendInvoicee.paidPrice)
                                
                            invoiceTotal = sendInvoiceTotal
                                
                            current = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = sendInvoice.customer, currency = sendInvoice.currency).first()
                            if current:
                                current.credit = current.credit - payment.amount
                                current.save()
                            else:
                                current = Current.objects.create(
                                    sourceCompany = request.user.profile.sourceCompany,
                                    company = sendInvoice.customer,
                                    currency = sendInvoice.currency
                                )
                                current.save()
                                current.credit = current.credit - payment.amount
                                current.save()
                            
                            sendInvoice.customer.debt = sendInvoice.customer.debt + payment.amount
                            sendInvoice.customer.save()
                            #current güncelleme-end
                else:
                    customer = payment.customer
                    customer.creditLimit = customer.creditLimit - payment.amount
                    customer.save()
                    #current güncelleme
                    current = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = payment.customer, currency = payment.currency).first()
                    if current:
                        current.credit = current.credit - payment.amount
                        current.save()
                    else:
                        current = Current.objects.create(
                            sourceCompany = request.user.profile.sourceCompany,
                            company = payment.customer,
                            currency = payment.currency
                        )
                        current.save()
                        current.credit = current.credit - payment.amount
                        current.save()
                    #current güncelleme-end
                    
                sourceBank = payment.sourceBank
                sourceBank.balance = float(sourceBank.balance) - float(payment.amount)
                sourceBank.save()
                
                #process güncelleme
                process = Process.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = payment.customer, payment = payment)
                process.delete()
                #process güncelleme-end
                
                payment.delete()
                
            elif payment.type == "out":
                items = payment.invoices["incomingInvoices"]
                if len(items) > 0:
                    for item in items:
                        incomingInvoice = IncomingInvoice.objects.filter(id = item["invoice"]).first()
                        if incomingInvoice:
                            incomingInvoice.paidPrice = incomingInvoice.paidPrice - item["paymentAmount"]
                            incomingInvoice.payed = False
                            incomingInvoice.save()
                            
                            #current güncelleme
                            sendInvoicess = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,customer = incomingInvoice.seller, currency = incomingInvoice.currency)
                            serviceSendInvoices = ServiceSendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,customer = incomingInvoice.seller, currency = incomingInvoice.currency)
                            incomingInvoices = IncomingInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,seller = incomingInvoice.seller, currency = incomingInvoice.currency)
                            sendInvoiceTotal = 0
                            for sendInvoicee in sendInvoicess:
                                sendInvoiceTotal = sendInvoiceTotal + (sendInvoicee.totalPrice - sendInvoicee.paidPrice)
                            incomingInvoiceTotal = 0
                            for incomingInvoice in incomingInvoices:
                                incomingInvoiceTotal = incomingInvoiceTotal + (incomingInvoice.totalPrice - incomingInvoice.paidPrice)
                    
                            invoiceTotal = sendInvoiceTotal - incomingInvoiceTotal
                                
                            current = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = incomingInvoice.seller, currency = incomingInvoice.currency).first()
                            if current:
                                current.debt = current.debt - payment.amount
                                current.save()
                            else:
                                current = Current.objects.create(
                                    sourceCompany = request.user.profile.sourceCompany,
                                    company = incomingInvoice.seller,
                                    currency = incomingInvoice.currency
                                )
                                current.save()
                                current.debt = current.debt - payment.amount
                                current.save()
                            
                            incomingInvoice.seller.debt = incomingInvoice.seller.debt - payment.amount
                            incomingInvoice.seller.save()
                            #current güncelleme-end
                else:
                    customer = payment.customer
                    customer.debt = customer.debt - payment.amount
                    customer.save()
                    #current güncelleme
                    current = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = payment.customer, currency = payment.currency).first()
                    if current:
                        current.debt = current.debt - payment.amount
                        current.save()
                    else:
                        current = Current.objects.create(
                            sourceCompany = request.user.profile.sourceCompany,
                            company = payment.customer,
                            currency = payment.currency
                        )
                        current.save()
                        current.debt = current.debt - payment.amount
                        current.save()
                    #current güncelleme-end
                    
                sourceBank = payment.sourceBank
                sourceBank.balance = float(sourceBank.balance) + float(payment.amount)
                sourceBank.save()
                
                #process güncelleme
                process = Process.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = payment.customer, payment = payment)
                process.delete()
                #process güncelleme-end
                
                payment.delete()
            
            """
        return HttpResponse(status=204)

class PaymentInvoiceInDetailAddView(LoginRequiredMixin, View):

    def get(self, request, id, *args, **kwargs):
        tag = _("Add Payment Invoice")
        elementTag = "paymentInvoice"
        elementTagSub = "paymentInvoicePart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        paymentId = refererPath.replace("/account/payment_update/","").replace("/","")
        payment = get_object_or_404(Payment, id = id)

        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "payment" : payment
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/payment_invoice_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        paymentId = refererPath.replace("/account/payment_update/","").replace("/","")
        
        payment = Payment.objects.get(id = id)
        paymentInvoices = PaymentInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,payment = payment)
        sequencyCount = len(paymentInvoices)
        
        paymentInvoices = request.POST.getlist("paymentInvoices")
        
        with transaction.atomic():
            for item in paymentInvoices:
                if payment.type == "in":
                    invoice = SendInvoice.objects.get(id = int(item))
                    paymentInvoiceCheck = PaymentInvoice.objects.filter(sendInvoice = invoice, payment = payment)
                    if paymentInvoiceCheck:
                        data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":f"The invoice with number {invoice.sendInvoiceNo} is already included in the payment list. Please remove this invoice from your selection."
                        }
                
                        sendAlert(data,"default")
                        raise ValueError(f"The invoice with number {invoice.sendInvoiceNo} is already included in the payment list. Please remove this invoice from your selection.")
                    newPaymentInvoice = PaymentInvoice.objects.create(
                            sourceCompany = request.user.profile.sourceCompany,
                            user = request.user,
                            payment = payment,
                            type = "send_invoice",
                            sendInvoice = invoice,
                            invoicePaymentDate = invoice.paymentDate
                        )
                elif payment.type == "out":
                    invoice = IncomingInvoice.objects.get(id = int(item))
                    paymentInvoiceCheck = PaymentInvoice.objects.filter(incomingInvoice = invoice, payment = payment)
                    if paymentInvoiceCheck:
                        data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":f"The invoice with number {invoice.incomingInvoiceNo} is already included in the payment list. Please remove this invoice from your selection."
                        }
                
                        sendAlert(data,"default")
                        raise ValueError(f"The invoice with number {invoice.incomingInvoiceNo} is already included in the payment list. Please remove this invoice from your selection.")
                    newPaymentInvoice = PaymentInvoice.objects.create(
                            sourceCompany = request.user.profile.sourceCompany,
                            user = request.user,
                            payment = payment,
                            type = "incoming_invoice",
                            incomingInvoice = invoice,
                            invoicePaymentDate = invoice.paymentDate
                        )
                newPaymentInvoice.save()

                sequencyCount = sequencyCount + 1
        
        #####amount fix#####
        paymentInvoices = payment.paymentinvoice_set.all().order_by("invoicePaymentDate")

        payment_invoice_amount_fix(payment,paymentInvoices,payment.amount)
        #####amount fix-end#####

        data = {
                "block":f"message-container-payment-{id}",
                "icon":"circle-check",
                "message":"Saved"
        }
    
        sendAlert(data,"form")
        
        return HttpResponse(status=204)
 

class PaymentInvoiceAmountView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):

        payment = Payment.objects.get(id = id)

        paymentInvoices = payment.paymentinvoice_set.all().order_by("invoicePaymentDate")

        payment_invoice_amount_fix(payment,paymentInvoices,payment.amount)

        
        
        return HttpResponse(status=204)
    

class PaymentInvoiceDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Payment Invoice")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/request/request_part_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            paymentInvoice = get_object_or_404(PaymentInvoice, id = int(id))
            payment = paymentInvoice.payment

            paymentInvoice.delete()

        

        
        
        
        
        return HttpResponse(status=204)
   