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
from django.db.models import Q

from ..forms import *

from datetime import datetime

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
    
class PartItemDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Part Items")
        elementTag = "partItem"
        elementTagSub = "partItemPart"
        
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

        return render(request, 'warehouse/part_item/part_items.html', context)
    
class PartItemAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Part Item")
        elementTag = "partItem"
        elementTagSub = "partItemPart"
        elementTagId = "new"
        
        pageLoad(request,0,100,"false")
        
        form = PartItemForm(request.POST or None, request.FILES or None, user = request.user)
        
        if is_ajax(request=request):
            term = request.GET.get("term")
            parts = Part.objects.filter(
                sourceCompany = request.user.profile.sourceCompany
            ).filter(
                Q(partUnique__code__icontains = term) |
                Q(maker__name__icontains = term) |
                Q(type__type__icontains = term) |
                Q(partNo__icontains = term) |
                Q(description__icontains = term) |
                Q(techncialSpecification__icontains = term)
            )
            response_content = list(parts.values("id","partUnique__code","partUniqueCode","maker__name","type__type","partNo","description","techncialSpecification"))

            return JsonResponse(response_content, safe=False)
        
        
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
        
        return render(request, 'warehouse/part_item/part_item_add.html', context)
    
    def post(self, request, *args, **kwargs):
        elementTag = "partItem"
        elementTagSub = "partItemPart"
        elementTagId = "new"

        pageLoad(request,0,100,"false")
        form = PartItemForm(request.POST, request.FILES or None, user = request.user)
        
        if form.is_valid():
            partItem = form.save(commit = False)
            partItem.sourceCompany = request.user.profile.sourceCompany
            partItem.user = request.user
            partItem.sessionKey = request.session.session_key
            
            partItem.unit = partItem.part.unit
            partItem.name = partItem.part.partNo
            partItem.description = partItem.part.description
            
            partItem.category = "part"

            pageLoad(request,20,100,"false")
            
            identificationCode = "I"
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastItem = Item.objects.filter(sourceCompany = request.user.profile.sourceCompany).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            if lastItem:
                lastCode = lastItem.code
            else:
                lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            
            #date = datetime.strftime(timezone.now().date(), "%d%m%y")
            date = datetime.strftime(partItem.itemDate, "%d%m%y")

            itemNo = str(identificationCode) + "-" + str(code) + "-" + str(date)
            
            partItem.code = code
            partItem.itemNo = itemNo
            partItem.save()
            
            pageLoad(request,60,100,"false")
            
            partItemGroupCheck = ItemGroup.objects.filter(part = partItem.part).first()
            
            if partItemGroupCheck:
                partItemGroup = partItemGroupCheck
                partItemGroup.quantity = partItemGroup.quantity + partItem.quantity
                partItemGroup.save()
                
                partItem.itemGroup = partItemGroup
                partItem.save()
            else:
                partItemGroup = ItemGroup.objects.create(
                    sourceCompany = partItem.sourceCompany,
                    user = partItem.user,
                    sessionKey = partItem.sessionKey,
                    unit = partItem.unit,
                    name = partItem.name,
                    description = partItem.description,
                    category = partItem.category,
                    part = partItem.part,
                    barcode = partItem.barcode,
                    quantity = partItem.quantity
                )
                partItemGroup.save()
                
                partItem.itemGroup = partItemGroup
                partItem.save()

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

class PartItemUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Part Item Detail")
        elementTag = "partItem"
        elementTagSub = "partItemPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        partItems = Item.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        pageLoad(request,20,100,"false")
        partItem = get_object_or_404(Item, id = id)
        pageLoad(request,80,100,"false")
        
        partUnique = f"{partItem.part.partUnique}.{str(partItem.part.partUniqueCode).zfill(3)}"

        form = PartItemForm(request.POST or None, request.FILES or None, instance = partItem, user = request.user)

        if is_ajax(request=request):
            term = request.GET.get("term")
            parts = Part.objects.filter(
                sourceCompany = request.user.profile.sourceCompany
            ).filter(
                Q(partUnique__code__icontains = term) |
                Q(maker__name__icontains = term) |
                Q(type__type__icontains = term) |
                Q(partNo__icontains = term) |
                Q(description__icontains = term) |
                Q(techncialSpecification__icontains = term)
            )
            response_content = list(parts.values("id","partUnique__code","partUniqueCode","maker__name","type__type","partNo","description","techncialSpecification"))
            
            return JsonResponse(response_content, safe=False)

        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "partItems" : partItems,
                "partItem" : partItem,
                "partUnique" : partUnique,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'warehouse/part_item/part_item_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "partItem"
        elementTagSub = "partItemPart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        partItem = get_object_or_404(Item, id = id)
        sourceCompany = partItem.sourceCompany
        user = partItem.user
        sessionKey = partItem.sessionKey
        pageLoad(request,20,100,"false")
        form = PartItemForm(request.POST, request.FILES or None, instance = partItem, user = request.user)
        if form.is_valid():
            partItem = form.save(commit = False)
            partItem.sourceCompany = sourceCompany
            partItem.user = user
            partItem.sessionKey = sessionKey
            partItem.save()
            
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

class PartItemDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Part Item")
        elementTag = "partItem"
        elementTagSub = "partItemPart"
        
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
        
        return render(request, 'warehouse/part_item/part_item_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            partItem = get_object_or_404(Item, id = int(id))

            purchaseOrderItem = partItem.purchaseOrderItem
            purchaseOrderItem.placed = False
            purchaseOrderItem.save()

            partItemGroup = partItem.itemGroup
            partItemGroup.quantity = partItemGroup.quantity - partItem.quantity
            partItemGroup.save()

            pageLoad(request,90,100,"false")
            partItem.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
