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
    
class WarehouseDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("WArehouses")
        elementTag = "warehouse"
        elementTagSub = "warehousePart"
        
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

        return render(request, 'warehouse/warehouse/warehouses.html', context)
    
class WarehouseAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Warehouse")
        elementTag = "warehouse"
        elementTagSub = "warehousePart"
        elementTagId = "new"
        
        pageLoad(request,0,100,"false")
        
        form = WarehouseForm(request.POST or None, request.FILES or None, user = request.user)
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
        
        return render(request, 'warehouse/warehouse/warehouse_add.html', context)
    
    def post(self, request, *args, **kwargs):
        tag = _("Add Warehouse")
        elementTag = "warehouse"
        elementTagSub = "warehousePart"
        elementTagId = "new"

        pageLoad(request,0,100,"false")
        form = WarehouseForm(request.POST, request.FILES or None, user = request.user)
        
        if form.is_valid():
            warehouse = form.save(commit = False)
            warehouse.sourceCompany = request.user.profile.sourceCompany
            warehouse.user = request.user
            warehouse.sessionKey = request.session.session_key

            pageLoad(request,20,100,"false")
            
            warehouse.save()
            pageLoad(request,60,100,"false")
            warehouse.sessionKey = request.session.session_key
            warehouse.stage = "warehouse"
            warehouse.save()

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
    
class WarehouseUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Warehouse Detail")
        elementTag = "warehouse"
        elementTagSub = "warehousePart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        warehouses = Warehouse.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        pageLoad(request,20,100,"false")
        warehouse = get_object_or_404(Warehouse, id = id)
        pageLoad(request,80,100,"false")
        
        form = WarehouseForm(request.POST or None, request.FILES or None, instance = warehouse, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "warehouses" : warehouses,
                "warehouse" : warehouse,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'warehouse/warehouse/warehouse_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "warehouse"
        elementTagSub = "warehousePart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        warehouse = get_object_or_404(Warehouse, id = id)
        sourceCompany = warehouse.sourceCompany
        user = warehouse.user
        sessionKey = warehouse.sessionKey
        pageLoad(request,20,100,"false")
        form = WarehouseForm(request.POST, request.FILES or None, instance = warehouse, user = request.user)
        if form.is_valid():
            warehouse = form.save(commit = False)
            warehouse.sourceCompany = sourceCompany
            warehouse.user = user
            warehouse.sessionKey = sessionKey
            warehouse.save()
            
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

class WarehouseDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Warehouse")
        elementTag = "warehouse"
        elementTagSub = "warehousePart"
        
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
        
        return render(request, 'warehouse/warehouse/warehouse_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            warehouse = get_object_or_404(Warehouse, id = int(id))
            pageLoad(request,90,100,"false")
            warehouse.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
 