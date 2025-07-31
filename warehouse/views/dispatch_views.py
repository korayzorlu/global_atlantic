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

from datetime import datetime

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpProject'

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

def reloadTable(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "reload_table",
            "message": message,
            "location" : location
        }
    )
    
class DispatchDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Dispatches")
        elementTag = "dispatch"
        elementTagSub = "dispatchPart"
        
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

        return render(request, 'warehouse/dispatch/dispatches.html', context)

class DispatchAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Dispatch")
        elementTag = "dispatch"
        elementTagSub = "dispatchPart"
        
        pageLoad(request,0,100,"false")
        
        form = DispatchForm(request.POST or None, request.FILES or None, user = request.user)
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
        
        return render(request, 'warehouse/dispatch/dispatch_add.html', context)
    
    def post(self, request, *args, **kwargs):
        pageLoad(request,0,100,"false")
        form = DispatchForm(request.POST, request.FILES or None, user = request.user)
        
        if form.is_valid():
            dispatch = form.save(commit = False)
            dispatch.sourceCompany = request.user.profile.sourceCompany
            
            identificationCode = request.user.profile.sourceCompany.saleRequestCode
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastDispatch = Dispatch.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            pageLoad(request,20,100,"false")
            
            if lastDispatch:
                lastCode = lastDispatch.code
            else:
                lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            dispatch.code = code
            
            dispatch.yearCode = yearCode
            
            dispatchNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
            dispatch.dispatchNo = dispatchNo
            
            pageLoad(request,60,100,"false")
            dispatch.save()

            pageLoad(request,100,100,"true")

            return HttpResponse(status=204)
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'warehouse/dispatch/dispatch_add.html', context)
        


class DispatchUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Dispatch Detail")
        elementTag = "dispatch"
        elementTagSub = "dispatchPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        dispatches = Dispatch.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        pageLoad(request,20,100,"false")
        dispatch = get_object_or_404(Dispatch, id = id)
        pageLoad(request,80,100,"false")
        
        form = DispatchForm(request.POST or None, request.FILES or None, instance = dispatch, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "dispatches" : dispatches,
                "dispatch" : dispatch,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'warehouse/dispatch/dispatch_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "dispatch"
        elementTagSub = "dispatchPart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        dispatch = get_object_or_404(Dispatch, id = id)
        sourceCompany = dispatch.sourceCompany
        user = dispatch.user
        sessionKey = dispatch.sessionKey
        pageLoad(request,20,100,"false")
        form = DispatchForm(request.POST, request.FILES or None, instance = dispatch, user = request.user)
        if form.is_valid():
            dispatch = form.save(commit = False)
            dispatch.sourceCompany = sourceCompany
            dispatch.user = user
            dispatch.sessionKey = sessionKey
            dispatch.save()
            
            pageLoad(request,100,100,"true")
            
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

class DispatchDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Dispatch")
        elementTag = "dispatch"
        elementTagSub = "dispatchPart"
        
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
        
        return render(request, 'warehouse/dispatch/dispatch_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            dispatch = get_object_or_404(Dispatch, id = int(id))
            pageLoad(request,90,100,"false")
            dispatch.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)