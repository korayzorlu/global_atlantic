from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage, send_mail
# Create your views here.
from django.views import View
from django.views.decorators.cache import cache_page
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Template
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import close_old_connections

from ..forms import *
from ..tasks import *
from ..pdfs.inquiry_pdfs import *
from ..pdfs.quotation_pdfs import *

from source.models import Company as SourceCompany
from account.models import ProformaInvoice, CommericalInvoice, SendInvoice

import pandas as pd
import json
import random
import string
from datetime import datetime
import time

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

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

def pageLoad(request,percent,total,ready):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'private_' + str(request.user.id),
        {
            "type": "send_percent",
            "message": percent,
            "location" : "page_load",
            "totalCount" : total,
            "ready" : ready
        }
    )
    
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

class InquiryDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Inquiries")
        elementTag = "inquiry"
        elementTagSub = "inquiryPart"
        pageLoad(request,0,100,"false")
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/inquiry/inquiries.html', context)
    
class InquiryAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Create Inquiry")
        elementTag = "inquiryAdd"
        elementTagSub = "inquiryPartInAdd"
        elementTagId = id
        
        theRequest = Request.objects.get(project = id)
        suppliers = Company.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        parts = RequestPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = theRequest)

        form = InquiryForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "suppliers" : suppliers,
                "parts" : parts,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/inquiry/inquiry_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        form = InquiryForm(request.POST, request.FILES or None, user = request.user)
        
        suppliers = request.POST.getlist("suppliers")
        parts = request.POST.getlist("parts")
        
        if suppliers and parts:
            for supplier in suppliers:
                
                identificationCode = request.user.profile.sourceCompany.saleInquiryCode
                yearCode = int(str(datetime.today().date().year)[-2:])
                startCodeValue = 1
                
                lastRequest = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                
                if lastRequest:
                    lastCode = lastRequest.code
                else:
                    lastCode = startCodeValue - 1
                
                code = int(lastCode) + 1
                
                inquiryNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
                
                project = Project.objects.select_related().filter(id = id).first()
                theRequest = project.request
                theSupplier = Company.objects.select_related().filter(id = int(supplier)).first()
                currency = Currency.objects.select_related().filter(id = 106).first()
                
                inquiry = Inquiry.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    code = code,
                    yearCode = yearCode,
                    inquiryNo = inquiryNo,
                    project = project,
                    theRequest = theRequest,
                    supplier = theSupplier,
                    currency = currency,
                    sessionKey = request.session.session_key,
                    user = request.user
                )
                
                inquiry.save()
                
                #project = inquiry.project
                project.stage = "inquiry"
                project.save()
                
                for part in parts:
                    requestPart = RequestPart.objects.select_related().filter(id = int(part)).first()
                    inquiryPart = InquiryPart.objects.create(
                        sourceCompany = request.user.profile.sourceCompany,
                        user = request.user,
                        sessionKey = request.session.session_key,
                        inquiry = inquiry,
                        requestPart = requestPart,
                        sequency = requestPart.sequency,
                        quantity = requestPart.quantity
                    )
                    inquiryPart.save()
                
                inquiryParts = inquiry.inquirypart_set.select_related().filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry).order_by("requestPart__sequency")
                sequencyCount = 0
                for inquiryPart in inquiryParts:
                    InquiryPart.objects.filter(id = inquiryPart.id).update(sequency = sequencyCount + 1)
                    # inquiryPart.sequency = sequencyCount + 1
                    # inquiryPart.save()
                    sequencyCount = sequencyCount + 1
                    
                inquiryPdfInTask.delay(inquiry.id,request.user.profile.sourceCompany.id)
                #inquiryPdf(inquiry)
              
            return HttpResponse(status=204)
        
        else:
            data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"At least one supplier and one part must be selected!"
                }
            
            sendAlert(data,"default")
            return HttpResponse(status=404)

class InquiryUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Inquiry Detail")
        elementTag = "inquiry"
        elementTagSub = "inquiryPart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        
        inquiries = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        inquiry = get_object_or_404(Inquiry, id = id)
        purchaseOrders = PurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry)
        
        inquiryParts = InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry)
        inquiryPartList = []
        
        for inquiryPart in inquiryParts:
            inquiryPartList.append(inquiryPart.id)
            
        quotations = Quotation.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry)
        
        if len(quotations) > 0:
            quotation = 1
        else:
            quotation = 0
        
        requestt = get_object_or_404(Request, project = inquiry.project)
        
        parts = InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry)
        pageLoad(request,20,100,"false")
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
        partsTotal = 0
        
        for index, part in enumerate(parts):
            percent = (60/len(parts)) * (index + 1)
            pageLoad(request,20+percent,100,"false")
            partsTotal  = partsTotal + part.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
            
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"]
        
        # Para miktarını belirtilen formatta gösterme
        totalTotalPriceFixed = "{:,.2f}".format(round(partsTotals["totalFinal"],2))
        # Nokta ile virgülü değiştirme
        totalTotalPriceFixed = totalTotalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        pageLoad(request,90,100,"false")
        form = InquiryDetailForm(request.POST or None, request.FILES or None, instance = inquiry, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "inquiries" : inquiries,
                "inquiry" : inquiry,
                "inquiryPartList" : inquiryPartList,
                "purchaseOrders" : purchaseOrders,
                "requestt" : requestt,
                "parts" : parts,
                "partsTotals" : partsTotals,
                "totalTotalPriceFixed" : totalTotalPriceFixed,
                "quotation" : quotation,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/inquiry/inquiry_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "inquiry"
        elementTagSub = "inquiryPart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        inquiry = get_object_or_404(Inquiry, id = id)
        project = inquiry.project
        theRequest = inquiry.theRequest
        identificationCode = inquiry.identificationCode
        code = inquiry.code
        yearCode = inquiry.yearCode
        inquiryNo = inquiry.inquiryNo
        sessionKey = inquiry.sessionKey
        user = inquiry.user
        sourceCompany = inquiry.sourceCompany

        form = InquiryDetailForm(request.POST, request.FILES or None, instance = inquiry, user = request.user)
        pageLoad(request,20,100,"false")
        if form.is_valid():
            inquiry = form.save(commit = False)
            inquiry.sourceCompany = sourceCompany
            inquiry.project = project
            inquiry.theRequest = theRequest
            inquiry.identificationCode = identificationCode
            inquiry.code = code
            inquiry.yearCode = yearCode
            inquiry.inquiryNo = inquiryNo
            inquiry.sessionKey = sessionKey
            inquiry.user = user
            inquiry.save()
            
            parts = InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry)
            partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
            partsTotal = 0
            
            for index, part in enumerate(parts):
                percent = (60/len(parts)) * (index + 1)
                pageLoad(request,20+percent,100,"false")
                partsTotal  = partsTotal + part.totalPrice
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
                
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"]
            
            inquiry.totalTotalPrice = round(partsTotals["totalFinal"],2)
            inquiry.save()
            pageLoad(request,90,100,"false")
            #inquiryPdfInTask.delay(id)
            inquiryPdfInTask.delay(inquiry.id,request.user.profile.sourceCompany.id)
            pageLoad(request,100,100,"true")
            
            # Para miktarını belirtilen formatta gösterme
            totalTotalPriceFixed = "{:,.2f}".format(round(inquiry.totalTotalPrice,2))
            # Nokta ile virgülü değiştirme
            totalTotalPriceFixed = totalTotalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            totalPrices = {"inquiry":inquiry.id,
                            "totalTotalPrice":totalTotalPriceFixed,
                            "currency":inquiry.currency.symbol}
            
            updateDetail(totalPrices,"inquiry_update")

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
            return HttpResponse(status=404)
        
class InquiryDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Inquiries")
        elementTag = "inquiry"
        elementTagSub = "inquiryPart"
        idList = list.split(",")
        elementTagId = idList[0]
        for id in idList:
            print(int(id))
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

        return render(request, 'sale/inquiry/inquiry_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        
        for index, id in enumerate(idList):
            percent = (90/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")  
            
            inquiry = get_object_or_404(Inquiry, id = id)
            quotations = Quotation.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiries = inquiry)
            if len(quotations) == 0:
                inquiry.delete()
        
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)

class InquiryPdfView(LoginRequiredMixin, View):
    def get(self, request, id, source, *args, **kwargs):
        tag = _("Inquiry PDF")
        
        if source == "i":
            elementTag = "inquiry"
            elementTagSub = "inquiryPart"
            elementTagId = str(id) + "-pdf"
        elif source == "ot":
            elementTag = "orderTracking"
            elementTagSub = "orderTrackingPart"
            elementTagId = str(id) + "-pdf"
        
        pageLoad(request,0,100,"false")
        
        inquiry = Inquiry.objects.get(id = id)
        pageLoad(request,50,100,"false")
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "inquiry" : inquiry,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/inquiry/inquiry_pdf.html', context)

class InquiryPdfMakeView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        inquiry = Inquiry.objects.filter(id = id).first()
        
        parts = InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry)
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
    
        partsTotal = 0
        
        for part in parts:
            partsTotal  = partsTotal + part.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
            
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"]
        
        inquiry.totalTotalPrice = round(partsTotals["totalFinal"],2)
        inquiry.save()
            
        inquiryPdf(inquiry)
            
        return HttpResponse(status=204)
 
class InquiryPartUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Maker Detail")
        elementTagSub = "inquiryPart"
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        inquiryPart = get_object_or_404(InquiryPart, id = id)

        form = InquiryPartForm(request.POST or None, request.FILES or None, instance = inquiryPart)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "refererPath" : refererPath,
                "form" : form,
                "inquiryPart" : inquiryPart
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/inquiry/inquiry_part_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        inquiryPart = InquiryPart.objects.get(InquiryPart, id = id)
        inquiry = inquiryPart.inquiry
        sessionKey = inquiryPart.sessionKey
        user = inquiryPart.user
        requestPart = inquiryPart.requestPart
        
        
        
        # form = InquiryPartForm(request.POST, request.FILES or None, instance = inquiryPart)
        # if form.is_valid():
        #     inquiryPart = form.save(commit = False)
        #     inquiryPart.inquiry = inquiry
        #     inquiryPart.sessionKey = sessionKey
        #     inquiryPart.user = user
        #     inquiryPart.requestPart = requestPart
        #     inquiryPart.save()
        #     return HttpResponse(status=204)
            
        # else:
        #     return HttpResponse(status=404)

class InquiryPartQuantityDuplicateView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        theInquiryPart = InquiryPart.objects.select_related("inquiry").get(id = id)
        inquiryParts = theInquiryPart.inquiry.inquirypart_set.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        #inquiryParts.update(quantity = theInquiryPart.quantity)
        
        totalTotalPrice = 0
        for inquiryPart in inquiryParts:
            inquiryPart.quantity = theInquiryPart.quantity
            inquiryPart.totalPrice = float(inquiryPart.unitPrice) * float(inquiryPart.quantity)
            inquiryPart.save()
            totalTotalPrice = totalTotalPrice + inquiryPart.totalPrice
        
        theInquiryPart.inquiry.totalTotalPrice = totalTotalPrice
        theInquiryPart.inquiry.save()
        
        # Para miktarını belirtilen formatta gösterme
        totalTotalPriceFixed = "{:,.2f}".format(round(totalTotalPrice,2))
        # Nokta ile virgülü değiştirme
        totalTotalPriceFixed = totalTotalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        totalPrices = {"inquiry":theInquiryPart.inquiry.id,
                        "totalTotalPrice":totalTotalPriceFixed,
                        "currency":theInquiryPart.inquiry.currency.symbol}
        
        updateDetail(theInquiryPart.inquiry.id,"inquiry_duplicate")
        updateDetail(totalPrices,"inquiry_update") 
            
        return HttpResponse(status=204)
    
class InquiryPartAvailabilityDuplicateView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        theInquiryPart = InquiryPart.objects.select_related("inquiry").get(id = id)
        inquiryParts = theInquiryPart.inquiry.inquirypart_set.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        inquiryParts.update(availability = theInquiryPart.availability)
        
        updateDetail(theInquiryPart.inquiry.id,"inquiry_duplicate")
        
        return HttpResponse(status=204)
    
class InquiryPartDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Inquiry Part")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/inquiry/inquiry_part_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            inquiryPart = get_object_or_404(InquiryPart, id = int(id))
            inquiryPart.delete()
        return HttpResponse(status=204)
    