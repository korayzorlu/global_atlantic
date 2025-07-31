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
        elementTag = "purchasingInquiry"
        elementTagSub = "purchasingInquiryPart"
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
        
        return render(request, 'purchasing/inquiry/inquiries.html', context)
    
class InquiryAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Create Inquiry")
        elementTag = "purchasingInquiryAdd"
        elementTagSub = "purchasingInquiryItemInAdd"
        elementTagId = id
        
        project = Project.objects.get(id = id)
        suppliers = Company.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        items = ProjectItem.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,project = project)

        form = InquiryForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "suppliers" : suppliers,
                "items" : items,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'purchasing/inquiry/inquiry_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "purchasingInquiryAdd"
        elementTagSub = "purchasingInquiryItemInAdd"
        elementTagId = id

        form = InquiryForm(request.POST, request.FILES or None, user = request.user)
        
        suppliers = request.POST.getlist("suppliers")
        items = request.POST.getlist("items")
        
        if suppliers and items:
            for supplier in suppliers:
                
                identificationCode = request.user.profile.sourceCompany.purchasingInquiryCode
                yearCode = int(str(datetime.today().date().year)[-2:])
                startCodeValue = 1
                
                lastProject = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                
                if lastProject:
                    lastCode = lastProject.code
                else:
                    lastCode = startCodeValue - 1
                
                code = int(lastCode) + 1
                
                inquiryNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
                
                project = Project.objects.select_related().filter(id = id).first()
                theSupplier = Company.objects.select_related().filter(id = int(supplier)).first()
                currency = Currency.objects.select_related().filter(id = 106).first()
                
                inquiry = Inquiry.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    code = code,
                    yearCode = yearCode,
                    inquiryNo = inquiryNo,
                    project = project,
                    supplier = theSupplier,
                    currency = currency,
                    sessionKey = request.session.session_key,
                    user = request.user
                )
                
                inquiry.save()
                
                #project = inquiry.project
                project.stage = "inquiry"
                project.save()
                
                for item in items:
                    projectItem = ProjectItem.objects.select_related().filter(id = int(item)).first()
                    inquiryItem = InquiryItem.objects.create(
                        sourceCompany = request.user.profile.sourceCompany,
                        user = request.user,
                        sessionKey = request.session.session_key,
                        inquiry = inquiry,
                        projectItem = projectItem,
                        name = projectItem.name,
                        description = projectItem.description,
                        unit = projectItem.unit,
                        sequency = projectItem.sequency,
                        quantity = projectItem.quantity
                    )
                    inquiryItem.save()
                
                inquiryItems = inquiry.inquiryitem_set.select_related().filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry).order_by("-projectItem__id")

                inquiryPdfInTask.delay(inquiry.id,request.user.profile.sourceCompany.id)
                
            return HttpResponse(status=204)
        
        else:
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"triangle-exclamation",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)

class InquiryUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Inquiry Detail")
        elementTag = "purchasingInquiry"
        elementTagSub = "purchasingInquiryPart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        
        inquiries = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        inquiry = get_object_or_404(Inquiry, id = id)
        
        inquiryItems = InquiryItem.objects.filter(inquiry = inquiry)
        inquiryItemList = []
        
        for inquiryItem in inquiryItems:
            inquiryItemList.append(inquiryItem.id)
        
        items = InquiryItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry)
        pageLoad(request,20,100,"false")
        itemsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
        itemsTotal = 0
        
        for index, item in enumerate(items):
            percent = (60/len(items)) * (index + 1)
            pageLoad(request,20+percent,100,"false")
            itemsTotal  = itemsTotal + item.totalPrice
            itemsTotals["totalUnitPrice1"] = itemsTotals["totalUnitPrice1"] + item.unitPrice
            itemsTotals["totalUnitPrice2"] = itemsTotals["totalUnitPrice2"] + item.unitPrice
            itemsTotals["totalUnitPrice3"] = itemsTotals["totalUnitPrice3"] + item.unitPrice
            itemsTotals["totalTotalPrice1"] = itemsTotals["totalTotalPrice1"] + item.totalPrice
            itemsTotals["totalTotalPrice2"] = itemsTotals["totalTotalPrice2"] + item.totalPrice
            itemsTotals["totalTotalPrice3"] = itemsTotals["totalTotalPrice3"] + item.totalPrice
            
        itemsTotals["totalFinal"] = itemsTotals["totalTotalPrice3"]
        
        # Para miktarını belirtilen formatta gösterme
        totalTotalPriceFixed = "{:,.2f}".format(round(itemsTotals["totalFinal"],2))
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
                "inquiryItemList" : inquiryItemList,
                "items" : items,
                "itemsTotals" : itemsTotals,
                "totalTotalPriceFixed" : totalTotalPriceFixed,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'purchasing/inquiry/inquiry_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "purchasingInquiry"
        elementTagSub = "purchasingInquiryPart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        inquiry = get_object_or_404(Inquiry, id = id)
        project = inquiry.project
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
            inquiry.identificationCode = identificationCode
            inquiry.code = code
            inquiry.yearCode = yearCode
            inquiry.inquiryNo = inquiryNo
            inquiry.sessionKey = sessionKey
            inquiry.user = user
            inquiry.save()
            
            items = InquiryItem.objects.filter(inquiry = inquiry)
            itemsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
            itemsTotal = 0
            
            for index, item in enumerate(items):
                percent = (60/len(items)) * (index + 1)
                pageLoad(request,20+percent,100,"false")
                itemsTotal  = itemsTotal + item.totalPrice
                itemsTotals["totalUnitPrice1"] = itemsTotals["totalUnitPrice1"] + item.unitPrice
                itemsTotals["totalUnitPrice2"] = itemsTotals["totalUnitPrice2"] + item.unitPrice
                itemsTotals["totalUnitPrice3"] = itemsTotals["totalUnitPrice3"] + item.unitPrice
                itemsTotals["totalTotalPrice1"] = itemsTotals["totalTotalPrice1"] + item.totalPrice
                itemsTotals["totalTotalPrice2"] = itemsTotals["totalTotalPrice2"] + item.totalPrice
                itemsTotals["totalTotalPrice3"] = itemsTotals["totalTotalPrice3"] + item.totalPrice
                
            itemsTotals["totalFinal"] = itemsTotals["totalTotalPrice3"]
            
            inquiry.totalTotalPrice = round(itemsTotals["totalFinal"],2)
            inquiry.save()
            pageLoad(request,90,100,"false")
            inquiryPdfInTask.delay(inquiry.id,request.user.profile.sourceCompany.id)
            pageLoad(request,100,100,"true")
            
            # Para miktarını belirtilen formatta gösterme
            totalTotalPriceFixed = "{:,.2f}".format(round(inquiry.totalTotalPrice,2))
            # Nokta ile virgülü değiştirme
            totalTotalPriceFixed = totalTotalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            totalPrices = {"inquiry":inquiry.id,
                            "totalTotalPrice":totalTotalPriceFixed,
                            "currency":inquiry.currency.symbol}
            
            updateDetail(totalPrices,"purchasing_inquiry_update")

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
        elementTag = "purchasingInquiry"
        elementTagSub = "purchasingInquiryPart"
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

        return render(request, 'purchasing/inquiry/inquiry_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        
        for index, id in enumerate(idList):
            percent = (90/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")  
            
            inquiry = get_object_or_404(Inquiry, id = id)
            #process status sil
            processStatus = inquiry.project.process_status_purchasing_project.first()
            if processStatus:
                processStatus.delete()
            #process status sil-end
            inquiry.delete()
        
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)

class InquiryPdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Inquiry PDF")
        
        elementTag = "purchasingInquiry"
        elementTagSub = "purchasingInquiryPart"
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
        
        return render(request, 'purchasing/inquiry/inquiry_pdf.html', context)


class InquirySentView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        
        inquiry = get_object_or_404(Inquiry, id = id)
        
        pageLoad(request,50,100,"false")
        
        inquiry.approval = "sent"
        inquiry.save()
        
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)

