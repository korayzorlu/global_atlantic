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

from forex_python.converter import CurrencyRates
import requests as rs
import xmltodict
import json
import pyodbc
import random
import string

import subprocess
from django.core import serializers
# Create your views here.

import telnetlib
from ..models import *
from ..forms import *

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

class AccessAuthorizationDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Access Authorizations")
        elementTag = "accessAuthorization"
        elementTagSub = "accessAuthorizationPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'administration/access_authorization/access_authorizations.html', context)

class AccessAuthorizationAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Access Authorization")
        elementTag = "accessAuthorization"
        elementTagSub = "accessAuthorizationPart"
        
        pageLoad(request,0,100,"false")
        
        form = AccessAuthorizationForm(request.POST or None, request.FILES or None)
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
        
        return render(request, 'administration/access_authorization/access_authorization_add.html', context)
    def post(self, request, *args, **kwargs):
        pageLoad(request,0,100,"false")
        form = AccessAuthorizationForm(request.POST, request.FILES or None)
        
        if form.is_valid():
            accessAuthorization = form.save(commit = False)
            accessAuthorization.user = request.user
            accessAuthorization.sessionKey = request.session.session_key
            
            if not accessAuthorization.name:
                data = {
                            "status":"secondary",
                            "icon":"triangle-exclamation",
                            "message":"Name field must be fill!"
                    }
                
                sendAlert(data,"default")
            
            accessAuthorization.save()

            pageLoad(request,100,100,"true")

            return HttpResponse(status=204)
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'administration/access_authorization/access_authorization_add.html', context)

class AccessAuthorizationUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Access Authorization Detail")
        elementTag = "accessAuthorization"
        elementTagSub = "accessAuthorizationPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        accessAuthorizations = AccessAuthorization.objects.filter()
        pageLoad(request,20,100,"false")
        accessAuthorization = get_object_or_404(AccessAuthorization, id = id)
        pageLoad(request,40,100,"false")
        pageLoad(request,60,100,"false")
        pageLoad(request,80,100,"false")
        
        # addParts = Part.objects.filter(maker = requestt.maker, type = requestt.makerType)
        # partsLength = len(addParts)
        
        form = AccessAuthorizationForm(request.POST or None, request.FILES or None, instance = accessAuthorization)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "accessAuthorizations" : accessAuthorizations,
                "accessAuthorization" : accessAuthorization,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'administration/access_authorization/access_authorization_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        accessAuthorization = get_object_or_404(AccessAuthorization, id = id)
        user = accessAuthorization.user
        sessionKey = accessAuthorization.sessionKey
        pageLoad(request,20,100,"false")
        form = AccessAuthorizationForm(request.POST, request.FILES or None, instance = accessAuthorization)
        if form.is_valid():
            accessAuthorization = form.save(commit = False)
            accessAuthorization.user = user
            accessAuthorization.sessionKey = sessionKey
            
            accessAuthorization.save()
            
            pageLoad(request,100,100,"true")
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)
  

class AccessAuthorizationDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Access Authorization")
        elementTag = "accessAuthorization"
        elementTagSub = "accessAuthorizationPart"
        
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
        
        return render(request, 'administration/access_authorization/access_authorization_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            accessAuthorization = get_object_or_404(AccessAuthorization, id = int(id))
            pageLoad(request,90,100,"false")
            accessAuthorization.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
   