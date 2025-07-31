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
from ..pdfs.request_pdfs import *
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
    
class RequestDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Projects")
        elementTag = "request"
        elementTagSub = "requestPart"
        
        pageLoad(request,0,100,"false")
        
        # def send_outlook_email(subject, message, from_email, recipient_list):
        #     send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
        # subject = 'Konu'
        # message = 'Merhaba, bu bir test e-postasıdır.'
        # from_email = 'armin_koray@hotmail.com'
        # recipient_list = ['korayzorllu@gmail.com']

        # send_outlook_email(subject, message, from_email, recipient_list)
        
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

        return render(request, 'sale/request/requests.html', context)
    
class RequestAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Request")
        elementTag = "request"
        elementTagSub = "requestPart"
        elementTagId = "new"
        
        pageLoad(request,0,100,"false")
        
        form = RequestForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/request/request_add.html', context)
    
    def post(self, request, *args, **kwargs):
        elementTag = "request"
        elementTagSub = "requestPart"
        elementTagId = "new"

        pageLoad(request,0,100,"false")
        form = RequestForm(request.POST, request.FILES or None, user = request.user)
        
        if form.is_valid():
            requestt = form.save(commit = False)
            requestt.sourceCompany = request.user.profile.sourceCompany
            
            identificationCode = request.user.profile.sourceCompany.saleRequestCode
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastRequest = Request.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            pageLoad(request,20,100,"false")
            
            if lastRequest:
                lastCode = lastRequest.code
            else:
                lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            requestt.code = code
            
            requestt.yearCode = yearCode
            
            requestNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
            requestt.requestNo = requestNo
            
            project = Project.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                user = request.user,
                stage = "request",
                projectNo = requestNo
            )
            
            project.save()
            pageLoad(request,60,100,"false")
            requestt.project = project
            requestt.sessionKey = request.session.session_key
            requestt.save()
            
            sessionRequestParts = RequestPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,sessionKey = request.session.session_key, user = request.user, theRequest = None)
            for sessionRequestPart in sessionRequestParts:
                sessionRequestPart.theRequest = requestt
                sessionRequestPart.save()

            pageLoad(request,100,100,"true")

            return HttpResponse(status=204)
        else:
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"triangle-exclamation",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
        
class RequestUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Request Detail")
        elementTag = "request"
        elementTagSub = "requestPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        requests = Request.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        pageLoad(request,20,100,"false")
        requestt = get_object_or_404(Request, project = id)
        pageLoad(request,40,100,"false")
        inquiries = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = requestt)
        pageLoad(request,60,100,"false")
        parts = RequestPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = requestt)
        pageLoad(request,80,100,"false")
        
        # addParts = Part.objects.filter(maker = requestt.maker, type = requestt.makerType)
        # partsLength = len(addParts)
        
        form = RequestForm(request.POST or None, request.FILES or None, instance = requestt, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "requests" : requests,
                "requestt" : requestt,
                "inquiries" : inquiries,
                "parts" : parts,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/request/request_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        requestt = get_object_or_404(Request, project = id)
        project = requestt.project
        identificationCode = requestt.identificationCode
        code = requestt.code
        yearCode = requestt.yearCode
        requestNo = requestt.requestNo
        maker = requestt.maker
        makerType = requestt.makerType
        sessionKey = requestt.sessionKey
        sourceCompany = requestt.sourceCompany
        pageLoad(request,20,100,"false")
        form = RequestForm(request.POST, request.FILES or None, instance = requestt, user = request.user)
        if form.is_valid():
            requestt = form.save(commit = False)
            requestt.sourceCompany = sourceCompany
            requestt.project = project
            requestt.identificationCode = identificationCode
            requestt.code = code
            requestt.yearCode = yearCode
            requestt.requestNo = requestNo
            requestt.sessionKey = sessionKey
            # requestt.maker = maker
            # requestt.makerType = makerType

            project.projectNo = requestNo
            project.save()
            requestt.save()
            
            sessionRequestParts = RequestPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,sessionKey = request.session.session_key, user = request.user, theRequest = None)
            for index, sessionRequestPart in enumerate(sessionRequestParts):
                percent = (70/len(sessionRequestParts)) * (index + 1)
                pageLoad(request,20+percent,100,"false")
                sessionRequestPart.theRequest = requestt
                sessionRequestPart.save()
            
            pageLoad(request,100,100,"true")
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)
    
class RequestDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Request")
        elementTag = "request"
        elementTagSub = "requestPart"
        
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
        
        return render(request, 'sale/request/request_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            project = get_object_or_404(Project, id = int(id))
            theRequest = Request.objects.get(project = project)
            inquiries = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = theRequest)
            pageLoad(request,90,100,"false")
            if len(inquiries) == 0:
                project.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
    
class RequestPdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Reqeust PDF")
        
        elementTag = "request"
        elementTagSub = "requestPart"
        elementTagId = str(id) + "-pdf"
        
        requestt = get_object_or_404(Request, project = id)
        
        requestPdf(requestt)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "requestt" : requestt
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/request/request_pdf.html', context)
    
class RequestPartAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Request Part")
        elementTag = "requestPart"
        elementTagSub = "requestPartPart"
        elementTagId = id
        
        form = RequestPartForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/request/request_part_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = RequestPartForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            requestPart = form.save(commit = False)
            requestPart.sourceCompany = request.user.profile.sourceCompany
            requestPart.user = request.user
            requestPart.sessionKey = request.session.session_key
            requestPart.save()
            
            return HttpResponse(status=204)
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'sale/request/request_part_add.html', context)

class RequestPartReorderView(LoginRequiredMixin, View):
    def post(self, request, theRequestId, id, old, new, *args, **kwargs):
        idList = id.split(",")
        oldList = old.split(",")
        newList = new.split(",")
        
        requestParts = RequestPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = theRequestId).order_by("sequency")
        sequency = 1
        for requestPart in requestParts:
            requestPart.sequency = sequency
            requestPart.save()
            sequency = sequency + 1
        
        for i in range(len(idList)):
            requestPart = RequestPart.objects.filter(id = idList[i]).first()
            requestPart.sequency = newList[i]
            requestPart.save()
            
            inquiryParts = InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,requestPart = requestPart)
            if len(inquiryParts) > 0:
                inquiryPartsAll = InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiryParts[0].inquiry).order_by("sequency")
                sequency = 1
                for inquiryPartAll in inquiryPartsAll:
                    inquiryPartAll.sequency = sequency
                    inquiryPartAll.save()
                    sequency = sequency + 1
                    
                for inquiryPart in inquiryParts:
                    inquiryPart.sequency = newList[i]
                    inquiryPart.save()
                    
                    quotationParts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiryPart = inquiryPart)
                    if len(quotationParts) > 0:
                        quotationPartsAll = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotationParts[0].quotation).order_by("sequency")
                        sequency = 1
                        for quotationPartAll in quotationPartsAll:
                            quotationPartAll.sequency = sequency
                            quotationPartAll.save()
                            sequency = sequency + 1
                    
                        for quotationPart in quotationParts:
                            quotationPart.sequency = newList[i]
                            quotationPart.save()
                            print(str(quotationPart.sequency) + " - " + str(quotationPart.note))
                            
                    purchaseOrderParts = PurchaseOrderPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiryPart = inquiryPart)
                    if len(purchaseOrderParts) > 0:
                        purchaseOrderPartsAll = PurchaseOrderPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrderParts[0].purchaseOrder).order_by("sequency")
                        sequency = 1
                        for purchaseOrderPartAll in purchaseOrderPartsAll:
                            purchaseOrderPartAll.sequency = sequency
                            purchaseOrderPartAll.save()
                            sequency = sequency + 1
                            
                        for purchaseOrderPart in purchaseOrderParts:
                            purchaseOrderPart.sequency = newList[i]
                            purchaseOrderPart.save()
                            
                            collectionParts = CollectionPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrderPart = purchaseOrderPart)
                            if len(collectionParts) > 0:
                                collectionPartsAll = CollectionPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,collection = collectionParts[0].collection).order_by("sequency")
                                sequency = 1
                                for collectionPartAll in collectionPartsAll:
                                    collectionPartAll.sequency = sequency
                                    collectionPartAll.save()
                                    sequency = sequency + 1
                            
                                for collectionPart in collectionParts:
                                    collectionPart.sequency = newList[i]
                                    collectionPart.save()
            
            theRequest = requestPart.theRequest
            
            #print("part: " + requestPart.part.partNo + " old: " + str(oldList[i]) + " new: " + str(newList[i]))
        
        
            
        return HttpResponse(status=204)

class RequestPartInDetailAddView(LoginRequiredMixin, View):

    def get(self, request, id, *args, **kwargs):
        tag = _("Add Request Part")
        elementTag = "requestPart"
        elementTagSub = "requestPartPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        requestId = refererPath.replace("/sale/request_update/","").replace("/","")
        theRequest = get_object_or_404(Request, project = id)
        form = RequestPartForm(request.POST or None, request.FILES or None, user = request.user)
        
        if is_ajax(request=request):
            term = request.GET.get("term")
            parts = Part.objects.filter(sourceCompany = request.user.profile.sourceCompany,maker = theRequest.maker, partNo__icontains = term)
            if len(parts) == 0:
                parts = Part.objects.filter(sourceCompany = request.user.profile.sourceCompany,maker = theRequest.maker, group__icontains = term)
            response_content = list(parts.values())
            
            return JsonResponse(response_content, safe=False)
            
        # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        #     term = request.GET.get("term")
        #     print(term)
        #     #parts = Part.objects.filter(partNo__icontains = term)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "theRequest" : theRequest,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/request/request_part_add_in_detail_yedek.html', context)
    
    def post(self, request, id, *args, **kwargs):
        # refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        # requestId = refererPath.replace("/sale/request_update/","").replace("/","")
        
        theRequest = Request.objects.get(project = id)
        requestParts = RequestPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = theRequest)
        sequencyCount = len(requestParts)
        parts = []
        
        for requestPart in requestParts:
            parts.append(requestPart.part)
        
        
        requestParts = request.POST.getlist("requestParts")
        
        for item in requestParts:
            part = Part.objects.get(id = int(item))
            newRequestPart = RequestPart.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    theRequest = theRequest,
                    part = part,
                    quantity = 1,
                    sequency = sequencyCount + 1
                )
            newRequestPart.save()
            
            # requestPartControl = RequestPart.objects.filter(theRequest = theRequest, part = part)
            # if not requestPartControl:
            #     newRequestPart = RequestPart.objects.create(
            #          user = request.user,
            #          theRequest = theRequest,
            #          part = part,
            #          quantity = 1,
            #          sequency = sequencyCount + 1
            #     )
            #     newRequestPart.save()
            sequencyCount = sequencyCount + 1
        
        # theRequest = Request.objects.get(project = id)
        # requestParts = RequestPart.objects.filter(theRequest = theRequest)
        
        # parts = []
        
        # for requestPart in requestParts:
        #     parts.append(requestPart.part)
        
        # #####select2'den multiple seçim yapılırken uygulanan yöntem#####
        # postParts = request.POST.getlist("partFormName")
        
        # for item in postParts:
        #     if item == "":
        #         postParts.remove(item)
        
        # for item in postParts:
        #     part = Part.objects.get(id = int(item))
        #     requestPartControl = RequestPart.objects.filter(theRequest = theRequest, part = part)
        #     if not requestPartControl:
        #         newRequestPart = RequestPart.objects.create(
        #             user = request.user,
        #             theRequest = theRequest,
        #             part = part,
        #             quantity = int(request.POST.get("quantity"))
        #         )
        #         newRequestPart.save()
        
        return HttpResponse(status=204)
        
        #####select2'den multiple seçim yapılırken uygulanan yöntem-end#####
        
        # form = RequestPartForm(request.POST, request.FILES or None, user = request.user)
        # if form.is_valid():
        #     requestPart = form.save(commit = False)
            
        #     if requestPart.part in parts:
        #         return HttpResponse(status=500)
        #     else:
        #         requestPart.user = request.user
        #         requestPart.theRequest = get_object_or_404(Request, project = id)
        #         requestPart.save()
        #         return HttpResponse(status=204)
        # else:
        #     return HttpResponse(status=404)
        
class RequestPartUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Maker Detail")
        elementTag = "request"
        elementTagSub = "requestPart"
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        requestPart = get_object_or_404(RequestPart, id = id)
        theRequest = get_object_or_404(Request, project = requestPart.theRequest.project)

        form = RequestPartForm(request.POST or None, request.FILES or None, instance = requestPart, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "refererPath" : refererPath,
                "form" : form,
                "requestPart" : requestPart,
                "theRequest" : theRequest
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/request/request_part_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        requestPart = get_object_or_404(RequestPart, id = id)
        requestt = requestPart.theRequest
        sessionKey = requestPart.sessionKey
        user = requestPart.user
        sourceCompany = requestPart.sourceCompany
        form = RequestPartForm(request.POST, request.FILES or None, instance = requestPart, user = request.user)
        if form.is_valid():
            requestPart = form.save(commit = False)
            requestPart.sourceCompany = sourceCompany
            requestPart.theRequest = requestt
            requestPart.sessionKey = sessionKey
            requestPart.user = user
            requestPart.save()
            return HttpResponse(status=204)
            
        else:
            context = {
                    "form" : form
            }
        return render(request, 'sale/request/request_part_detail.html', context)

class RequestPartQuantityDuplicateView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        theRequestPart = RequestPart.objects.filter(id = id).first()
        requestParts = RequestPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest=theRequestPart.theRequest)
        
        for requestPart in requestParts:
            requestPart.quantity = theRequestPart.quantity
            requestPart.save()
            
        return HttpResponse(status=204)

class RequestPartAddToInquiryView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Send Request Part")
        
        requestPart = RequestPart.objects.filter(id = id).first()
        theRequest = requestPart.theRequest
        inquiries = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = theRequest)
        
        context = {
                "tag": tag,
                "inquiries" : inquiries
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/request/request_part_add_to_inquiry.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        requestPart = RequestPart.objects.filter(id = id).first()
        pageLoad(request,20,100,"false")
        idList = request.POST.getlist("addToInquiryInquiry")
        
        for index, theId in enumerate(idList):
            percent = (60/len(idList)) * (index + 1)
            pageLoad(request,20+percent,100,"false")
            inquiry = Inquiry.objects.filter(id = theId).first()
            inquiryParts = InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry)
            sequencyCount = len(inquiryParts)
            inquiryPart = InquiryPart.objects.create(
                        sourceCompany = request.user.profile.sourceCompany,
                        user = request.user,
                        sessionKey = request.session.session_key,
                        inquiry = inquiry,
                        requestPart = requestPart,
                        quantity = requestPart.quantity,
                        sequency = sequencyCount + 1
                    )
            inquiryPart.save()
            pageLoad(request,90,100,"false")
        
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
 
         
class RequestPartDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Request Part")
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
            requestPart = get_object_or_404(RequestPart, id = int(id))
            theRequest = requestPart.theRequest
            requestPart.delete()
            
        requestParts = RequestPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = theRequest).order_by("sequency")
        if len(requestParts) > 0:
            sequency = 1
            for requestPart in requestParts:
                requestPart.sequency = sequency
                requestPart.save()
                sequency = sequency +1
        return HttpResponse(status=204)
    