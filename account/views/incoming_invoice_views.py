from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa
from django.template.loader import get_template 
import json
from itertools import chain
import xmltodict
import requests as rs
from django.utils import timezone
from datetime import datetime, timedelta

from ..forms import *
from ..tasks import *
from ..pdfs.incoming_invoice_pdfs import *
from ..utils.payment_utils import *
from ..utils.incoming_invoice_utils import *

from sale.models import OrderTracking, OrderConfirmation, Collection, CollectionPart, Delivery,Inquiry
from source.models import Company as SourceCompany
from source.models import Bank as SourceBank
from service.models import Offer
from card.models import Current
from data.models import Part
from purchasing.models import PurchaseOrder as PurchasingPurchaseOrder
from purchasing.models import PurchaseOrderItem as PurchasingPurchaseOrderItem
from warehouse.models import Warehouse
from warehouse.models import Item as WarehouseItem
from warehouse.models import ItemGroup as WarehouseItemGroup

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

class IncomingInvoiceDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Incoming Invoice")
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
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
        return render(request, 'account/incoming_invoice/incoming_invoices.html', context)
    
class IncomingInvoiceManualAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Incoming Invoice")
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = "new"
        pageLoad(request,0,100,"false")
        form = IncomingInvoiceForm(request.POST or None, request.FILES or None, user=request.user)
        
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
        return render(request, 'account/incoming_invoice/incoming_invoice_add_manual.html', context)
    
    def post(self, request, *args, **kwargs):
        pageLoad(request,0,100,"false")
        form = IncomingInvoiceForm(request.POST, request.FILES or None,user=request.user)
        
        if form.is_valid():
            incomingInvoice = form.save(commit = False)
            incomingInvoice.sourceCompany = request.user.profile.sourceCompany
            
            incomingInvoice.customer = incomingInvoice.seller
            incomingInvoice.exchangeRate = incomingInvoice.currency.forexBuying
            incomingInvoice.save()
            
            #current güncelleme
            sendInvoices = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,customer = incomingInvoice.seller, currency = incomingInvoice.currency)
            incomingInvoices = IncomingInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,seller = incomingInvoice.seller, currency = incomingInvoice.currency)
            pageLoad(request,20,100,"false")
            sendInvoiceTotal = 0
            for sendInvoice in sendInvoices:
                sendInvoiceTotal = sendInvoiceTotal + sendInvoice.totalPrice
            incomingInvoiceTotal = 0
            for incomingInvoice in incomingInvoices:
                incomingInvoiceTotal = incomingInvoiceTotal + incomingInvoice.totalPrice
    
            invoiceTotal = sendInvoiceTotal - incomingInvoiceTotal
            pageLoad(request,40,100,"false")  
            current = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,company = incomingInvoice.seller, currency = incomingInvoice.currency).first()
            if current:
                current.debt = invoiceTotal
                current.save()
            else:
                current = Current.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    company = incomingInvoice.seller,
                    currency = incomingInvoice.currency
                )
                current.save()
                current.credit = invoiceTotal
                current.save()
            pageLoad(request,80,100,"false")
            incomingInvoice.seller.debt = invoiceTotal
            incomingInvoice.seller.save()
            #current güncelleme-end
            pageLoad(request,100,100,"true")
            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)
    
class IncomingInvoiceAddView(LoginRequiredMixin, View):
    def get(self, request, type, id, *args, **kwargs):
        tag = _("Add Incoming Invoice")
        
        elementTag = "incomingInvoiceAdd"
        elementTagSub = "incomingInvoicePartInAdd"
        elementTagId = id
        
        if type == "order":
            purchaseOrder = get_object_or_404(PurchaseOrder, id = id)
        elif type == "purchasing":
            purchaseOrder = get_object_or_404(PurchasingPurchaseOrder, id = id)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "purchaseOrder" : purchaseOrder,
                "type" : type
        }
        return render(request, 'account/incoming_invoice/incoming_invoice_add.html', context)
    
    def post(self, request, type, id, *args, **kwargs):
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = id

        try:
            if type == "order":
                purchaseOrder = get_object_or_404(PurchaseOrder, id = id)
                
                parts = PurchaseOrderPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)
                customerSource = SourceCompany.objects.filter(id = request.user.profile.sourceCompany.id).first()
                
                incomingInvoice = IncomingInvoice.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    project = purchaseOrder.project,
                    theRequest = purchaseOrder.inquiry.theRequest,
                    purchaseOrder = purchaseOrder,
                    seller = purchaseOrder.inquiry.supplier,
                    #customer = purchaseOrder.inquiry.theRequest.customer,
                    customer = purchaseOrder.inquiry.supplier,
                    customerSource = customerSource,
                    deliveryNote = purchaseOrder.delivery,
                    exchangeRate = purchaseOrder.currency.forexBuying,
                    currency = purchaseOrder.currency,
                    group = "order"
                )
                
                purchaseOrder.invoiced = True
                purchaseOrder.incomingInvoiced = True
                purchaseOrder.save()
                
                incomingInvoice.save()
                
                expenses = IncomingInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = incomingInvoice)
                partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
                
                partsTotal = 0
                
                for part in parts:
                    incomingInvoicePart = IncomingInvoiceItem.objects.create(
                        sourceCompany = request.user.profile.sourceCompany,
                        user = request.user,
                        invoice = incomingInvoice,
                        purchaseOrderPart = part,
                        part = part.inquiryPart.requestPart.part,
                        name = part.inquiryPart.requestPart.part.partNo,
                        description = part.inquiryPart.requestPart.part.description,
                        unit = part.inquiryPart.requestPart.part.unit,
                        quantity = part.quantity,
                        sequency = part.sequency,
                        unitPrice = part.unitPrice,
                        totalPrice = part.totalPrice
                    )
                    incomingInvoicePart.save()
                
                incomingInvoiceParts = IncomingInvoicePart.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = incomingInvoice).order_by("purchaseOrderPart__sequency")
                sequencyCount = 0
                for incomingInvoicePart in incomingInvoiceParts:
                    incomingInvoicePart.sequency = sequencyCount + 1
                    incomingInvoicePart.save()
                    sequencyCount = sequencyCount + 1

                items = incomingInvoice.incominginvoiceitem_set.all()
                expenses = incomingInvoice.incominginvoiceexpense_set.all()
                incoming_invoice_price_fix(incomingInvoice, items, expenses)
                
                incomingInvoice.paymentDate = timezone.now() + timedelta(days=incomingInvoice.seller.creditPeriod)
                incomingInvoice.save()
                
                invoicedList = []
                purchaseOrders = PurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderConfirmation = purchaseOrder.orderConfirmation)
                for po in purchaseOrders:
                    if po.invoiced == True:
                        invoicedList.append(True)
                    else:
                        invoicedList.append(False)
                
                orderConfirmation = OrderConfirmation.objects.get(id = purchaseOrder.orderConfirmation.id)
                if all(invoicedList) and orderConfirmation.sendInvoiced == True:
                    orderConfirmation.status = "invoiced"
                    orderConfirmation.save()
                    project = orderConfirmation.project
                    project.stage = "invoiced"
                    project.save()
                    
                #####proje fatura durum kontrolü#####
                orderTracking = OrderTracking.objects.get(project = orderConfirmation.project)
                incomingInvoiceCheckList = []
                for purchaseOrder in purchaseOrders:
                    incomingInvoiceCheckList.append(purchaseOrder.incomingInvoiced)
                if all(value for value in incomingInvoiceCheckList) and orderConfirmation.sendInvoiced == True:
                    orderConfirmation.status = "invoiced"
                    orderTracking.invoiced = True
                    orderTracking.save()
                    project = orderConfirmation.project
                    project.stage = "invoiced"
                    project.save()
                
                orderConfirmation.invoiced = True
                orderConfirmation.save()
                #####proje fatura durum kontrolü-end#####
                
                
                incomingInvoicePdfTask.delay(request.user.profile.sourceCompany.id, incomingInvoice.id,request.build_absolute_uri(),elementTag)

                return HttpResponse(status=204)
            elif type == "purchasing":
                purchaseOrder = get_object_or_404(PurchasingPurchaseOrder, id = id)
                items = PurchasingPurchaseOrderItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)
                customerSource = SourceCompany.objects.filter(id = request.user.profile.sourceCompany.id).first()
                
                incomingInvoice = IncomingInvoice.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    purchasingProject = purchaseOrder.project,
                    purchasingPurchaseOrder = purchaseOrder,
                    seller = purchaseOrder.inquiry.supplier,
                    #customer = purchaseOrder.inquiry.theRequest.customer,
                    customer = purchaseOrder.inquiry.supplier,
                    customerSource = customerSource,
                    deliveryNote = purchaseOrder.delivery,
                    exchangeRate = purchaseOrder.currency.forexBuying,
                    currency = purchaseOrder.currency,
                    group = "purchasing"
                )
                
                purchaseOrder.invoiced = True
                purchaseOrder.incomingInvoiced = True
                purchaseOrder.save()
                
                incomingInvoice.save()

                expenses = IncomingInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = incomingInvoice)

                for item in items:
                    incomingInvoiceItem = IncomingInvoiceItem.objects.create(
                        sourceCompany = request.user.profile.sourceCompany,
                        user = request.user,
                        invoice = incomingInvoice,
                        purchasingPurchaseOrderItem = item,
                        part = item.inquiryItem.projectItem.part,
                        name = item.inquiryItem.projectItem.part.partNo,
                        description = item.inquiryItem.projectItem.part.description,
                        unit = item.inquiryItem.projectItem.part.unit,
                        quantity = item.quantity,
                        sequency = item.sequency,
                        unitPrice = item.unitPrice,
                        totalPrice = item.totalPrice
                    )
                    incomingInvoiceItem.save()
                
                incomingInvoiceItems = IncomingInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = incomingInvoice).order_by("purchasingPurchaseOrderItem__sequency")
                sequencyCount = 0
                for incomingInvoiceItem in incomingInvoiceItems:
                    incomingInvoiceItem.sequency = sequencyCount + 1
                    incomingInvoiceItem.save()
                    sequencyCount = sequencyCount + 1

                items = incomingInvoice.incominginvoiceitem_set.all()
                expenses = incomingInvoice.incominginvoiceexpense_set.all()
                incoming_invoice_price_fix(incomingInvoice, items, expenses)
                
                incomingInvoice.paymentDate = timezone.now() + timedelta(days=incomingInvoice.seller.creditPeriod)
                incomingInvoice.save()

                invoicedList = []
                purchaseOrders = PurchasingPurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,project = purchaseOrder.project)
                for po in purchaseOrders:
                    if po.invoiced == True:
                        invoicedList.append(True)
                    else:
                        invoicedList.append(False)
                
                purchasingProject = PurchasingProject.objects.get(id = purchaseOrder.project.id)
                if all(invoicedList):
                    purchasingProject.stage = "invoiced"
                    purchasingProject.save()
                    
                
                
                #####proje fatura durum kontrolü#####
                incomingInvoiceCheckList = []
                for purchaseOrder in purchaseOrders:
                    incomingInvoiceCheckList.append(purchaseOrder.incomingInvoiced)
                if all(value for value in incomingInvoiceCheckList):
                    purchasingProject = purchaseOrder.project
                    purchasingProject.stage = "invoiced"
                    purchasingProject.save()
                #####proje fatura durum kontrolü-end#####
                
                incomingInvoicePdfTask.delay(request.user.profile.sourceCompany.id, incomingInvoice.id,request.build_absolute_uri(),elementTag)

                return HttpResponse(status=204)
        except Exception as e:
            print(e)
class IncomingInvoiceBulkAddView(LoginRequiredMixin, View):
    def get(self, request, list, type, *args, **kwargs):
        tag = _("Add Incoming Invoice")
        
        idList = list.split(",")
        purchaseOrders = []
        for id in idList:
            if type == "order":
                purchaseOrders.append(PurchaseOrder.objects.get(id = id))
            elif type == "purchasing":
                purchaseOrders.append(PurchasingPurchaseOrder.objects.get(id = id))
        
        context = {
                "tag": tag,
                "purchaseOrders" : purchaseOrders,
                "type" : type
        }
        return render(request, 'account/incoming_invoice/incoming_invoice_add_modal.html', context)
    
    def post(self, request, list, type, *args, **kwargs):
        if type == "order":
            purchaseOrder = get_object_or_404(PurchaseOrder, id = id)

        elif type == "pusrchasing":
            purchaseOrder = get_object_or_404(PurchasingPurchaseOrder, id = id)
        
        incomingInvoice = IncomingInvoice.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            project = purchaseOrder.project,
            theRequest = purchaseOrder.inquiry.theRequest,
            purchaseOrder = purchaseOrder
        )
        
        incomingInvoice.save()    
            
        return HttpResponse(status=204)
    
class IncomingInvoiceUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Incoming Invoice Detail")
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = id
        pageLoad(request,0,100,"false")
        incomingInvoices = IncomingInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        incomingInvoice = get_object_or_404(IncomingInvoice, id = id)
        #quotationParts = QuotationPart.objects.filter(quotation = orderConfirmation.quotation)
        
        parts = IncomingInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = incomingInvoice)
        pageLoad(request,20,100,"false")

        incomingInvoiceBalance = Decimal(str(incomingInvoice.totalPrice)) - Decimal(str(incomingInvoice.paidPrice))
        
        pageLoad(request,90,100,"false")
        form = IncomingInvoiceForm(request.POST or None, request.FILES or None, instance = incomingInvoice, user = request.user)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "incomingInvoices" : incomingInvoices,
                "incomingInvoice" : incomingInvoice,
                "incomingInvoiceBalance" : incomingInvoiceBalance,
                "parts" : parts,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        pageLoad(request,100,100,"true")
        return render(request, 'account/incoming_invoice/incoming_invoice_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = id

        data = {
            "block":f"message-container-{elementTag}-{elementTagId}",
            "icon":"",
            "message":"Updating invoice...",
            "stage" : "loading",
            "buttons": f"tabPane-{elementTag}-{elementTagId} .modal-header .tableTopButtons"
        }
            
        sendAlert(data,"form")

        pageLoad(request,0,100,"false")
        incomingInvoice = get_object_or_404(IncomingInvoice, id = id)
        user = incomingInvoice.user
        project = incomingInvoice.project
        theRequest = incomingInvoice.theRequest
        purchaseOrder = incomingInvoice.purchaseOrder
        purchasingProject = incomingInvoice.purchasingProject
        purchasingPurchaseOrder = incomingInvoice.purchasingPurchaseOrder
        seller = incomingInvoice.seller
        customer = incomingInvoice.customer
        incomingInvoiceNo = incomingInvoice.incomingInvoiceNo
        currency = incomingInvoice.currency
        sourceCompany = incomingInvoice.sourceCompany
        parts = IncomingInvoicePart.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = incomingInvoice)
        pageLoad(request,20,100,"false")
        form = IncomingInvoiceForm(request.POST, request.FILES or None, instance = incomingInvoice, user = request.user)

        if form.is_valid():
            if not request.POST.get("exchangeRate"):
                data = {'message': 'Please fill out the "Exchange Rate" field.'}
                return JsonResponse(data, status=404)
            incomingInvoice = form.save(commit = False)
            incomingInvoice.sourceCompany = sourceCompany
            incomingInvoice.user = user
            incomingInvoice.project = project
            incomingInvoice.purchaseOrder = purchaseOrder
            incomingInvoice.theRequest = theRequest
            incomingInvoice.purchasingProject = purchasingProject
            incomingInvoice.purchasingPurchaseOrder = purchasingPurchaseOrder
            incomingInvoice.seller = seller
            incomingInvoice.customer = customer
            incomingInvoice.currency = currency
            incomingInvoice.paymentDate = incomingInvoice.incomingInvoiceDate + timedelta(days=seller.creditPeriod)
            incomingInvoice.save()

            if incomingInvoice.purchaseOrder:
                if incomingInvoice.ready == True:
                    for part in parts:
                        collectionPart = CollectionPart.objects.get(purchaseOrderPart = part.purchaseOrderPart)
                        collectionPart.tracked = part.quantity
                        collectionPart.remaining = float(collectionPart.quantity) - float(part.quantity)
                        collectionPart.save()
                else:
                    for part in parts:
                        collectionPart = CollectionPart.objects.get(purchaseOrderPart = part.purchaseOrderPart)
                        if collectionPart.tracked > 0:
                            collectionPart.tracked = int(collectionPart.tracked) - int(part.quantity)
                            collectionPart.remaining = float(collectionPart.quantity) - float(collectionPart.tracked)
                            collectionPart.save()
            
            parts = IncomingInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = incomingInvoice)

            #order tracking remaining düzeltmesi
            if incomingInvoice.purchaseOrder:
                orderTracking = OrderTracking.objects.get(purchaseOrders = purchaseOrder)
                theCollections = Collection.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
                
                collectionPartsList = []
                for collection in theCollections:
                    collectionParts = CollectionPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,collection = collection)
                    for collectionPart in collectionParts:
                        collectionPartsList.append(collectionPart)
                            
                itemsJSON = {"parts" : {}}
                quantity = 0
                tracked = 0
                remaining = 0
                for collectionPart in collectionPartsList:
                    quantity = quantity + collectionPart.quantity
                    tracked = tracked + collectionPart.tracked
                    remaining = remaining + collectionPart.remaining
                itemsJSON["parts"] = {"quantity" : quantity, "tracked" : tracked, "remaining" : remaining}
                
                orderTracking.items = itemsJSON
                orderTracking.save()
            #order tracking remaining düzeltmesi-end

            pageLoad(request,60,100,"false")

            incomingInvoicePdfTask.delay(request.user.profile.sourceCompany.id, incomingInvoice.id,request.build_absolute_uri(),elementTag)
            
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

class IncomingInvoiceDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Invoice")
        
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        
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
        
        return render(request, 'account/incoming_invoice/incoming_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            incomingInvoice = get_object_or_404(IncomingInvoice, id = int(id))
            if incomingInvoice.paidPrice > 0:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"There is a payment attached to this invoice."
                }
            
                sendAlert(data,"default")
                return HttpResponse(status=404)
            else:
                if incomingInvoice.purchaseOrder:
                    purchaseOrder = PurchaseOrder.objects.filter(id = incomingInvoice.purchaseOrder.id).first()
                    orderConfirmation = OrderConfirmation.objects.filter(id = purchaseOrder.orderConfirmation.id).first()
                    purchaseOrder.invoiced = False
                    purchaseOrder.incomingInvoiced = False
                    purchaseOrder.save()
                
                    #####proje fatura durum kontrolü#####
                    orderTracking = OrderTracking.objects.get(project = orderConfirmation.project)
                    purchaseOrders = PurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderConfirmation = orderConfirmation)
                    incomingInvoiceCheckList = []
                    for purchaseOrder in purchaseOrders:
                        incomingInvoiceCheckList.append(purchaseOrder.incomingInvoiced)
                    orderTracking.invoiced = False
                    orderTracking.save()
                    
                    orderConfirmation.status = "collected"
                    orderConfirmation.invoiced = False
                    orderConfirmation.save()
                    project = orderConfirmation.project
                    project.stage = "order_tracking"
                    project.save()
                    #####proje fatura durum kontrolü-end#####
                
                elif incomingInvoice.purchasingPurchaseOrder:
                    purchaseOrder = PurchasingPurchaseOrder.objects.filter(id = incomingInvoice.purchasingPurchaseOrder.id).first()
                    purchaseOrder.invoiced = False
                    purchaseOrder.incomingInvoiced = False
                    purchaseOrder.save()
                
                    #####proje fatura durum kontrolü#####
                    purchaseOrders = PurchasingPurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,project = purchaseOrder.project)
                    incomingInvoiceCheckList = []
                    for purchaseOrder in purchaseOrders:
                        incomingInvoiceCheckList.append(purchaseOrder.incomingInvoiced)
                    project = purchaseOrder.project
                    project.stage = "purchase_order"
                    project.save()
                    #####proje fatura durum kontrolü-end#####

                
                incomingInvoice.delete()
                return HttpResponse(status=204)

class IncomingInvoicePdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Incoming Invoice PDF")
        
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = str(id) + "-pdf"
        
        incomingInvoice = get_object_or_404(IncomingInvoice, id = id)
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #purchaseOrderPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "incomingInvoice" : incomingInvoice,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/incoming_invoice/incoming_invoice_pdf.html', context)


class IncomingInvoicePartAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Maker Type")
        elementTagSub = "makerType"
        
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/incoming_invoice/incoming_invoice_part_add.html', context)

class IncomingInvoicePartInDetailAddView(LoginRequiredMixin, View):

    def get(self, request, id, *args, **kwargs):
        tag = _("Add Incoming Invoice Part")
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        incomingInvoiceId = refererPath.replace("/account/incoming_invoice/incoming_invoice_update/","").replace("/","")
        incomingInvoice = get_object_or_404(IncomingInvoice, id = id)
        #form = IncomingInvoicePartForm(request.POST or None, request.FILES or None)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "incomingInvoice" : incomingInvoice,
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/incoming_invoice/incoming_invoice_part_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        # refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        # requestId = refererPath.replace("/sale/request_update/","").replace("/","")
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = id
        pageLoad(request,0,100,"false")

        incomingInvoice = IncomingInvoice.objects.get(id = id)
        incomingInvoiceParts = IncomingInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = incomingInvoice)
        sequencyCount = len(incomingInvoiceParts)
        parts = []
        
        for incomingInvoicePart in incomingInvoiceParts:
            parts.append(incomingInvoicePart.part)
            
        incomingInvoiceAppendingParts = request.POST.getlist("incomingInvoiceParts")
        
        for index,item in enumerate(incomingInvoiceAppendingParts):
            part = Part.objects.get(id = int(item))
            newIncomingInvoicePart = IncomingInvoiceItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    invoice = incomingInvoice,
                    part = part,
                    name = part.partNo,
                    unit = part.unit,
                    description = part.description,
                    quantity = 1,
                    sequency = sequencyCount + 1
                )
            newIncomingInvoicePart.save()
            
            percent = (90/len(incomingInvoiceAppendingParts)) * (index + 1)
            pageLoad(request,percent,100,"false")

        pageLoad(request,100,100,"true")

        incomingInvoicePdfTask.delay(request.user.profile.sourceCompany.id, incomingInvoice.id,request.build_absolute_uri(),elementTag)

        return HttpResponse(status=204)

class IncomingInvoicePartDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Incoming Invoice")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/incoming_invoice/incoming_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        print(idList)
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            incomingInvoicePart = get_object_or_404(IncomingInvoiceItem, id = int(id))
            invoice = incomingInvoicePart.invoice
            incomingInvoicePart.delete()

        items = invoice.incominginvoiceitem_set.all()
        expenses = invoice.incominginvoiceexpense_set.all()

        incoming_invoice_price_fix(invoice, items, expenses)

        pageLoad(request,100,100,"true")

        incomingInvoicePdfTask.delay(request.user.profile.sourceCompany.id, invoice.id,request.build_absolute_uri(),elementTag)

        return HttpResponse(status=204)     

class IncomingInvoiceExpenseInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Incoming Invoice Expense ")
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        invoiceId = refererPath.replace("/account/incoming_invoice/incoming_invoice_update/","").replace("/","")
        invoice = get_object_or_404(IncomingInvoice, id = id)
        
        form = IncomingInvoiceExpenseForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "invoice" : invoice,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/incoming_invoice/incoming_invoice_expense_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        invoiceId = refererPath.replace("/account/incoming_invoice/incoming_invoice_update/","").replace("/","")
        
        invoice = IncomingInvoice.objects.get(id = id)
        incomingInvoiceExpenses = IncomingInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = invoice)
        pageLoad(request,20,100,"false")
        form = IncomingInvoiceExpenseForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            incomingInvoiceExpense = form.save(commit = False)
            incomingInvoiceExpense.sourceCompany = request.user.profile.sourceCompany
            
            incomingInvoiceExpense.user = request.user
            incomingInvoiceExpense.invoice = invoice
            incomingInvoiceExpense.save()
            pageLoad(request,100,100,"true")

            incomingInvoicePdfTask.delay(request.user.profile.sourceCompany.id, invoice.id,request.build_absolute_uri(),elementTag)

            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)

class IncomingInvoiceExpenseDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Incoming Invoice")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/send_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        elementTag = "incomingInvoice"
        elementTagSub = "incomingInvoicePart"
        elementTagId = id

        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            sendInvoiceExpense = get_object_or_404(IncomingInvoiceExpense, id = int(id))
            invoice = sendInvoiceExpense.invoice
            sendInvoiceExpense.delete()

        items = invoice.incominginvoiceitem_set.all()
        expenses = invoice.incominginvoiceexpense_set.all()

        incoming_invoice_price_fix(invoice, items, expenses)
        pageLoad(request,100,100,"true")

        incomingInvoicePdfTask.delay(request.user.profile.sourceCompany.id, invoice.id,request.build_absolute_uri(),elementTag)

        return HttpResponse(status=204)


