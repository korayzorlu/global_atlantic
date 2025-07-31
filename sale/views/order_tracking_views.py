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
from ..pdfs.request_pdfs import *
from ..pdfs.order_confirmation_pdfs import *
from ..pdfs.purchase_order_pdfs import *
from ..pdfs.order_tracking_pdfs import *
from ..pdfs.quotation_pdfs import *

from source.models import Company as SourceCompany
from account.models import ProformaInvoice, CommericalInvoice, SendInvoice,ProcessStatus

import pandas as pd
import json
import random
import string
from datetime import datetime
import time

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

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


class OrderTrackingDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Order Tracking")
        elementTag = "orderTracking"
        elementTagSub = "orderTrackingCollection"
        
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
        
        return render(request, 'sale/order_tracking/order_trackings.html', context)

class OrderTrackingAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Order Tracking")
        
        purchaseOrder = PurchaseOrder.objects.get(id = id)
        
        elementTag = "orderTrackingAdd"
        elementTagSub = "orderTrackingPartInAdd"
        elementTagId = id
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "purchaseOrder" : purchaseOrder
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/order_tracking/order_tracking_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        orderTrackingForm = OrderTrackingForm(request.POST, request.FILES or None)
        collectionForm = CollectionForm(request.POST, request.FILES or None, user = request.user)
        
        purchaseOrder = get_object_or_404(PurchaseOrder, id = id)
        
        orderTracking = OrderTracking.objects.filter(project = purchaseOrder.project).first()
        orderConfirmation = purchaseOrder.orderConfirmation
        parts = PurchaseOrderPart.objects.filter(sourceCompany = request.user.profile.sourceCompany, purchaseOrder = purchaseOrder)
        itemsJSON = {"parts" : {}}
        
        if not orderTracking:
            orderTracking = OrderTracking.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                project = purchaseOrder.project,
                theRequest = purchaseOrder.inquiry.theRequest,
                sessionKey = request.session.session_key,
                user = request.user
            )
            
            orderTracking.save()
            
            orderTracking.purchaseOrders.add(purchaseOrder)
            orderTracking.save()
            
            collection = Collection.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                orderTracking = orderTracking,
                purchaseOrder = purchaseOrder
            )
            
            collection.save()
            delivery = Delivery.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                orderTracking = orderTracking,
                orderConfirmation = orderConfirmation
            )
            
            delivery.save()
            
            quantity = 0
            tracked = 0
            remaining = 0
            for part in parts:
                collectionPart = CollectionPart.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    collection = collection,
                    purchaseOrderPart = part,
                    quantity = part.quantity,
                    remaining = part.quantity
                )
                
                collectionPart.save()
                quantity = quantity + collectionPart.quantity
                tracked = tracked + collectionPart.tracked
                remaining = remaining + collectionPart.remaining
                
            itemsJSON["parts"] = {"quantity" : quantity, "tracked" : tracked, "remaining" : remaining}
            orderTracking.items = itemsJSON
            orderTracking.save()
            #requestPdfInMedia(orderTracking.theRequest)
            #inquiryPdfInMedia(purchaseOrder.inquiry)
            #orderConfirmationPdfInMedia(orderTracking.purchaseOrders.all()[0].orderConfirmation)
            #purchaseOrderPdfInMedia(purchaseOrder)
            
        else:
            print("var")
            
            orderTracking.purchaseOrders.add(purchaseOrder)
            orderTracking.save()
            
            collection = Collection.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                orderTracking = orderTracking,
                purchaseOrder = purchaseOrder
            )
        
            collection.save()
            
            quantity = 0
            tracked = 0
            remaining = 0
            for part in parts:
                collectionPart = CollectionPart.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    collection = collection,
                    purchaseOrderPart = part,
                    quantity = part.quantity,
                    remaining = part.quantity
                )
                
                collectionPart.save()
                quantity = quantity + collectionPart.quantity
                tracked = tracked + collectionPart.tracked
                remaining = remaining + collectionPart.remaining
                
            itemsJSON["parts"] = {"quantity" : quantity, "tracked" : tracked, "remaining" : remaining}

            #inquiryPdfInMedia(purchaseOrder.inquiry)
            #orderConfirmationPdfInMedia(orderTracking.purchaseOrders.all()[0].orderConfirmation)
            #purchaseOrderPdfInMedia(purchaseOrder)
        
        orderTracking.items = itemsJSON
        orderTracking.save()
        
        project = orderTracking.project
        project.stage = "order_tracking"
        project.save()
        
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
            project = orderTracking.project,
            type = "order"
        )
        
        processStatus.save()
        #process status oluştur-end
        
        return HttpResponse(status=204)
       
class OrderTrackingUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Order Tracking Detail")
        elementTag = "orderTracking"
        elementTagSub = "orderTrackingCollection"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        orderTrackings = OrderTracking.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        orderTracking = get_object_or_404(OrderTracking, id = id)
        orderConfirmation = orderTracking.purchaseOrders.all()[0].orderConfirmation
        #quotationParts = QuotationPart.objects.filter(quotation = orderConfirmation.quotation)
        #print(orderTracking.purchaseOrders.all())
        for collection in orderTracking.collection_set.select_related('purchaseOrder'):
            print(collection)
            
        collections = []
        deliveries = []
        theCollections = Collection.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
        theDeliveries = Delivery.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking).order_by("id")
        
        pageLoad(request,20,100,"false")
        
        collectionInitial = []
        
        for collection in theCollections:
            collectionInitial.append({"trackingNo":collection.trackingNo})
        
        collectionFormSet = CollectionFormSet(prefix = "collection", queryset = theCollections, form_kwargs={'user': request.user})
        deliveryFormSet = DeliveryFormSet(prefix = "delivery", queryset = theDeliveries, form_kwargs={'user': request.user})
        
        # for collectionForm in collectionFormSet:
        #     print(collectionForm.as_table())
        
        for index, collection in enumerate(theCollections):
            percent = (40/len(theCollections)) * (index + 1)
            pageLoad(request,20+percent,100,"false")
            collections.append({"collection" : collection, "collectionForm" : CollectionForm(request.POST or None, request.FILES or None, user = request.user, prefix = "form-collection-" + str(collection.id), instance = collection)})
        for delivery in theDeliveries:
            deliveries.append({"delivery" : delivery, "deliveryForm" : DeliveryForm(request.POST or None, request.FILES or None, user = request.user, prefix = "form-delivery-" + str(delivery.id), instance = delivery)})
        
        documents = OrderTrackingDocument.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
        pageLoad(request,70,100,"false")
        collectionFormList = zip(theCollections, collectionFormSet)
        deliveryFormList = zip(theDeliveries, deliveryFormSet)
        
        deliveries = Delivery.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
        #deliveryForm = DeliveryForm(request.POST or None, request.FILES or None, instance = delivery, user = request.user)
        pageLoad(request,80,100,"false")
        parts = CollectionPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,collection__purchaseOrder__project = orderTracking.project).order_by("sequency")

        collectionPartIdList = []
        for part in parts:
            collectionPartIdList.append(part.id)
        
        orderTrackingForm = OrderTrackingForm(request.POST or None, request.FILES or None, instance = orderTracking)
        orderTrackingDocumentForm = OrderTrackingDocumentForm(request.POST or None, request.FILES or None)
        pageLoad(request,90,100,"false")
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderTrackingForm" : orderTrackingForm,
                "orderTrackingDocumentForm" : orderTrackingDocumentForm,
                "collectionFormSet" : collectionFormSet,
                "collectionFormList" : collectionFormList,
                "deliveryFormSet" : deliveryFormSet,
                "deliveryFormList" : deliveryFormList,
                #"deliveryForm" : deliveryForm,
                "deliveries" : deliveries,
                "collections" : collections,
                "documents"  :documents,
                "orderTrackings" : orderTrackings,
                "orderTracking" : orderTracking,
                "orderConfirmation" : orderConfirmation,
                "parts" : parts,
                "collectionPartIdList" : collectionPartIdList,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/order_tracking/order_tracking_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        orderTracking = get_object_or_404(OrderTracking, id = id)
        project = orderTracking.project
        theRequest = get_object_or_404(Request, project = project)
        invoiced = orderTracking.invoiced
        sessionKey = orderTracking.sessionKey
        user = orderTracking.user
        sourceCompany = orderTracking.sourceCompany
        
        deliveries = Delivery.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
        #deliveryForm = DeliveryForm(request.POST or None, request.FILES or None, instance = delivery, user = request.user)
        
        orderTrackingForm = OrderTrackingForm(request.POST, request.FILES or None, instance = orderTracking)
        orderTrackingDocumentForm = OrderTrackingDocumentForm(request.POST or None, request.FILES)
        
        collections = []
        
        theCollections = Collection.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
        theDeliveries = Delivery.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
        pageLoad(request,20,100,"false")
        collectionFormSet = CollectionFormSet(request.POST, prefix = "collection", queryset = theCollections, form_kwargs={'user': request.user})
        deliveryFormSet = DeliveryFormSet(request.POST, prefix = "delivery", queryset = theDeliveries, form_kwargs={'user': request.user})
        collectionPartsList = []
        for index, collection in enumerate(theCollections):
            percent = (60/len(theCollections))
            pageLoad(request,20+percent,100,"false")
            collections.append({"collection" : collection, "collectionForm" : CollectionForm(request.POST or None, request.FILES or None, user = request.user, prefix = "form-collection-" + str(collection.id), instance = collection)})
            collectionParts = CollectionPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,collection = collection)
            for collectionPart in collectionParts:
                collectionPartsList.append(collectionPart)
            
        if orderTrackingForm.is_valid() and orderTrackingDocumentForm.is_valid() and collectionFormSet.is_valid() and deliveryFormSet.is_valid():
            orderTracking = orderTrackingForm.save(commit = False)
            orderTracking.sourceCompany = sourceCompany
            orderTracking.project = project
            orderTracking.theRequest = theRequest
            orderTracking.invoiced = invoiced
            orderTracking.sessionKey = sessionKey
            orderTracking.user = user
            
            purchaseOrders = orderTracking.purchaseOrders.all()
            orderConfirmation = purchaseOrders[0].orderConfirmation
            
            if orderTracking.collected == True:
                if orderConfirmation.status != "invoiced" and orderConfirmation.status != "logistic" and orderConfirmation.status != "project_closed":
                    orderConfirmation.status = "collected"
            else:
                orderConfirmation.status = "collecting"
            orderConfirmation.save()
            
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
            
            orderTrackingDocument = orderTrackingDocumentForm.save(commit = False)
            if orderTrackingDocument.file:
                orderTrackingDocument.sourceCompany = request.user.profile.sourceCompany
                orderTrackingDocument.user = request.user
                orderTrackingDocument.sessionKey = request.session.session_key
                orderTrackingDocument.orderTracking = orderTracking
                orderTrackingDocument.save()
            
            collectionFormSet.save(commit = False)
            for collectionForm in collectionFormSet:
                instance = collectionForm.save(commit=False)
                instance.sourceCompany = sourceCompany
                instance.orderTracking = orderTracking
                instance.save()
            deliveryFormSet.save(commit = False)
            for deliveryForm in deliveryFormSet:
                instance = deliveryForm.save(commit=False)
                instance.sourceCompany = sourceCompany
                instance.orderTracking = orderTracking
                instance.save()
            pageLoad(request,90,100,"false")
            # delivery = deliveryForm.save(commit = False)
            # delivery.orderTracking = orderTracking
            # delivery.orderConfirmation = orderConfirmation
            # delivery.save()
            
            

            
            # for collection in collections:
            #     theOrderTracking = collection["collection"].orderTracking
            #     thePurchaseOrder = collection["collection"].purchaseOrder
            #     theCollectionForm = CollectionForm(request.POST or None, request.FILES or None, prefix = "form-collection-" + str(collection["collection"].id), instance = collection["collection"])
            #     print(collection["collection"].id)
            #     if theCollectionForm.is_valid():
            #         theCollection = theCollectionForm.save(commit = False)
            #         print(theCollectionForm.data)
            #         theCollection.orderTracking = theOrderTracking
            #         theCollection.purchaseOrder = thePurchaseOrder
            #         theCollection.save()
            
            
            commericalInvoicePdf(theRequest, orderConfirmation, request.user.profile.sourceCompany)
            pageLoad(request,100,100,"true")
            
            return HttpResponse(status=204)
            
        else:
            print(orderTrackingForm.errors)
            print(orderTrackingDocumentForm.errors)
            print(collectionFormSet.errors)
            print(deliveryFormSet.errors)
            return HttpResponse(status=404)

  
class OrderTrackingDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Order Tracking")
        idList = list.split(",")
        for id in idList:
            print(int(id))
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/order_tracking/order_tracking_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            orderTracking = get_object_or_404(OrderTracking, id = id)
            
            #process status sil
            processStatus = orderTracking.project.process_status_project.first()
            processStatus.delete()
            #process status sil-end
            
            orderTracking.delete()
            
            
            
        pageLoad(request,100,100,"true")
        return HttpResponse(status=204)


class OrderTrackingDocumentsView(LoginRequiredMixin, View):
    def get(self, request, file, *args, **kwargs):
        tag = _("Download Document")
        
        target_file = str(file) + ".pdf"  # Hedef dosyanın adı
        start_dir = os.path.join(os.getcwd(), "media", "sale")
        
        #hedef dosyayı başlangıç klasörü içerisinde alt klasörleri de tarayarak arar
        for root, dirs, files in os.walk(start_dir):
            if target_file in files:
                file_path = os.path.join(root, target_file)
                break
            else:
                file_path = None
            
        if file_path:
            response = FileResponse(open(file_path, 'rb'), as_attachment=True)
            return response
        else:
            return HttpResponse(status=204)


class OrderTrackingDocumentView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        elementTag = "orderTracking"
        elementTagSub = "orderTrackingPart"
        elementTagId = id
        
        orderTrackings = OrderTracking.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        orderTracking = OrderTracking.objects.filter(id = id).first()
        
        orderTrackingDocuments = OrderTrackingDocument.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
        
        theCollections = Collection.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
        
        collections = []
        
        for collection in theCollections:
            collections.append({"collection" : collection, "collectionForm" : CollectionForm(request.POST or None, request.FILES or None, user = request.user, prefix = "form-collection-" + str(collection.id), instance = collection)})
        
        commericalInvoices = CommericalInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
        sendInvoices = SendInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderConfirmation = orderTracking.purchaseOrders.all()[0].orderConfirmation)
        
        documents = OrderTrackingDocument.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking)
        
        orderTrackingDocumentForm = OrderTrackingDocumentForm(request.POST or None, request.FILES or None)
        context = {
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderTrackingDocumentForm" : orderTrackingDocumentForm,
                "orderTrackings" : orderTrackings,
                "orderTracking" : orderTracking,
                "orderTrackingDocuments" : orderTrackingDocuments,
                "collections" : collections,
                "commericalInvoices" : commericalInvoices,
                "sendInvoices" : sendInvoices,
                "documents" : documents,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/order_tracking/order_tracking_document.html', context)


class OrderTrackingDocumentAddView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        orderTracking = OrderTracking.objects.filter(id=id).first()
        pageLoad(request,20,100,"false")
        orderTrackingDocument = OrderTrackingDocument.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            sessionKey = request.session.session_key,
            orderTracking = orderTracking,
            file = request.FILES.get("file")
        )
        pageLoad(request,90,100,"false")
        orderTrackingDocument.save()
        pageLoad(request,100,100,"true")
        return HttpResponse(status=204)

class OrderTrackingDocumentDeleteView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        
        orderTrackingDocument = OrderTrackingDocument.objects.get(id = id)
        orderTrackingDocument.delete()
            
        return HttpResponse(status=204)

class OrderTrackingDocumentPdfView(LoginRequiredMixin, View):
    def get(self, request, id, name, *args, **kwargs):
        tag = _("Inquiry PDF")
        
        elementTag = "orderTracking"
        elementTagSub = "orderTrackingPart"
        elementTagId = str(id) + "-pdf"
        
        pageLoad(request,0,100,"false")
        
        orderTrackingDocument = OrderTrackingDocument.objects.get(id = id, name = name)
        orderTracking = orderTrackingDocument.orderTracking
        pageLoad(request,50,100,"false")
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderTrackingDocument" : orderTrackingDocument,
                "orderTracking" : orderTracking,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/order_tracking/order_tracking_document_pdf.html', context)

class OrderTrackingPdfView(LoginRequiredMixin, View):
    def get(self, request, id, type, *args, **kwargs):
        tag = _("Documents")
        
        elementTag = "orderTracking"
        elementTagSub = "orderTrackingCollection"
        elementTagId = str(id) + "-pdf"
        
        pageLoad(request,0,100,"false")
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        if type == "r":
            requestt = Request.objects.get(project = id)
            pageLoad(request,50,100,"false")
            requestPdf(requestt)
            pageLoad(request,100,100,"true")

            return render(request,'sale/request/request_pdf.html',context={"tag":tag,"elementTag":elementTag,"elementTagSub":elementTagSub,"elementTagId":elementTagId,"requestt":requestt})
        
        elif type == "i":
            inquiry = Inquiry.objects.get(id = id)
            pageLoad(request,50,100,"false")
            #inquiryPdf(inquiry)
            pageLoad(request,100,100,"true")
            
            return render(request, 'sale/inquiry/inquiry_pdf.html',context={"tag":tag,"elementTag":elementTag,"elementTagSub":elementTagSub,"elementTagId":elementTagId,"inquiry":inquiry,"version":version})
        
        elif type == "q":
            quotation = Quotation.objects.get(id = id)
            pageLoad(request,50,100,"false")
            #quotationPdf(quotation)
            pageLoad(request,100,100,"true")
            
            return render(request, 'sale/quotation/quotation_pdf.html', context={"tag":tag,"elementTag":elementTag,"elementTagSub":elementTagSub,"elementTagId":elementTagId,"quotation":quotation,"version":version})
        
        elif type == "oc":
            orderConfirmation = OrderConfirmation.objects.get(id = id)
            pageLoad(request,50,100,"false")
            orderConfirmationPdf(orderConfirmation)
            pageLoad(request,100,100,"true")
            
            return render(request, 'sale/order_confirmation/order_confirmation_pdf.html',context={"tag":tag,"elementTag":elementTag,"elementTagSub":elementTagSub,"elementTagId":elementTagId,"orderConfirmation":orderConfirmation})
        
        elif type == "po":
            purchaseOrder = PurchaseOrder.objects.get(id = id)
            pageLoad(request,50,100,"false")
            purchaseOrderPdfInTask.delay(purchaseOrder.id)
            pageLoad(request,100,100,"true")
            
            return render(request, 'sale/purchase_order/purchase_order_pdf.html',context={"tag":tag,"elementTag":elementTag,"elementTagSub":elementTagSub,"elementTagId":elementTagId,"purchaseOrder":purchaseOrder})

class CommericalInvoicePdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Commerical Invoice PDF")
        
        elementTag = "orderTracking"
        elementTagSub = "orderTrackingPart"
        elementTagId = str(id) + "-pdf"
        
        orderConfirmation = OrderConfirmation.objects.filter(id=id).first()
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #orderConfirmationPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderConfirmation" : orderConfirmation,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/order_tracking/commerical_invoice_pdf.html', context)
   
  
class DeliveryInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Delivery ")
        elementTag = "orderTracking"
        elementTagSub = "orderTrackingCollection"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        orderTrackingId = refererPath.replace("/sale/order_tracking/order_tracking_update/","").replace("/","")
        orderTracking = get_object_or_404(OrderTracking, id = id)
        
        deliveryAddForm = DeliveryForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderTracking" : orderTracking,
                "deliveryAddForm" : deliveryAddForm
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/order_tracking/delivery_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        orderTrackingId = refererPath.replace("/sale/order_tracking_update/","").replace("/","")
        
        orderTracking = OrderTracking.objects.get(id = id)
        delivery = Delivery.objects.filter(orderTracking = orderTracking)
        orderConfirmation = orderTracking.purchaseOrders.all()[0].orderConfirmation
        
        deliveryAddForm = DeliveryForm(request.POST, request.FILES or None, user = request.user)
        if deliveryAddForm.is_valid():
            delivery = deliveryAddForm.save(commit = False)
            delivery.sourceCompany = request.user.profile.sourceCompany
            delivery.orderTracking = orderTracking
            delivery.orderConfirmation = orderConfirmation
            delivery.save()
            return HttpResponse(status=204)
        else:
            print(deliveryAddForm.errors)
            return HttpResponse(status=404)
     