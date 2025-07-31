from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.http.response import HttpResponse
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.utils import timezone
from django.utils.formats import date_format
from datetime import date, timedelta, datetime
from urllib.parse import urlparse

from django.core import serializers
# Create your views here.

from ..models import *
from ..forms import *
from source.models import Company as SourceCompany

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
    
class CompanyDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Companies")
        elementTag = "sourceCompany"
        elementTagSub = "sourceCompanyPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'administration/company/companies.html', context)

class CompanyAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Company")
        elementTag = "sourceCompany"
        elementTagSub = "sourceCompanyPart"
        
        pageLoad(request,0,100,"false")
        
        form = CompanyForm(request.POST or None, request.FILES or None)
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
        pageLoad(request,100,100,"true")
        
        return render(request, 'administration/company/company_add.html', context)
    def post(self, request, *args, **kwargs):
        pageLoad(request,0,100,"false")
        form = CompanyForm(request.POST, request.FILES or None)
        
        if form.is_valid():
            company = form.save(commit = False)
            company.user = request.user
            company.sessionKey = request.session.session_key
            
            if not company.name:
                data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":"Name field must be fill!"
                    }
                
                sendAlert(data,"default")
            elif not company.formalName:
                data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":"Name field must be fill!"
                    }
                
                sendAlert(data,"default")
                
            identificationCode = "SC"
            startCodeValue = 1
            
            lastCompany = SourceCompany.objects.select_related().filter().extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            if lastCompany:
                lastCode = lastCompany.code
            else:
                lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            company.code = code
            
            companyNo = str(identificationCode) + "-" + str(code).zfill(8)
            company.companyNo = companyNo
            
            company.save()

            pageLoad(request,100,100,"true")

            return HttpResponse(status=204)
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'administration/company/company_add.html', context)

 
class CompanyUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Company Detail")
        elementTag = "sourceCompany"
        elementTagSub = "sourceCompanyPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        companies = SourceCompany.objects.filter()
        pageLoad(request,20,100,"false")
        company = get_object_or_404(SourceCompany, id = id)
        pageLoad(request,40,100,"false")
        pageLoad(request,60,100,"false")
        pageLoad(request,80,100,"false")
        
        # addParts = Part.objects.filter(maker = requestt.maker, type = requestt.makerType)
        # partsLength = len(addParts)
        
        form = CompanyForm(request.POST or None, request.FILES or None, instance = company)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "companies" : companies,
                "company" : company,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'administration/company/company_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        company = get_object_or_404(SourceCompany, id = id)
        user = company.user
        sessionKey = company.sessionKey
        pageLoad(request,20,100,"false")
        form = CompanyForm(request.POST, request.FILES or None, instance = company)
        if form.is_valid():
            company = form.save(commit = False)
            company.user = user
            company.sessionKey = sessionKey
            
            company.save()
            
            pageLoad(request,100,100,"true")
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)

class CompanyDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Company")
        elementTag = "company"
        elementTagSub = "companyPart"
        
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
        
        return render(request, 'administration/company/company_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            company = get_object_or_404(SourceCompany, id = int(id))
            pageLoad(request,90,100,"false")
            company.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
   