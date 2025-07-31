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

from source.models import Company as SourceCompany
from account.models import ProformaInvoice, CommericalInvoice, SendInvoice,ProcessStatus
from warehouse.models import Warehouse
from warehouse.models import Item as WarehouseItem
from warehouse.models import ItemGroup as WarehouseItemGroup

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
    
def updateDetail(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "update_detail",
            "message": message,
            "location" : location
        }
    )
    
class PurchaseOrderDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Purchase Orders")
        elementTag = "purchasingPurchaseOrder"
        elementTagSub = "purchasingPurchaseOrderPart"
        
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

        return render(request, 'purchasing/purchase_order/purchase_orders.html', context)

class PurchaseOrderAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Purchase Order")
        
        elementTag = "purchaseOrderAdd"
        elementTagSub = "purchaseOrderPartInAdd"
        elementTagId = id
        
        inquiry = Inquiry.objects.select_related().filter(id = id).first()
        
        inquiries = Inquiry.objects.select_related("project","supplier","currency").filter(project = inquiry.project)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "inquiry" : inquiry,
                "inquiries" : inquiries,
                "sessionKey" : request.session.session_key
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'purchasing/purchase_order/purchase_order_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        
        inquiryId = request.POST.get("purchasingPurchaseOrderSupplier")
        
        if not inquiryId:
            data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"At least one inquiry must be selected!"
                }
            
            sendAlert(data,"default")
        
        identificationCode = request.user.profile.sourceCompany.salePurchaseOrderCode
        yearCode = int(str(datetime.today().date().year)[-2:])
        startCodeValue = 1
        
        lastPurchaseOrder = PurchaseOrder.objects.filter(
            sourceCompany = request.user.profile.sourceCompany,
            yearCode = yearCode
        ).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
        
        if lastPurchaseOrder:
            lastCode = lastPurchaseOrder.code
        else:
            lastCode = startCodeValue - 1
            
        code = int(lastCode) + 1
        
        purchaseOrderNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
    
        inquiry = get_object_or_404(Inquiry, id = inquiryId)
        
        if inquiry.purchasing_purchase_order_inquiry.first():
            data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"It has purchase order!"
                }
            
            sendAlert(data,"default")
        
        items = inquiry.inquiryitem_set.all()
        
        purchaseOrder = PurchaseOrder.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            code = code,
            yearCode = yearCode,
            purchaseOrderNo = purchaseOrderNo,
            project = inquiry.project,
            inquiry = inquiry,
            currency = inquiry.currency,
            sessionKey = request.session.session_key,
            user = request.user
        )
        
        purchaseOrder.save()
        
        project = purchaseOrder.project
        project.stage = "purchase_order"
        project.save()
        
        items = inquiry.inquiryitem_set.all()
        
        for item in items:
            purchaseOrderItem = PurchaseOrderItem.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                user = request.user,
                sessionKey = request.session.session_key,
                purchaseOrder = purchaseOrder,
                inquiryItem = item,
                name = item.projectItem.name,
                description = item.projectItem.description,
                unit = item.projectItem.unit,
                quantity = item.quantity,
                unitPrice = item.unitPrice,
                totalPrice = item.totalPrice,
                availability = item.availability,
                availabilityType = item.availabilityType,
                sequency = item.sequency
            )
            
            purchaseOrderItem.save()
        
        purchaseOrderItems = PurchaseOrderItem.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder).order_by("inquiryItem__sequency")
        sequencyCount = 0
        for purchaseOrderItem in purchaseOrderItems:
            purchaseOrderItem.sequency = sequencyCount + 1
            purchaseOrderItem.save()
            sequencyCount = sequencyCount + 1
        
        purchaseOrderPdfInTask.delay(purchaseOrder.id,request.user.profile.sourceCompany.id)
        
        #process status oluştur
        identificationCode = "PS"
        yearCode = int(str(datetime.today().date().year)[-2:])
        startCodeValue = 1
        
        lastProcessStatus = ProcessStatus.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
        
        if lastProcessStatus:
            lastCode = lastProcessStatus.code
        else:
            lastCode = startCodeValue - 1
        
        code = int(lastCode) + 1
        processStatusNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        
        processStatus = ProcessStatus.objects.create(
            user = request.user,
            sourceCompany = request.user.profile.sourceCompany,
            code = code,
            yearCode = yearCode,
            processStatusNo = processStatusNo,
            purchasingProject = purchaseOrder.project,
            type = "purchasing"
        )
        
        processStatus.save()
        #process status oluştur-end
        
        return HttpResponse(status=204)
    
class PurchaseOrderUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Purchase Order Detail")
        elementTag = "purchasingPurchaseOrder"
        elementTagSub = "purchasingPurchaseOrderPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        purchaseOrders = PurchaseOrder.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        purchaseOrder = get_object_or_404(PurchaseOrder, id = id)
        
        items = PurchaseOrderItem.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)
        pageLoad(request,20,100,"false")
        itemsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
        itemsTotal = 0
        
        for index, item in enumerate(items):
            percent = (60/len(items)) * (index + 1)
            pageLoad(request,20+percent,100,"false")
            itemsTotal  = itemsTotal + item.totalPrice
            itemsTotals["totalUnitPrice1"] = itemsTotals["totalUnitPrice1"] + item.unitPrice
            itemsTotals["totalUnitPrice2"] = itemsTotals["totalUnitPrice2"] + item.unitPrice
            itemsTotals["totalUnitPrice3"] = itemsTotals["totalUnitPrice3"] + item.unitPrice
            itemsTotals["totalTotalPrice1"] = itemsTotals["totalTotalPrice1"] + item.totalPrice
            itemsTotals["totalTotalPrice2"] = itemsTotals["totalTotalPrice2"] + item.totalPrice
            itemsTotals["totalTotalPrice3"] = itemsTotals["totalTotalPrice3"] + item.totalPrice
        
        if purchaseOrder.discountAmount > 0:
            itemsTotals["totalDiscount"] = purchaseOrder.discountAmount
        else:
            itemsTotals["totalDiscount"] = itemsTotals["totalTotalPrice3"] * (purchaseOrder.discount/100)
        itemsTotals["totalFinal"] = itemsTotals["totalTotalPrice3"] - itemsTotals["totalDiscount"]
        
        # Para miktarını belirtilen formatta gösterme
        totalBuyingPriceFixed = "{:,.2f}".format(round(itemsTotals["totalTotalPrice3"],2))
        totalDiscountPriceFixed = "{:,.2f}".format(round(itemsTotals["totalDiscount"],2))
        totalTotalPriceFixed = "{:,.2f}".format(round(itemsTotals["totalFinal"],2))
        # Nokta ile virgülü değiştirme
        totalBuyingPriceFixed = totalBuyingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalDiscountPriceFixed = totalDiscountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalTotalPriceFixed = totalTotalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        form = PurchaseOrderForm(request.POST or None, request.FILES or None, instance = purchaseOrder)
        pageLoad(request,90,100,"false")
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "purchaseOrders" : purchaseOrders,
                "purchaseOrder" : purchaseOrder,
                "itemsTotals" : itemsTotals,
                "totalBuyingPriceFixed" : totalBuyingPriceFixed,
                "totalDiscountPriceFixed" : totalDiscountPriceFixed,
                "totalTotalPriceFixed" : totalTotalPriceFixed,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'purchasing/purchase_order/purchase_order_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "purchasingPurchaseOrder"
        elementTagSub = "purchasingPurchaseOrderPart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        purchaseOrder = get_object_or_404(PurchaseOrder, id = id)
        project = purchaseOrder.project
        inquiry = purchaseOrder.inquiry
        identificationCode = purchaseOrder.identificationCode
        code = purchaseOrder.code
        yearCode = purchaseOrder.yearCode
        purchaseOrderNo = purchaseOrder.purchaseOrderNo
        sessionKey = purchaseOrder.sessionKey
        user = purchaseOrder.user
        sourceCompany = purchaseOrder.sourceCompany
        pageLoad(request,20,100,"false")
        form = PurchaseOrderForm(request.POST, request.FILES or None, instance = purchaseOrder)

        if form.is_valid():
            purchaseOrder = form.save(commit = False)
            purchaseOrder.sourceCompany = sourceCompany
            purchaseOrder.project = project
            purchaseOrder.inquiry = inquiry
            purchaseOrder.identificationCode = identificationCode
            purchaseOrder.code = code
            purchaseOrder.yearCode = yearCode
            purchaseOrder.purchaseOrderNo = purchaseOrderNo
            purchaseOrder.sessionKey = sessionKey
            purchaseOrder.user = user
            
            if not purchaseOrder.discount:
                purchaseOrder.discount = 0
                
            if not purchaseOrder.discountAmount:
                purchaseOrder.discountAmount = 0
            
            items = PurchaseOrderItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)
            itemsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
            itemsTotal = 0
            
            for index, item in enumerate(items):
                percent = (60/len(items)) * (index + 1)
                pageLoad(request,20+percent,100,"false")
                itemsTotal  = itemsTotal + item.totalPrice
                itemsTotals["totalUnitPrice1"] = itemsTotals["totalUnitPrice1"] + item.unitPrice
                itemsTotals["totalUnitPrice2"] = itemsTotals["totalUnitPrice2"] + item.unitPrice
                itemsTotals["totalUnitPrice3"] = itemsTotals["totalUnitPrice3"] + item.unitPrice
                itemsTotals["totalTotalPrice1"] = itemsTotals["totalTotalPrice1"] + item.totalPrice
                itemsTotals["totalTotalPrice2"] = itemsTotals["totalTotalPrice2"] + item.totalPrice
                itemsTotals["totalTotalPrice3"] = itemsTotals["totalTotalPrice3"] + item.totalPrice
            
            if purchaseOrder.discountAmount > 0:
                itemsTotals["totalDiscount"] = purchaseOrder.discountAmount
            else:
                itemsTotals["totalDiscount"] = itemsTotals["totalTotalPrice3"] * (purchaseOrder.discount/100)
            itemsTotals["totalFinal"] = itemsTotals["totalTotalPrice3"] - itemsTotals["totalDiscount"]
            
            purchaseOrder.totalDiscountPrice = round(itemsTotals["totalDiscount"],2)
            purchaseOrder.totalTotalPrice = round(itemsTotals["totalFinal"],2)
            purchaseOrder.save()
            
            # Para miktarını belirtilen formatta gösterme
            totalBuyingPriceFixed = "{:,.2f}".format(round(itemsTotals["totalTotalPrice3"],2))
            totalDiscountPriceFixed = "{:,.2f}".format(round(purchaseOrder.totalDiscountPrice,2))
            totalTotalPriceFixed = "{:,.2f}".format(round(purchaseOrder.totalTotalPrice,2))
            # Nokta ile virgülü değiştirme
            totalBuyingPriceFixed = totalBuyingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalDiscountPriceFixed = totalDiscountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalTotalPriceFixed = totalTotalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            totalPrices = {"purchaseOrder":purchaseOrder.id,
                            "totalBuyingPrice":totalBuyingPriceFixed,
                            "totalDiscountPrice":totalDiscountPriceFixed,
                            "totalTotalPrice":totalTotalPriceFixed,
                            "currency":purchaseOrder.currency.symbol}
            
            updateDetail(totalPrices,"purchasing_purchase_order_update")
        
            pageLoad(request,90,100,"false")
            #purchaseOrderPdf(theRequest, purchaseOrder)
            purchaseOrderPdfInTask.delay(purchaseOrder.id,request.user.profile.sourceCompany.id)
            #purchaseOrderPdf(purchaseOrder.id)
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

   
class PurchaseOrderDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Purchase Orders")
        elementTag = "purchasingPurchaseOrder"
        elementTagSub = "purchasingPurchaseOrderPart"
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

        return render(request, 'purchasing/purchase_order/purchase_order_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList): 
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            purchaseOrder = get_object_or_404(PurchaseOrder, id = id)
            
            project = purchaseOrder.project
            
            #process status sil
            processStatus = purchaseOrder.project.process_status_purchasing_project.first()
            if processStatus:
                processStatus.delete()
            #process status sil-end
            
            purchaseOrder.delete()
            
            project.stage = "inquiry"
            project.save()
            
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)

class PurchaseOrderPdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Purchase Order PDF")
        
        elementTag = "purchasingPurchaseOrder"
        elementTagSub = "purchasingPurchaseOrderPart"
        elementTagId = str(id) + "-pdf"
        
        pageLoad(request,0,100,"false")
        
        purchaseOrder = get_object_or_404(PurchaseOrder, id = id)
        pageLoad(request,50,100,"false")
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #orderConfirmationPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "purchaseOrder" : purchaseOrder,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'purchasing/purchase_order/purchase_order_pdf.html', context)

class PurchaseOrderDocumentView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        elementTag = "purchasingPurchaseOrder"
        elementTagSub = "purchasingPurchaseOrderPart"
        elementTagId = id
        
        purchaseOrders = PurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        purchaseOrder = PurchaseOrder.objects.filter(id = id).first()
        
        purchaseOrderDocuments = PurchaseOrderDocument.objects.filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)

        documents = PurchaseOrderDocument.objects.filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)
        
        purchaseOrderDocumentForm = PurchaseOrderDocumentForm(request.POST or None, request.FILES or None)
        context = {
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "purchaseOrderDocumentForm" : purchaseOrderDocumentForm,
                "purchaseOrders" : purchaseOrders,
                "purchaseOrder" : purchaseOrder,
                "purchaseOrderDocuments" : purchaseOrderDocuments,
                "documents" : documents,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'purchasing/purchase_order/purchase_order_document.html', context)

class PurchaseOrderDocumentAddView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        purchaseOrder = PurchaseOrder.objects.filter(id=id).first()
        pageLoad(request,20,100,"false")
        purchaseOrderDocument = PurchaseOrderDocument.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            sessionKey = request.session.session_key,
            purchaseOrder = purchaseOrder,
            file = request.FILES.get("file")
        )
        pageLoad(request,90,100,"false")
        purchaseOrderDocument.save()
        pageLoad(request,100,100,"true")
        return HttpResponse(status=204)

class PurchaseOrderDocumentDeleteView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        
        purchaseOrderDocument = PurchaseOrderDocument.objects.get(id = id)
        purchaseOrderDocument.delete()
            
        return HttpResponse(status=204)

class PurchaseOrderDocumentPdfView(LoginRequiredMixin, View):
    def get(self, request, id, name, *args, **kwargs):
        tag = _("Purchase Order Document PDF")
        
        elementTag = "purchasingPurchaseOrder"
        elementTagSub = "purchasingPurchaseOrderPart"
        elementTagId = str(id) + "-pdf"
        
        pageLoad(request,0,100,"false")
        
        purchaseOrderDocument = PurchaseOrderDocument.objects.get(id = id, name = name)
        purchaseOrder = purchaseOrderDocument.purchaseOrder
        pageLoad(request,50,100,"false")
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "purchaseOrderDocument" : purchaseOrderDocument,
                "purchaseOrder" : purchaseOrder,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'purchasing/purchase_order/purchase_order_document_pdf.html', context)

class PurchaseOrderItemPlaceView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Purchase Order Item Place")
        
        elementTag = "purchaseOrderItemPlace"
        elementTagSub = "purchaseOrderItemPlacePart"
        
        purchaseOrderItem = PurchaseOrderItem.objects.select_related("inquiryItem__projectItem__part").filter(id = int(request.GET.get("iii"))).first()
        part = purchaseOrderItem.inquiryItem.projectItem.part
        
        partUnique = str(part.partUnique) + "." + str(part.partUniqueCode).zfill(3)

        theWarehouses = Warehouse.objects.filter(sourceCompany = request.user.profile.sourceCompany)

        warehouses = []

        for warehouse in theWarehouses:
            partsInStock = WarehouseItem.objects.filter(part = part,warehouse = warehouse)
            stock = sum(partInStock.quantity for partInStock in partsInStock)
            warehouses.append({
                "id" : warehouse.id,
                "code" : warehouse.code,
                "name" : warehouse.name,
                "stock" : stock
            })

        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "purchaseOrderItem" : purchaseOrderItem,
                "part" : part,
                "partUnique" : partUnique,
                "warehouses" : warehouses,
                "sessionKey" : request.session.session_key
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'purchasing/purchase_order/purchase_order_item_place.html', context)
    
    def post(self, request, *args, **kwargs):
        pageLoad(request,0,100,"false")
        purchaseOrderItem = PurchaseOrderItem.objects.select_related("inquiryItem__projectItem__part").filter(id = int(request.GET.get("iii"))).first()
        
        warehouse = Warehouse.objects.select_related().filter(id = int(request.GET.get("w"))).first()
        
        #####part item process#####
        pageLoad(request,20,100,"false")
        
        identificationCode = "I"
        yearCode = int(str(datetime.today().date().year)[-2:])
        startCodeValue = 1
        
        lastItem = WarehouseItem.objects.filter(sourceCompany = request.user.profile.sourceCompany).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
        
        if lastItem:
            lastCode = lastItem.code
        else:
            lastCode = startCodeValue - 1
        
        code = int(lastCode) + 1
        
        #date = datetime.strftime(timezone.now().date(), "%d%m%y")
        date = datetime.strftime(timezone.now().date(), "%d%m%y")

        itemNo = str(identificationCode) + "-" + str(code) + "-" + str(date)
        
        partItem = WarehouseItem.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            sessionKey = request.session.session_key,
            unit = purchaseOrderItem.inquiryItem.projectItem.part.unit,
            name = purchaseOrderItem.inquiryItem.projectItem.part.partNo,
            description = purchaseOrderItem.inquiryItem.projectItem.part.description,
            category = "part",
            code = code,
            itemNo = itemNo,
            warehouse = warehouse,
            quantity = purchaseOrderItem.quantity,
            part = purchaseOrderItem.inquiryItem.projectItem.part,
            location = str(request.GET.get("l")),
            buyingPrice = purchaseOrderItem.unitPrice,
            cost = float(Decimal(str(purchaseOrderItem.unitPrice)) + ((Decimal(str(purchaseOrderItem.purchaseOrder.customsDuty)) + Decimal(str(purchaseOrderItem.purchaseOrder.additionalCustomsDuty)) + Decimal(str(purchaseOrderItem.purchaseOrder.stampDuty)))/Decimal(str(purchaseOrderItem.quantity)))),
            purchaseOrderItem = purchaseOrderItem
        )

        partItem.save()
        
        pageLoad(request,60,100,"false")
        
        partItemGroupCheck = WarehouseItemGroup.objects.filter(part = partItem.part).first()
        
        if partItemGroupCheck:
            partItemGroup = partItemGroupCheck
            partItemGroup.quantity = partItemGroup.quantity + partItem.quantity
            partItemGroup.save()
            
            partItem.itemGroup = partItemGroup
            partItem.save()
        else:
            partItemGroup = WarehouseItemGroup.objects.create(
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
        #####part item process-end#####

        purchaseOrderItem.placed = True
        purchaseOrderItem.save()
        
        messageDict = {"purchaseOrder":purchaseOrderItem.purchaseOrder.id}
                
        updateDetail(messageDict,"purchase_order_item_place")
        
        return HttpResponse(status=204)

