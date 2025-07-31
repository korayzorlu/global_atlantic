from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio

from ..forms import *
from ..tasks import *
from account.models import SendInvoice

import pandas as pd
from validate_email import validate_email
import json
from operator import itemgetter

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
    
def matchMikro(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "match_mikro",
            "message": message,
            "location" : location
        }
    )

def updateMikro(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "update_mikro",
            "message": message,
            "location" : location
        }
    )
    
def createMikro(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "create_mikro",
            "message": message,
            "location" : location
        }
    )

class BillingDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Vessel Billing")
        elementTag = "billing"
        elementTagSub = "billingPart"
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        
        context = {
                    "tag" : tag,
                    "elementTagSub" : elementTagSub,
                    "elementTag" : elementTag
            }
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'card/billings.html', context)
  
class BillingUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Billing Detail")
        elementTag = "billing"
        elementTagSub = "billingPart"
        elementTagId = id

        billing = get_object_or_404(Billing, id = id)
        
        if billing.hesapKodu:
            cariKod = billing.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
        
        form = BillingForm(request.POST or None, request.FILES or None, instance = billing, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "billing" : billing,
                "cariKod" : cariKod
        }
        return render(request, 'card/billing_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "billing"
        elementTagSub = "billingPart"
        elementTagId = id

        billing = get_object_or_404(Billing, id = id)
        form = BillingForm(request.POST, request.FILES or None, instance = billing, user = request.user)
        if form.is_valid():
            billing = form.save(commit = False)
            billing.sourceCompany = request.user.profile.sourceCompany
            billing.save()
                
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
                "icon":"circle-check",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
  

class BillingInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Billing")
        elementTag = "billing"
        elementTagSub = "billingPart"
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        vesselId = refererPath.replace("/card/vessel_update/","").replace("/","")
        vessel = get_object_or_404(Vessel, id = id)
        
        form = BillingForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "vessel" : vessel,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'card/billing_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        vesselId = refererPath.replace("/card/vessel_update/","").replace("/","")
        
        vessel = Vessel.objects.get(id = id)
        
        form = BillingForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            billing = form.save(commit = False)
            billing.sourceCompany = request.user.profile.sourceCompany
            
            billing.user = request.user
            billing.vessel = vessel
            billing.save()
            
            return HttpResponse(status=204)
        else:
            data = {
                "status":"secondary",
                "icon":"triangle-exclamation",
                "message":form.errors
            }
            
            sendAlert(data,"default")
            return HttpResponse(status=404)

class BillingDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Billing")
        elementTag = "billing"
        elementTagSub = "billingPart"
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
        
        return render(request, 'card/billing_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            billing = get_object_or_404(Billing, id = int(id))
            billing.delete()
        return HttpResponse(status=204)

class BillingMatchWithMikroView(LoginRequiredMixin, View):
    def get(self, request, id, hesapKodu, *args, **kwargs):
        tag = _("Get updates")
        
        elementTag = "companyMatchWith"
        elementTagSub = "companyPartInMatchWith"
        elementTagId = id
        
        company = Billing.objects.select_related().filter(id = id).first()
        
        if company.hesapKodu:
            cariKod = company.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "cariKod" : cariKod
        }
        return render(request, 'card/match_with_mikro.html', context)
    
    def post(self, request, id, hesapKodu, *args, **kwargs):
        channel_layer = get_channel_layer()
        
        billing = Billing.objects.select_related().filter(id = id).first()
        cariKod = billing.hesapKodu
        
        data = {
                "type":"billing",
                "cariKod":cariKod,
                "cariName":billing.name,
                "companyId":id,
                "mikroDBName":request.user.profile.sourceCompany.mikroDBName
                }
            
        matchMikro(data,"match_mikro")
        
        return HttpResponse(status=204)

class BillingUnmatchWithMikroView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Get updates")
        
        elementTag = "billingUnmatchWith"
        elementTagSub = "billingPartInUnmatchWith"
        elementTagId = id
        
        billing = Billing.objects.select_related().filter(id = id).first()
        
        if billing.hesapKodu:
            cariKod = billing.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "billing" : billing,
                "cariKod" : cariKod
        }
        return render(request, 'card/unmatch_with_mikro_billing.html', context)
    
    def post(self, request, id, *args, **kwargs):
        channel_layer = get_channel_layer()
        
        billing = Billing.objects.select_related().filter(id = id).first()
        cariKod = billing.hesapKodu
        
        data = {
                "type":"billing",
                "cariName":billing.name,
                "companyId":id,
                "mikroDBName":request.user.profile.sourceCompany.mikroDBName
                }
            
        matchMikro(data,"unmatch_mikro")
        
        return HttpResponse(status=204)

class BillingUpdateFromMikroView(LoginRequiredMixin, View):
    def get(self, request, id, hesapKodu, *args, **kwargs):
        tag = _("Get updates")
        
        elementTag = "companyUpdateFrom"
        elementTagSub = "companyPartInUpdateFrom"
        elementTagId = id
        
        company = Billing.objects.select_related().filter(id = id).first()
        
        if company.hesapKodu:
            cariKod = company.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "cariKod" : cariKod
        }
        return render(request, 'card/get_updates_from_mikro.html', context)
    
    def post(self, request, id, hesapKodu, *args, **kwargs):
        channel_layer = get_channel_layer()
        
        company = get_object_or_404(Billing, id = id)
        cariKod = company.hesapKodu
        
        data = {"cariKod":cariKod,
                "cariName":company.name,
                "companyId":id,
                "mikroDBName":request.user.profile.sourceCompany.mikroDBName
                        }
            
        updateMikro(data,"update_from_mikro_billing")
        
        return HttpResponse(status=204)
   

class BillingUpdateToMikroView(LoginRequiredMixin, View):
    def get(self, request, id, hesapKodu, *args, **kwargs):
        tag = _("Get updates")
        
        elementTag = "companyUpdateTo"
        elementTagSub = "companyPartInUpdateTo"
        elementTagId = id
        
        company = get_object_or_404(Billing, id = id)
        
        if company.hesapKodu:
            cariKod = company.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "cariKod" : cariKod
        }
        return render(request, 'card/send_updates_to_mikro.html', context)
    
    def post(self, request, id, hesapKodu, *args, **kwargs):
        channel_layer = get_channel_layer()
        
        company = get_object_or_404(Billing, id = id)
        cariKod = company.hesapKodu
        
        data = {"cariKod":cariKod,
                "cariName":company.name,
                "companyId":id,
                "adres":company.address,
                "mikroDBName":request.user.profile.sourceCompany.mikroDBName
                        }
            
        updateMikro(data,"update_to_mikro_billing")
        
        return HttpResponse(status=204)

class BillingCreateMikroView(LoginRequiredMixin, View):
    def get(self, request, id, hesapKodu, *args, **kwargs):
        tag = _("Get updates")
        
        elementTag = "companyCreateMikro"
        elementTagSub = "companyPartCreateMikro"
        elementTagId = id
        
        company = get_object_or_404(Billing, id = id)
        
        if company.hesapKodu:
            cariKod = company.hesapKodu.replace(".","_")
        else:
            cariKod = "xxxx"
            
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "cariKod" : cariKod
        }
        return render(request, 'card/create_mikro_company.html', context)
    
    def post(self, request, id, hesapKodu, *args, **kwargs):
        company = get_object_or_404(Billing, id = id)
        cariKod = company.hesapKodu
        
        countryTR = Country.objects.select_related().filter(id = 205).first()
        
        cariBasKod = "120"
        
        if company.country == countryTR:
            cariOrtaKod = "01"
        else:
            cariOrtaKod = "02"
            
        if company.address:
            address = company.address
        else:
            address = ""
        
        data = {
            "type":"billing",
            "cariBasKod":cariBasKod,
            "cariOrtaKod":cariOrtaKod,
            "cariName":company.name,
            "companyId":id,
            "adres":address,
            "mikroDBName":request.user.profile.sourceCompany.mikroDBName
                        }
            
        createMikro(data,"create_mikro")
        
        return HttpResponse(status=204)

def get_cities(request):
    country_id = request.GET.get('country')
    cities = City.objects.filter(country = country_id)
    city_list = [{'id': city.id, 'name': city.name} for city in cities]
    return JsonResponse({'cities': city_list})