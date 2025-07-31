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

class UserAuthorizationDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("User Authorizations")
        elementTag = "userAuthorization"
        elementTagSub = "userAuthorizationPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'administration/user_authorization/user_authorizations.html', context)
    
class UserAuthorizationUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("User Authorization Detail")
        elementTag = "userAuthorization"
        elementTagSub = "userAuthorizationPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        pageLoad(request,20,100,"false")
        profile = get_object_or_404(Profile, user = id)
        pageLoad(request,40,100,"false")
        accessAuthorizations = AccessAuthorization.objects.filter().order_by("name")
        dataAuthorizations = DataAuthorization.objects.filter().order_by("name")
        profileAccessAuthorizations = profile.accessAuth.all()
        profileDataAuthorizations = profile.dataAuth.all()
        pageLoad(request,60,100,"false")
        pageLoad(request,80,100,"false")
        
        form = UserAuthorizationForm(request.POST or None, request.FILES or None, instance = profile)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "profile" : profile,
                "accessAuthorizations" : accessAuthorizations,
                "dataAuthorizations" : dataAuthorizations,
                "profileAccessAuthorizations"  :profileAccessAuthorizations,
                "profileDataAuthorizations"  :profileDataAuthorizations,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'administration/user_authorization/user_authorization_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        profile = get_object_or_404(Profile, user = id)
        pageLoad(request,20,100,"false")
        
        keyList = list(request.POST.keys())
        keyList.remove("csrfmiddlewaretoken")
        
        accessAuthorizationList = []
        dataAuthorizationList = []
        
        for item in keyList:
            if item.startswith("accessAuthorization"):
                accessAuthorizationList.append(item.split('-')[1])
            elif item.startswith("dataAuthorization"):
                dataAuthorizationList.append(item.split('-')[1])
        
        profile.accessAuth.clear()
        profile.dataAuth.clear()
        
        for item in accessAuthorizationList:
            accessAuthorization = AccessAuthorization.objects.filter(code = item).first()
            profile.accessAuth.add(accessAuthorization)
            
        for item in dataAuthorizationList:
            dataAuthorization = DataAuthorization.objects.filter(code = item).first()
            profile.dataAuth.add(dataAuthorization)
            
        profile.save()
        
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
