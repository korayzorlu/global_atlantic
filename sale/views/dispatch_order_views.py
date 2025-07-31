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
import json

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
    
class DispatchOrderDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Dispatch Orders")
        elementTag = "dispatchOrder"
        elementTagSub = "dispatchOrderPart"
        
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

        return render(request, 'sale/dispatch_order/dispatch_orders.html', context)

class DispatchOrderAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Dispatch Order")
        elementTag = "dispatchOrder"
        elementTagSub = "dispatchOrderPart"
        
        pageLoad(request,0,100,"false")

        orderTracking = OrderTracking.objects.filter(id = id).first()
        parts = CollectionPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,collection__purchaseOrder__project = orderTracking.project)


        form = DispatchOrderForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "sessionKey" : request.session.session_key,
                "orderTracking" : orderTracking,
                "parts" : parts,
                "user" : request.user,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/dispatch_order/dispatch_order_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")

        orderTracking = OrderTracking.objects.filter(id = id).first()

        idList = request.POST.getlist("collectionPart")
        print(f"idlist: {idList}")
        identificationCode = request.user.profile.sourceCompany.saleDispatchOrderCode
        yearCode = int(str(datetime.today().date().year)[-2:])
        startCodeValue = 1
        
        lastDispatchOrder = DispatchOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
        
        pageLoad(request,20,100,"false")
        
        if lastDispatchOrder:
            lastCode = lastDispatchOrder.code
        else:
            lastCode = startCodeValue - 1
        
        code = int(lastCode) + 1
        
        dispatchOrderNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        
        dispatchOrder = DispatchOrder.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            code = code,
            yearCode = yearCode,
            dispatchOrderNo = dispatchOrderNo,
            orderTracking = orderTracking,
            sessionKey = request.session.session_key,
            user = request.user
        )
        
        dispatchOrder.save()
        
        pageLoad(request,60,100,"false")

        seq = 1
        for i in idList:
            collectionPart = CollectionPart.objects.select_related("purchaseOrderPart__inquiryPart__requestPart__part").filter(id = i).first()

            dispatchOrderPart = DispatchOrderPart.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                user = request.user,
                sessionKey = request.session.session_key,
                dispatchOrder = dispatchOrder,
                maker = collectionPart.purchaseOrderPart.inquiryPart.maker,
                makerType = collectionPart.purchaseOrderPart.inquiryPart.makerType,
                collectionPart = collectionPart,
                partNo = collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.partNo,
                description = collectionPart.purchaseOrderPart.inquiryPart.requestPart.part.description,
                quantity = collectionPart.quantity,
                sequency = seq
            )
                
            dispatchOrderPart.save()

            seq += 1

        pageLoad(request,100,100,"true")

        return HttpResponse(status=204)

        


class DispatchOrderAddManualView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Dispatch Order")
        elementTag = "dispatchOrder"
        elementTagSub = "dispatchOrderPart"
        
        pageLoad(request,0,100,"false")
        
        form = DispatchOrderForm(request.POST or None, request.FILES or None, user = request.user)
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
        
        return render(request, 'sale/dispatch_order/dispatch_order_add_manual.html', context)
    
    def post(self, request, *args, **kwargs):
        pageLoad(request,0,100,"false")
        form = DispatchOrderForm(request.POST, request.FILES or None, user = request.user)
        
        if form.is_valid():
            dispatchOrder = form.save(commit = False)
            dispatchOrder.sourceCompany = request.user.profile.sourceCompany
            
            identificationCode = request.user.profile.sourceCompany.saleRequestCode
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastDispatchOrder = DispatchOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            pageLoad(request,20,100,"false")
            
            if lastDispatchOrder:
                lastCode = lastDispatchOrder.code
            else:
                lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            dispatchOrder.code = code
            
            dispatchOrder.yearCode = yearCode
            
            dispatchOrderNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
            dispatchOrder.dispatchOrderNo = dispatchOrderNo
            
            pageLoad(request,60,100,"false")
            dispatchOrder.save()

            pageLoad(request,100,100,"true")

            return HttpResponse(status=204)
        else:
            data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"At least one supplier and one part must be selected!"
                }
            
            sendAlert(data,"default")
            return HttpResponse(status=404)
        


class DispatchOrderUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Dispatch Order Detail")
        elementTag = "dispatchOrder"
        elementTagSub = "dispatchOrderPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        dispatchOrders = DispatchOrder.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        pageLoad(request,20,100,"false")
        dispatchOrder = get_object_or_404(DispatchOrder, id = id)
        pageLoad(request,80,100,"false")
        
        form = DispatchOrderForm(request.POST or None, request.FILES or None, instance = dispatchOrder, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "dispatchOrders" : dispatchOrders,
                "dispatchOrder" : dispatchOrder,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/dispatch_order/dispatch_order_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "dispatchOrder"
        elementTagSub = "dispatchOrderPart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        dispatchOrder = get_object_or_404(DispatchOrder, id = id)
        sourceCompany = dispatchOrder.sourceCompany
        user = dispatchOrder.user
        sessionKey = dispatchOrder.sessionKey
        pageLoad(request,20,100,"false")
        form = DispatchOrderForm(request.POST, request.FILES or None, instance = dispatchOrder, user = request.user)
        if form.is_valid():
            dispatchOrder = form.save(commit = False)
            dispatchOrder.sourceCompany = sourceCompany
            dispatchOrder.user = user
            dispatchOrder.sessionKey = sessionKey
            dispatchOrder.save()
            
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

class DispatchOrderDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Dispatch Order")
        elementTag = "dispatchOrder"
        elementTagSub = "dispatchOrderPart"
        
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
        
        return render(request, 'sale/dispatch_order/dispatch_order_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            dispatchOrder = get_object_or_404(DispatchOrder, id = int(id))
            pageLoad(request,90,100,"false")
            dispatchOrder.delete()
                
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)