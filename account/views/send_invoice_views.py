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
from ..pdfs.send_invoice_pdfs import *
from ..utils.payment_utils import *
from ..utils.current_utils import *
from ..utils.send_invoice_utils import *

from sale.models import OrderTracking, OrderConfirmation, Collection, CollectionPart, Delivery,Inquiry,QuotationExtra
from source.models import Company as SourceCompany
from source.models import Bank as SourceBank
from service.models import Offer
from card.models import Current
from data.models import Part

from administration.forms import CompanySendInvoicePdfHtmlForm

import random
import string
import pandas as pd
from decimal import Decimal

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

class SendInvoiceDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Send Invoice")
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"

        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/send_invoice/send_invoices.html', context)

class SendInvoiceAddView(LoginRequiredMixin, View):
    def get(self, request, id, type, *args, **kwargs):
        tag = _("Add Send Invoice")
        
        elementTag = "sendInvoiceAdd"
        elementTagSub = "sendInvoicePartInAdd"
        elementTagId = id
        
        if type == "order":
            model = get_object_or_404(OrderConfirmation, id = id)
            invoiceType = "order"
        elif type == "service":
            model = get_object_or_404(Offer, id = id)
            invoiceType = "service"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "model" : model,
                "invoiceType" : invoiceType
        }
        return render(request, 'account/send_invoice/send_invoice_add.html', context)
    
    def post(self, request, id, type, *args, **kwargs):
        elementTag = "sendInvoiceAdd"
        elementTagSub = "sendInvoicePartInAdd"
        elementTagId = id

        if type == "order":
            orderConfirmation = get_object_or_404(OrderConfirmation, id = id)
            purchaseOrders = PurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderConfirmation = orderConfirmation)
            
            quotation = orderConfirmation.quotation
            project = orderConfirmation.project
            theRequest = Request.objects.get(project = project)
            orderTracking = OrderTracking.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = theRequest).first()
            delivery = Delivery.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking).first()
            
            parts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation).order_by("sequency")
            expenses = QuotationExtra.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation).order_by("id")
            
            if theRequest.vessel:
                billing = Billing.objects.filter(sourceCompany = request.user.profile.sourceCompany,vessel = theRequest.vessel).first()
            else:
                billing = None
            sendInvoice = SendInvoice.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                user = request.user,
                project = orderConfirmation.project,
                theRequest = quotation.inquiry.theRequest,
                orderConfirmation = orderConfirmation,
                seller = SourceCompany.objects.get(id = request.user.profile.sourceCompany.id),
                customer = orderConfirmation.quotation.inquiry.theRequest.customer,
                vessel = orderConfirmation.quotation.inquiry.theRequest.vessel,
                billing = billing,
                awb = delivery.trackingNo,
                exchangeRate = quotation.currency.forexBuying,
                currency = quotation.currency,
                group = "order"
            )
            
            identificationCode = request.user.profile.sourceCompany.accountSendInvoiceCode
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastSendInvoice = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            lastServiceSendInvoice = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            if lastSendInvoice:
                if lastServiceSendInvoice:
                    if lastSendInvoice.code >= lastServiceSendInvoice.code:
                        lastCode = lastSendInvoice.code
                    else:
                        lastCode = lastServiceSendInvoice.code
                else:
                    lastCode = lastSendInvoice.code
            else:
                if lastServiceSendInvoice:
                    lastCode = lastServiceSendInvoice.code
                else:
                    lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            sendInvoice.code = code
            
            sendInvoice.yearCode = yearCode
            
            sendInvoiceNoSys = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
            sendInvoice.sendInvoiceNoSys = sendInvoiceNoSys
            
            sendInvoice.paymentDate = timezone.now() + timedelta(days=sendInvoice.customer.creditPeriod)
            sendInvoice.save()
            
            for part in parts:
                sendInvoicePart = SendInvoiceItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    invoice = sendInvoice,
                    quotationPart = part,
                    part = part.inquiryPart.requestPart.part,
                    name = part.inquiryPart.requestPart.part.partNo,
                    description = part.inquiryPart.requestPart.part.description,
                    unit = part.inquiryPart.requestPart.part.unit,
                    quantity = part.quantity,
                    unitPrice = part.unitPrice3,
                    totalPrice = part.totalPrice3
                )
                sendInvoicePart.save()
                
            for expense in expenses:
                sendInvoicePart = SendInvoiceItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    invoice = sendInvoice,
                    quotationExpense = expense,
                    description = expense.description,
                    unit = expense.unit,
                    quantity = expense.quantity,
                    unitPrice = expense.unitPrice,
                    totalPrice = expense.totalPrice
                )
                sendInvoicePart.save()

            sendInvoiceParts = SendInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = sendInvoice).order_by("id")
            sequencyCount = 0
            for sendInvoicePart in sendInvoiceParts:
                sendInvoicePart.sequency = sequencyCount + 1
                sendInvoicePart.save()
                sequencyCount = sequencyCount + 1

            items = sendInvoice.sendinvoiceitem_set.all()
            expenses = sendInvoice.sendinvoiceexpense_set.all()

            send_invoice_price_fix(sendInvoice,items,expenses)

            
            #####proje fatura durum kontrolü#####
            orderTracking = OrderTracking.objects.get(project = orderConfirmation.project)
            
            incomingInvoiceCheckList = []
            for purchaseOrder in purchaseOrders:
                incomingInvoiceCheckList.append(purchaseOrder.incomingInvoiced)
            #if all(value for value in incomingInvoiceCheckList):
            orderConfirmation.status = "invoiced"
            orderTracking.invoiced = True
            orderTracking.save()
            project = orderConfirmation.project
            project.stage = "invoiced"
            project.save()
            
            orderConfirmation.invoiced = True
            orderConfirmation.sendInvoiced = True
            orderConfirmation.save()
            #####proje fatura durum kontrolü-end#####

            sendInvoicePdfTask.delay(request.user.profile.sourceCompany.id, sendInvoice.id,request.build_absolute_uri(),elementTag)
            
            return HttpResponse(status=204)
        elif type == "service":
            offer = get_object_or_404(Offer, id = id)
            
            parts = OfferServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = offer).order_by("id")
            materials = OfferPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = offer).order_by("id")
            offerExpenses = OfferExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = offer).order_by("id")
            
            billing = Billing.objects.filter(sourceCompany = request.user.profile.sourceCompany,vessel = offer.vessel).first()
            sendInvoice = SendInvoice.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                user = request.user,
                offer = offer,
                seller = SourceCompany.objects.get(id = request.user.profile.sourceCompany.id),
                customer = offer.customer,
                vessel = offer.vessel,
                billing = billing,
                exchangeRate = offer.currency.forexBuying,
                currency = offer.currency,
                group = "service"
            )
            
            identificationCode = request.user.profile.sourceCompany.accountSendInvoiceCode
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastSendInvoice = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            lastServiceSendInvoice = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            if lastSendInvoice:
                if lastServiceSendInvoice:
                    if lastSendInvoice.code >= lastServiceSendInvoice.code:
                        lastCode = lastSendInvoice.code
                    else:
                        lastCode = lastServiceSendInvoice.code
                else:
                    lastCode = lastSendInvoice.code
            else:
                if lastServiceSendInvoice:
                    lastCode = lastServiceSendInvoice.code
                else:
                    lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            sendInvoice.code = code
            
            sendInvoice.yearCode = yearCode
            
            sendInvoiceNoSys = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
            sendInvoice.sendInvoiceNoSys = sendInvoiceNoSys
            
            sendInvoice.paymentDate = timezone.now() + timedelta(days=sendInvoice.customer.creditPeriod)
            sendInvoice.save()
            
            for part in parts:
                sendInvoicePart = SendInvoiceItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    invoice = sendInvoice,
                    offerServiceCard = part,
                    serviceCard = part.serviceCard,
                    name = part.serviceCard.code,
                    description = part.serviceCard.name,
                    remark = part.serviceCard.about,
                    unit = part.serviceCard.unit,
                    quantity = part.quantity,
                    unitPrice = part.unitPrice3,
                    totalPrice = part.totalPrice
                )
                sendInvoicePart.save()
                
            for material in materials:
                sendInvoiceMaterial = SendInvoiceItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    invoice = sendInvoice,
                    offerPart = material,
                    part = material.part,
                    name = material.part.partNo,
                    description = material.part.description,
                    unit = material.part.unit,
                    quantity = material.quantity,
                    unitPrice = material.unitPrice,
                    totalPrice = material.totalPrice
                )
                sendInvoiceMaterial.save()
                
            for offerExpense in offerExpenses:
                sendInvoiceExpense = SendInvoiceItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    invoice = sendInvoice,
                    offerExpense = offerExpense,
                    expense = offerExpense.expense,
                    name = offerExpense.expense.code,
                    description = offerExpense.expense.name,
                    unit = offerExpense.expense.unit,
                    quantity = offerExpense.quantity,
                    unitPrice = offerExpense.unitPrice,
                    totalPrice = offerExpense.totalPrice
                )
                sendInvoiceExpense.save()
            
            sendInvoiceParts = SendInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = sendInvoice).order_by("id")
            sequencyCount = 0
            for sendInvoicePart in sendInvoiceParts:
                sendInvoicePart.sequency = sequencyCount + 1
                sendInvoicePart.save()
                sequencyCount = sequencyCount + 1

            items = sendInvoice.sendinvoiceitem_set.all()
            expenses = sendInvoice.sendinvoiceexpense_set.all()

            send_invoice_price_fix(sendInvoice,items,expenses)
            

            
            #####proje fatura durum kontrolü#####

            
            offer.invoiced = True
            offer.sendInvoiced = True
            offer.save()
            #####proje fatura durum kontrolü-end#####
            
            
            sendInvoicePdfTask.delay(request.user.profile.sourceCompany.id, sendInvoice.id,request.build_absolute_uri(),elementTag)
            
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=404)


class SendInvoiceUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Send Invoice Detail")
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"
        elementTagId = id
        
        sendInvoices = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        sendInvoice = get_object_or_404(SendInvoice, id = id)
        
        if sendInvoice.group == "order":
        
            #print(sendInvoice.sendInvoiceDate + timedelta(days=30))
            
            parts = SendInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = sendInvoice)
            expenses = SendInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = sendInvoice)
            partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
            
            sendInvoicePartList = []
            
            partsTotal = 0
            
            for part in parts:
                sendInvoicePartList.append(part.id)
                
                partsTotal  = partsTotal + part.totalPrice
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
            
            if sendInvoice.orderConfirmation.quotation.manuelDiscountAmount > 0:
                partsTotals["totalDiscount"] = sendInvoice.orderConfirmation.quotation.manuelDiscountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (sendInvoice.orderConfirmation.quotation.manuelDiscount/100)
            
            for expense in expenses:
                partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
            
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
            partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (sendInvoice.vat/100)
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
            
            remainingPrice = float(partsTotals["totalFinal"]) - float(sendInvoice.paidPrice)
            
            # Para miktarını belirtilen formatta gösterme
            partsTotals["totalTotalPrice3"] = "{:,.2f}".format(round(partsTotals["totalTotalPrice3"],2))
            partsTotals["totalDiscount"] = "{:,.2f}".format(round(partsTotals["totalDiscount"],2))
            partsTotals["totalVat"] = "{:,.2f}".format(round(partsTotals["totalVat"],2))
            partsTotals["totalFinal"] = "{:,.2f}".format(round(partsTotals["totalFinal"],2))
            remainingPrice = "{:,.2f}".format(round(remainingPrice,2))
            # Nokta ile virgülü değiştirme
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
            partsTotals["totalDiscount"] = partsTotals["totalDiscount"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
            partsTotals["totalVat"] = partsTotals["totalVat"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
            partsTotals["totalFinal"] = partsTotals["totalFinal"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
            remainingPrice = remainingPrice.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            sendInvoiceBalance = Decimal(str(sendInvoice.totalPrice)) - Decimal(str(sendInvoice.paidPrice))

            form = SendInvoiceForm(request.POST or None, request.FILES or None, instance = sendInvoice, user=request.user)
            
            context = {
                    "tag": tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "elementTagId" : elementTagId,
                    "form" : form,
                    "sendInvoices" : sendInvoices,
                    "sendInvoice" : sendInvoice,
                    "partsTotals" : partsTotals,
                    "parts" : parts,
                    "sendInvoicePartList" : sendInvoicePartList,
                    "remainingPrice" : remainingPrice,
                    "sendInvoiceBalance" : sendInvoiceBalance,
                    "sessionKey" : request.session.session_key,
                    "user" : request.user
            }
        elif sendInvoice.group == "service":
            
            parts = SendInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = sendInvoice)
            expenses = SendInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = sendInvoice)
            partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
            
            sendInvoicePartList = []
            
            partsTotal = 0
            
            for part in parts:
                sendInvoicePartList.append(part.id)
                
                partsTotal  = partsTotal + part.totalPrice
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
            
            if sendInvoice.offer.discountAmount > 0:
                partsTotals["totalDiscount"] = sendInvoice.offer.discountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (sendInvoice.offer.discount/100)
            
            for expense in expenses:
                partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
            
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
            partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (sendInvoice.vat/100)
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
            
            remainingPrice = float(partsTotals["totalFinal"]) - float(sendInvoice.paidPrice)
            
            # Para miktarını belirtilen formatta gösterme
            partsTotals["totalTotalPrice3"] = "{:,.2f}".format(round(partsTotals["totalTotalPrice3"],2))
            partsTotals["totalDiscount"] = "{:,.2f}".format(round(partsTotals["totalDiscount"],2))
            partsTotals["totalVat"] = "{:,.2f}".format(round(partsTotals["totalVat"],2))
            partsTotals["totalFinal"] = "{:,.2f}".format(round(partsTotals["totalFinal"],2))
            remainingPrice = "{:,.2f}".format(round(remainingPrice,2))
            # Nokta ile virgülü değiştirme
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
            partsTotals["totalDiscount"] = partsTotals["totalDiscount"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
            partsTotals["totalVat"] = partsTotals["totalVat"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
            partsTotals["totalFinal"] = partsTotals["totalFinal"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
            remainingPrice = remainingPrice.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            sendInvoiceBalance = Decimal(str(sendInvoice.totalPrice)) - Decimal(str(sendInvoice.paidPrice))
            
            form = SendInvoiceForm(request.POST or None, request.FILES or None, instance = sendInvoice, user=request.user)
            
            context = {
                    "tag": tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "elementTagId" : elementTagId,
                    "form" : form,
                    "sendInvoices" : sendInvoices,
                    "sendInvoice" : sendInvoice,
                    "partsTotals" : partsTotals,
                    "parts" : parts,
                    "sendInvoicePartList" : sendInvoicePartList,
                    "remainingPrice" : remainingPrice,
                    "sendInvoiceBalance" : sendInvoiceBalance,
                    "sessionKey" : request.session.session_key,
                    "user" : request.user
            }
        
        return render(request, 'account/send_invoice/send_invoice_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"
        elementTagId = id

        data = {
            "block":f"message-container-{elementTag}-{elementTagId}",
            "icon":"",
            "message":"Updating invoice...",
            "stage" : "loading",
            "buttons": f"tabPane-{elementTag}-{elementTagId} .modal-header .tableTopButtons"
        }
            
        sendAlert(data,"form")

        sendInvoice = get_object_or_404(SendInvoice, id = id)
        
        process = Process.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = sendInvoice.customer, sendInvoice = sendInvoice).first()
        
        user = sendInvoice.user
        project = sendInvoice.project
        theRequest = sendInvoice.theRequest
        orderConfirmation = sendInvoice.orderConfirmation
        offer = sendInvoice.offer
        seller = sendInvoice.seller
        identificationCode = sendInvoice.identificationCode
        code = sendInvoice.code
        yearCode = sendInvoice.yearCode
        sendInvoiceNoSys = sendInvoice.sendInvoiceNoSys
        group = sendInvoice.group
        sourceCompany = sendInvoice.sourceCompany
        #parts = SendInvoicePart.objects.filter(invoice = sendInvoice)
        
        form = SendInvoiceForm(request.POST, request.FILES or None, instance = sendInvoice, user=request.user)
        
        vessel = request.POST.getlist("vessel")[0]
        if vessel:
            form.fields['billing'].queryset = Billing.objects.filter(vessel=int(vessel))
        else:
            form.fields['billing'].queryset = Billing.objects.none()

        if form.is_valid():
            if not request.POST.get("exchangeRate"):
                data = {'message': 'Please fill out the "Exchange Rate" field.'}
                return JsonResponse(data, status=404)
            sendInvoice = form.save(commit = False)
            sendInvoice.sourceCompany = sourceCompany
            sendInvoice.user = user
            sendInvoice.project = project
            sendInvoice.orderConfirmation = orderConfirmation
            sendInvoice.theRequest = theRequest
            sendInvoice.offer = offer
            sendInvoice.seller = seller
            sendInvoice.identificationCode = identificationCode
            sendInvoice.code = code
            sendInvoice.yearCode = yearCode
            sendInvoice.sendInvoiceNoSys = sendInvoiceNoSys
            sendInvoice.group = group
            sendInvoice.paymentDate = sendInvoice.sendInvoiceDate + timedelta(days=sendInvoice.customer.creditPeriod)
            sendInvoice.save()

            items = sendInvoice.sendinvoiceitem_set.all()
            expenses = sendInvoice.sendinvoiceexpense_set.all()

            send_invoice_price_fix(sendInvoice,items,expenses)
            
            #current güncelleme
            sendInvoicess = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,customer = sendInvoice.customer, currency = sendInvoice.currency)
            incomingInvoices = IncomingInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,seller = sendInvoice.customer, currency = sendInvoice.currency)
            sendInvoiceTotal = 0
            for sendInvoicee in sendInvoicess:
                sendInvoiceTotal = sendInvoiceTotal + (sendInvoice.totalPrice - sendInvoice.paidPrice)
            incomingInvoiceTotal = 0
            for incomingInvoice in incomingInvoices:
                incomingInvoiceTotal = incomingInvoiceTotal + (incomingInvoice.totalPrice - incomingInvoice.paidPrice)
    
            invoiceTotal = sendInvoiceTotal - incomingInvoiceTotal
                
            current = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = sendInvoice.customer, currency = sendInvoice.currency).first()
            if current:
                current.debt = invoiceTotal
                current.save()
            else:
                current = Current.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    company = sendInvoice.customer,
                    currency = sendInvoice.currency
                )
                current.save()
                current.debt = invoiceTotal
                current.save()
            
            sendInvoice.customer.debt = invoiceTotal
            sendInvoice.customer.save()
            
            #current güncelleme-end

            
            #sendInvoicePdf(theRequest, orderConfirmation, offer, sendInvoice, delivery, request.user.profile.sourceCompany)

            sendInvoicePdfTask.delay(request.user.profile.sourceCompany.id, sendInvoice.id,request.build_absolute_uri(),elementTag)
            
            
            return HttpResponse(status=204)
            
        else:
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"triangle-exclamation",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)

class SendInvoicePdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Order Confirmation PDF")
        
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"
        elementTagId = str(id) + "-pdf"
        
        sendInvoice = get_object_or_404(SendInvoice, id = id)
        orderConfirmation = sendInvoice.orderConfirmation
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #orderConfirmationPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "sendInvoice" : sendInvoice,
                "orderConfirmation" : orderConfirmation,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/send_invoice/send_invoice_pdf.html', context)

class SendInvoicePdfInOTView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Send Invoice PDF")
        
        elementTag = "orderTracking"
        elementTagSub = "orderTrackingPart"
        elementTagId = str(id) + "-pdf"
        
        sendInvoice = get_object_or_404(SendInvoice, id = id)
        orderConfirmation = sendInvoice.orderConfirmation
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #orderConfirmationPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "sendInvoice" : sendInvoice,
                "orderConfirmation" : orderConfirmation,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/send_invoice/send_invoice_pdf.html', context)

class SendInvoicePartCurrencyUpdateView(LoginRequiredMixin, View):
    def post(self, request, id, cid, *args, **kwargs):
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"
        elementTagId = id

        sendInvoice = SendInvoice.objects.filter(id = id).first()

        if sendInvoice.paidPrice > 0:
            data = {
                    "status":"secondary",
                    "icon":"triangle-exclamation",
                    "message":"You cannot change the currency, there is a payment attached to this invoice."
            }
        
            sendAlert(data,"default")
            return HttpResponse(status=404)
        
        oldCurrency = sendInvoice.currency
        newCurrency = Currency.objects.filter(id = cid).first()

        items = sendInvoice.sendinvoiceitem_set.all()
        expenses = sendInvoice.sendinvoiceexpense_set.all()
        print(sendInvoice.exchangeRate)
        for item in items:
            unitPrice = convert_currency(item.unitPrice,sendInvoice.exchangeRate,newCurrency.forexBuying)
            totalPrice = float(unitPrice) * float(item.quantity)
            item.unitPrice = unitPrice
            item.totalPrice = totalPrice
            item.save()
            
        for expense in expenses:
            unitPrice = convert_currency(expense.unitPrice,sendInvoice.exchangeRate,newCurrency.forexBuying)
            totalPrice = float(unitPrice) * float(expense.quantity)
            expense.unitPrice = unitPrice
            expense.totalPrice = totalPrice
            expense.save()
        
        sendInvoice.currency = newCurrency
        sendInvoice.exchangeRate = newCurrency.forexBuying
        sendInvoice.save()

        items = sendInvoice.sendinvoiceitem_set.all()
        expenses = sendInvoice.sendinvoiceexpense_set.all()

        send_invoice_price_fix(sendInvoice,items,expenses)

        sendInvoicePdfTask.delay(request.user.profile.sourceCompany.id, sendInvoice.id,request.build_absolute_uri(),elementTag)
            
        return HttpResponse(status=204)

class SendInvoicePartDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Send Invoice")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/send_invoice/send_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"
        elementTagId = id

        idList = list.split(",")
        for id in idList:
            sendInvoicePart = get_object_or_404(SendInvoiceItem, id = int(id))
            invoice = sendInvoicePart.invoice
            sendInvoicePart.delete()

        items = invoice.sendinvoiceitem_set.all()
        expenses = invoice.sendinvoiceexpense_set.all()
        send_invoice_price_fix(invoice, items, expenses)

        sendInvoicePdfTask.delay(request.user.profile.sourceCompany.id, invoice.id,request.build_absolute_uri(),elementTag)

        return HttpResponse(status=204)

class SendInvoiceExpenseInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Send Invoice Expense ")
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        invoiceId = refererPath.replace("/account/send_invoice_update/","").replace("/","")
        invoice = get_object_or_404(SendInvoice, id = id)
        
        form = SendInvoiceExpenseForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "invoice" : invoice,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/send_invoice/send_invoice_expense_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"
        elementTagId = id

        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        invoiceId = refererPath.replace("/account/send_invoice_update/","").replace("/","")
        
        invoice = SendInvoice.objects.get(id = id)
        sendInvoiceExpenses = SendInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = invoice)
        
        form = SendInvoiceExpenseForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            sendInvoiceExpense = form.save(commit = False)
            sendInvoiceExpense.sourceCompany = request.user.profile.sourceCompany
            
            sendInvoiceExpense.user = request.user
            sendInvoiceExpense.invoice = invoice
            sendInvoiceExpense.save()

            sendInvoicePdfTask.delay(request.user.profile.sourceCompany.id, invoice.id,request.build_absolute_uri(),elementTag)
            
            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)

class SendInvoiceExpenseDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Send Invoice")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/send_invoice/send_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"

        idList = list.split(",")
        for id in idList:
            sendInvoiceExpense = get_object_or_404(SendInvoiceExpense, id = int(id))
            invoice = sendInvoiceExpense.invoice
            
            invoice = sendInvoiceExpense.invoice
            
            sendInvoiceExpense.delete()

            sendInvoicePdfTask.delay(request.user.profile.sourceCompany.id, invoice.id,request.build_absolute_uri(),elementTag)
        
        items = invoice.sendinvoiceitem_set.all()
        expenses = invoice.sendinvoiceexpense_set.all()
        send_invoice_price_fix(invoice, items, expenses)
        
        return HttpResponse(status=204)

class SendInvoiceDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Invoice")
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"
        
        idList = list.split(",")
        #ypeList = types.split(",")
        
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
        
        return render(request, 'account/send_invoice/send_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        #typeList = types.split(",")
        #combinedList = [{"id": idList_item, "type": typeList_item} for idList_item, typeList_item in zip(idList, typeList)]
        for id in idList:
            sendInvoice = get_object_or_404(SendInvoice, id = int(id))
            if sendInvoice.paidPrice > 0:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"There is a payment attached to this invoice."
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=404)
            else:
                if sendInvoice.group == "order":
                    orderConfirmation = sendInvoice.orderConfirmation
                    orderConfirmation.sendInvoiced = False
                    orderConfirmation.save()
                    
                    #####proje fatura durum kontrolü#####
                    orderTracking = OrderTracking.objects.get(project = orderConfirmation.project)
                    purchaseOrders = PurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderConfirmation = orderConfirmation)
                    incomingInvoiceCheckList = []
                    for purchaseOrder in purchaseOrders:
                        incomingInvoiceCheckList.append(purchaseOrder.incomingInvoiced)
                    orderTracking.invoiced = False
                    orderTracking.save()
                    
                    orderConfirmation.status = "collected"
                    orderConfirmation.invoiced = False
                    orderConfirmation.sendInvoiced = False
                    orderConfirmation.save()
                    project = orderConfirmation.project
                    project.stage = "order_tracking"
                    project.save()
                elif sendInvoice.group == "service":
                    offer = sendInvoice.offer
                    offer.invoiced == False
                    offer.sendInvoiced = False
                    offer.save()
                

                

                
                sendInvoice.delete()
                return HttpResponse(status=204)
            
class SendInvoiceFilterExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Send Invoice Excel")
        
        elementTag = "sendInvoiceExcel"
        elementTagSub = "sendInvoicePartExcel"
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "sessionKey" : request.session.session_key
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/send_invoice/send_invoice_excel.html', context)       

class SendInvoiceExportExcelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "account", "send_invoice", "documents")
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        
        if request.GET.get("start") == "":
            startDate = "01/01/2024"
        else:
            startDate = datetime.strptime(request.GET.get("start"), "%d/%m/%Y").date()
            
        if request.GET.get("end") == "":
            endDate = datetime.today().date().strftime('%d/%m/%Y')
        else:
            endDate = datetime.strptime(request.GET.get("end"), "%d/%m/%Y").date()
        
        sendInvoiceExcludeTypes = []
        
        if request.GET.get("o") == "false":
            sendInvoiceExcludeTypes.append("order")
            
        if request.GET.get("s") == "false":
            sendInvoiceExcludeTypes.append("service")
        
        customers = request.GET.get("c")
        
        if request.GET.get("p") == "true":
            sendInvoices = SendInvoice.objects.select_related("customer").exclude(group__in=sendInvoiceExcludeTypes).filter(
                sourceCompany = request.user.profile.sourceCompany,
                payed=True,sendInvoiceDate__range=(startDate,endDate)
            ).order_by("sendInvoiceDate").distinct()
        elif request.GET.get("np") == "true":
            sendInvoices = SendInvoice.objects.select_related("customer").exclude(group__in=sendInvoiceExcludeTypes).filter(
                sourceCompany = request.user.profile.sourceCompany,
                payed=False,sendInvoiceDate__range=(startDate,endDate)
            ).order_by("sendInvoiceDate").distinct()
        else:
            sendInvoices = SendInvoice.objects.select_related("customer").exclude(group__in=sendInvoiceExcludeTypes).filter(
                sourceCompany = request.user.profile.sourceCompany,
                sendInvoiceDate__range=(startDate,endDate)
            ).order_by("sendInvoiceDate")
        
        if customers:
            customers = customers.split(",")
            sendInvoices = sendInvoices.filter(sourceCompany = request.user.profile.sourceCompany,customer__id__in=customers).order_by("customer__name")
        
        
        data = {
            "Line": [],
            "Project No": [],
            "Group": [],
            "Customer": [],
            "Vessel": [],
            "Billing Name": [],
            "Invoice Date": [],
            "Invoice No": [],
            "Payment Date": [],
            "Net Amount": [],
            "Discount": [],
            "Vat": [],
            "Gross Amount": [],
            "Currency": [],
            "Exchange Rate": [],
            "TRY Gross": [],
            "Paid": []
        }
        
        channel_layer = get_channel_layer()
        
        seq = 0
        for sendInvoice in sendInvoices:
            async_to_sync(channel_layer.group_send)(
                'private_' + str(request.user.id),
                {
                    "type": "send_percent",
                    "message": seq,
                    "location" : "send_invoice_excel",
                    "totalCount" : len(sendInvoices),
                    "ready" : "false"
                }
            )
            
            if sendInvoice.theRequest:
                project = sendInvoice.theRequest.requestNo
            elif sendInvoice.offer:
                project = sendInvoice.offer.offerNo
            else:
                project  = ""
            
            if sendInvoice.customer:
                customer = sendInvoice.customer.name
            else:
                customer = ""
            
            if sendInvoice.vessel:
                vessel = sendInvoice.vessel.name
            else:
                vessel = ""
                
            if sendInvoice.billing:
                billing = sendInvoice.billing.name
            else:
                billing = ""
                
            data["Line"].append(seq)
            data["Project No"].append(project)
            data["Group"].append(sendInvoice.group)
            data["Customer"].append(customer)
            data["Vessel"].append(vessel)
            data["Billing Name"].append(billing)
            data["Invoice Date"].append(str(sendInvoice.sendInvoiceDate.strftime("%d.%m.%Y")))
            data["Invoice No"].append(sendInvoice.sendInvoiceNo)
            data["Payment Date"].append(str(sendInvoice.paymentDate.strftime("%d.%m.%Y")))
            data["Net Amount"].append(sendInvoice.netPrice)
            data["Discount"].append(sendInvoice.discountPrice)
            data["Vat"].append(sendInvoice.vatPrice)
            data["Gross Amount"].append(sendInvoice.totalPrice)
            data["Currency"].append(sendInvoice.currency.code)
            data["Exchange Rate"].append(sendInvoice.exchangeRate)
            data["TRY Gross"].append(sendInvoice.totalPrice * sendInvoice.exchangeRate)
            data["Paid"].append("Paid" if sendInvoice.payed == True else "Not Paid")
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/all-send-invoices.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='SendInvoice', index=False)
            # dfTo.to_excel(writer, sheet_name='SendInvoice', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='SendInvoice', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        if sendInvoices:
            sendInvoicesCount = len(sendInvoices)
        else:
            sendInvoicesCount = 0
        async_to_sync(channel_layer.group_send)(
            'private_' + str(request.user.id),
            {
                "type": "send_percent",
                "message": seq,
                "location" : "send_invoice_excel",
                "totalCount" : sendInvoicesCount,
                "ready" : "true"
            }
        )
        
        return HttpResponse(status=204)

class SendInvoiceDownloadExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/account/send_invoice/documents/all-send-invoices.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'
        
        return response

class SendInvoiceFaturaPdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Send Invoice Pdf")
        elementTag = "sendInvoice"
        elementTagSub = "sendInvoicePart"
        elementTagId = id

        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "account", "send_invoice", "documents")


        # Örnek veri
        items = [
            {"name": "yarrak 1", "quantity": 2, "unit_price": 50, "total": 100},
            {"name": "Ürün 2", "quantity": 5, "unit_price": 30, "total": 150},
        ]
        grand_total = sum(item["total"] for item in items)

        # HTML içeriğini oluştur
        html_content = render_to_string("account/invoice_pdf.html", {"items": items, "grand_total": grand_total})

        # Kaydedilecek dosya yolu
        os.makedirs(base_path, exist_ok=True)  # Klasör yoksa oluştur
        file_name = "rapor.pdf"
        file_path = os.path.join(base_path, file_name)

        # PDF'yi kaydet
        HTML(string=html_content).write_pdf(file_path)

        return HttpResponse(status=204)
    
class SendInvoicePdfHtmlView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Send Invoice Pdf Html")
        
        elementTag = "senInvoicePdfHtml"
        elementTagSub = "senInvoicePdfHtmlPart"

        sourceCompany = request.user.profile.sourceCompany
        
        form = CompanySendInvoicePdfHtmlForm(request.POST or None, request.FILES or None, instance = sourceCompany, user=request.user)

        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "form" : form,
                "sessionKey" : request.session.session_key
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/send_invoice/send_invoice_pdf_html.html', context)
    
    def post(self, request, id, *args, **kwargs):
        sourceCompany = request.user.profile.sourceCompany

        form = CompanySendInvoicePdfHtmlForm(request.POST, request.FILES or None, instance = sourceCompany, user=request.user)
        
        if form.is_valid():
            sourceCompany = form.save(commit = False)
            sourceCompany.save()

        return HttpResponse(status=204)
