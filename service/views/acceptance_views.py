from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage, send_mail
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa
from django.template.loader import get_template 

from ..forms import *
from ..pdfs.offer_pdfs import *
from ..pdfs.active_project_pdfs import *
from ..pdfs.finish_project_pdfs import *
from ..pdfs.acceptance_pdfs import *

from source.models import Company as SourceCompany

import pandas as pd
import json
import random
import string
from datetime import datetime

class AcceptanceDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Acceptances")
        elementTag = "acceptance"
        elementTagSub = "acceptancePart"

        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/acceptance/acceptances.html', context)

class AcceptanceAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Acceptance")
        elementTag = "acceptance"
        elementTagSub = "acceptancePart"
        print(request.session.session_key)
        form = AcceptanceForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/acceptance/acceptance_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = AcceptanceForm(request.POST, request.FILES or None, user = request.user)
        
        if form.is_valid():
            acceptance = form.save(commit = False)
            acceptance.sourceCompany = request.user.profile.sourceCompany
            
            identificationCode = "ESM"
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastRequest = Acceptance.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            if lastRequest:
                lastCode = lastRequest.code
            else:
                lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            acceptance.code = code
            
            acceptance.yearCode = yearCode
            
            acceptanceNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
            acceptance.acceptanceNo = acceptanceNo
            
            acceptance.user = request.user
            acceptance.save()

            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)

class AcceptanceUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Acceptance Detail")
        elementTag = "acceptance"
        elementTagSub = "acceptancePart"
        elementTagId = id
        
        acceptances = Acceptance.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        acceptance = get_object_or_404(Acceptance, id = id)
        

        
        form = AcceptanceForm(request.POST or None, request.FILES or None, instance = acceptance, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "acceptances" : acceptances,
                "acceptance" : acceptance,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/acceptance/acceptance_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        acceptance = get_object_or_404(Acceptance, id = id)
        identificationCode = acceptance.identificationCode
        code = acceptance.code
        yearCode = acceptance.yearCode
        acceptanceNo = acceptance.acceptanceNo
        user = acceptance.user
        sourceCompany = acceptance.sourceCompany
        form = AcceptanceForm(request.POST, request.FILES or None, instance = acceptance, user = request.user)
        if form.is_valid():
            acceptance = form.save(commit = False)
            acceptance.sourceCompany = sourceCompany
            acceptance.identificationCode = identificationCode
            acceptance.code = code
            acceptance.yearCode = yearCode
            acceptance.acceptanceNo = acceptanceNo
            acceptance.user = user
            
            acceptance.save()
            
            acceptancePdf(acceptance, request.user.profile.sourceCompany)
                
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)
        
class AcceptanceDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Acceptance")
        elementTag = "acceptance"
        elementTagSub = "acceptancePart"
        
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
        
        return render(request, 'service/acceptance/acceptance_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:   
            acceptance = get_object_or_404(Acceptance, id = int(id))
            acceptance.delete()
        return HttpResponse(status=204)

class AcceptanceServiceCardInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Acceptance Service Card")
        elementTag = "acceptance"
        elementTagSub = "acceptancePart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        acceptanceId = refererPath.replace("/service/acceptance_update/","").replace("/","")
        acceptance = get_object_or_404(Acceptance, id = id)
        
        form = AcceptanceServiceCardForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "acceptance" : acceptance,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/acceptance/acceptance_service_card_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        acceptanceId = refererPath.replace("/service/acceptance_update/","").replace("/","")
        
        acceptance = Acceptance.objects.get(id = id)
        acceptanceServiceCards = AcceptanceServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany,acceptance = acceptance)
        
        serviceCards = []
        
        for acceptanceServiceCard in acceptanceServiceCards:
            serviceCards.append(acceptanceServiceCard.serviceCard)
        
        form = AcceptanceServiceCardForm(request.POST, request.FILES or None)
        if form.is_valid():
            acceptanceServiceCard = form.save(commit = False)
            acceptanceServiceCard.sourceCompany = request.user.profile.sourceCompany
            
            if acceptanceServiceCard.serviceCard in serviceCards:
                return HttpResponse(status=500)
            else:
                acceptanceServiceCard.user = request.user
                acceptanceServiceCard.acceptance = get_object_or_404(Acceptance, id = id)
                acceptanceServiceCard.save()
                return HttpResponse(status=204)
        else:
            context = {
                    "form" : form,
                    "acceptanceId" : acceptanceId
            }
            return render(request, 'service/acceptance/acceptance_service_card_add_in_detail.html', context)

class AcceptanceServiceCardDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Acceptance Service Card")
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
            acceptanceServiceCard = get_object_or_404(AcceptanceServiceCard, id = int(id))
            acceptanceServiceCard.delete()
        return HttpResponse(status=204)


class AcceptancePdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Acceptance PDF")
        
        elementTag = "acceptance"
        elementTagSub = "acceptancePart"
        elementTagId = str(id) + "-pdf"
        
        acceptance = Acceptance.objects.get(id = id)
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "acceptance" : acceptance,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/acceptance/acceptance_pdf.html', context)