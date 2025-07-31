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
from ..pdfs.purchase_order_pdfs import *
from ..pdfs.quotation_pdfs import *

from source.models import Company as SourceCompany
from account.models import ProformaInvoice, CommericalInvoice, SendInvoice

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
        elementTag = "purchaseOrder"
        elementTagSub = "purchaseOrderPart"
        
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

        return render(request, 'sale/purchase_order/purchase_orders.html', context)

class PurchaseOrderAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Purchase Order")
        orderConfirmation = OrderConfirmation.objects.get(id = id)
        
        elementTag = "purchaseOrderAdd"
        elementTagSub = "purchaseOrderPartInAdd"
        elementTagId = id
        
        quotationParts = QuotationPart.objects.select_related("inquiryPart__inquiry").filter(
            sourceCompany = request.user.profile.sourceCompany,
            quotation = orderConfirmation.quotation
        )
        
        inquiryIdList = []
        inquiryParts = []
        
        for quotationPart in quotationParts:
            if quotationPart.inquiryPart.inquiry.purchase_order_inquiry.select_related().all().first():
                purchaseOrder = quotationPart.inquiryPart.inquiry.purchase_order_inquiry.select_related().all().first().purchaseOrderNo
            else:
                purchaseOrder = ""
            inquiryIdList.append(quotationPart.inquiryPart.inquiry.id)
            inquiryParts.append({"id" : quotationPart.inquiryPart.inquiry.id,
                                "supplier" : quotationPart.inquiryPart.inquiry.supplier.name,
                                 "totalPrice" : quotationPart.totalPrice1,
                                 "totalPrice" : quotationPart.totalPrice1,
                                 "currency" : quotationPart.quotation.currency.code,
                                 "purchaseOrder" : purchaseOrder
                                 })

        temp_dict = {}
        for item in inquiryParts:
            id = item['id']
            supplier = item['supplier']
            total_price = item['totalPrice']
            currency = item['currency']
            purchaseOrder = item['purchaseOrder']
            
            if supplier in temp_dict:
                temp_dict[supplier]['totalPrice'] += total_price
                if temp_dict[supplier]['currency'] != currency:
                    raise ValueError(f"Supplier {supplier} has multiple currencies.")
            else:
                temp_dict[supplier] = {'totalPrice': total_price, 'currency': currency, 'purchaseOrder': purchaseOrder, 'id' : id}
        
        inquiries = [{'supplier': supplier, 'totalPrice': values['totalPrice'], 'currency': values['currency'], 'purchaseOrder': values['purchaseOrder'], 'id': values['id']} for supplier, values in temp_dict.items()]
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderConfirmation" : orderConfirmation,
                "inquiryIdList" : inquiryIdList,
                "inquiries" : inquiries,
                "sessionKey" : request.session.session_key
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/purchase_order/purchase_order_add.html', context)
    
    def post(self, request, id, listt, *args, **kwargs):
        form = PurchaseOrderForm(request.POST, request.FILES or None)
        print(request.POST.getlist("purchaseOrderSupplier"))
        orderConfirmation = get_object_or_404(OrderConfirmation, id = id)
        
        idList = json.loads(listt)
        
        newIdList = []
        for i in idList:
            newIdList.append(i)
            
        #idList = list(set(newIdList))
        
        idList = request.POST.getlist("purchaseOrderSupplier")
        
        for i in idList:
            identificationCode = request.user.profile.sourceCompany.salePurchaseOrderCode
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastPurchaseOrder = PurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            if lastPurchaseOrder:
                lastCode = lastPurchaseOrder.code
            else:
                lastCode = startCodeValue - 1
                
            code = int(lastCode) + 1
            
            purchaseOrderNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        
            inquiry = get_object_or_404(Inquiry, id = i)
            
            purchaseOrder = PurchaseOrder.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                code = code,
                yearCode = yearCode,
                purchaseOrderNo = purchaseOrderNo,
                project = get_object_or_404(Project, id = inquiry.project.id),
                inquiry = inquiry,
                orderConfirmation = orderConfirmation,
                currency = inquiry.currency,
                sessionKey = request.session.session_key,
                user = request.user
            )
            
            purchaseOrder.save()
            
            project = purchaseOrder.project
            project.stage = "purchase_order"
            project.save()
            
            parts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = orderConfirmation.quotation, inquiryPart__inquiry = inquiry)
            
            for part in parts:
                purchaseOrderPart = PurchaseOrderPart.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    sessionKey = request.session.session_key,
                    purchaseOrder = purchaseOrder,
                    maker = part.inquiryPart.maker,
                    makerType = part.inquiryPart.makerType,
                    inquiryPart = part.inquiryPart,
                    partNo = part.inquiryPart.requestPart.part.partNo,
                    description = part.inquiryPart.requestPart.part.description,
                    quantity = part.quantity,
                    unitPrice = part.inquiryPart.unitPrice,
                    totalPrice = part.inquiryPart.totalPrice,
                    availability = part.inquiryPart.availability,
                    availabilityType = part.inquiryPart.availabilityType,
                    sequency = part.inquiryPart.sequency
                )
                
                purchaseOrderPart.save()
            
            purchaseOrderParts = PurchaseOrderPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder).order_by("inquiryPart__sequency")
            sequencyCount = 0
            for purchaseOrderPart in purchaseOrderParts:
                purchaseOrderPart.sequency = sequencyCount + 1
                purchaseOrderPart.save()
                sequencyCount = sequencyCount + 1
        
        purchaseOrderPdfInTask.delay(purchaseOrder.id,request.user.profile.sourceCompany.id)
        
        return HttpResponse(status=204)
    
class PurchaseOrderUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Purchase Order Detail")
        elementTag = "purchaseOrder"
        elementTagSub = "purchaseOrderPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        purchaseOrders = PurchaseOrder.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        purchaseOrder = get_object_or_404(PurchaseOrder, id = id)
        #quotationParts = QuotationPart.objects.filter(quotation = orderConfirmation.quotation)
        
        collection = Collection.objects.select_related().filter(purchaseOrder = purchaseOrder).first()
        
        parts = PurchaseOrderPart.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)
        pageLoad(request,20,100,"false")
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
        partsTotal = 0
        
        for index, part in enumerate(parts):
            percent = (60/len(parts)) * (index + 1)
            pageLoad(request,20+percent,100,"false")
            partsTotal  = partsTotal + part.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
        
        if purchaseOrder.discountAmount > 0:
            partsTotals["totalDiscount"] = purchaseOrder.discountAmount
        else:
            partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (purchaseOrder.discount/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
        
        # Para miktarını belirtilen formatta gösterme
        totalBuyingPriceFixed = "{:,.2f}".format(round(partsTotals["totalTotalPrice3"],2))
        totalDiscountPriceFixed = "{:,.2f}".format(round(partsTotals["totalDiscount"],2))
        totalTotalPriceFixed = "{:,.2f}".format(round(partsTotals["totalFinal"],2))
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
                "partsTotals" : partsTotals,
                "totalBuyingPriceFixed" : totalBuyingPriceFixed,
                "totalDiscountPriceFixed" : totalDiscountPriceFixed,
                "totalTotalPriceFixed" : totalTotalPriceFixed,
                "collection" : collection,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/purchase_order/purchase_order_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        purchaseOrder = get_object_or_404(PurchaseOrder, id = id)
        project = purchaseOrder.project
        theRequest = Request.objects.get(project = project)
        inquiry = purchaseOrder.inquiry
        orderConfirmation = purchaseOrder.orderConfirmation
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
            purchaseOrder.orderConfirmation = orderConfirmation
            purchaseOrder.identificationCode = identificationCode
            purchaseOrder.code = code
            purchaseOrder.yearCode = yearCode
            purchaseOrder.purchaseOrderNo = purchaseOrderNo
            purchaseOrder.sessionKey = sessionKey
            purchaseOrder.user = user
            
            parts = PurchaseOrderPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)
            partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
            partsTotal = 0
            
            for index, part in enumerate(parts):
                percent = (60/len(parts)) * (index + 1)
                pageLoad(request,20+percent,100,"false")
                partsTotal  = partsTotal + part.totalPrice
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
            
            if purchaseOrder.discountAmount > 0:
                partsTotals["totalDiscount"] = purchaseOrder.discountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (purchaseOrder.discount/100)
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
            
            purchaseOrder.totalDiscountPrice = round(partsTotals["totalDiscount"],2)
            purchaseOrder.totalTotalPrice = round(partsTotals["totalFinal"],2)
            purchaseOrder.save()
            
            # Para miktarını belirtilen formatta gösterme
            totalBuyingPriceFixed = "{:,.2f}".format(round(partsTotals["totalTotalPrice3"],2))
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
            
            updateDetail(totalPrices,"purchase_order_update")
        
            pageLoad(request,90,100,"false")
            #purchaseOrderPdf(theRequest, purchaseOrder)
            purchaseOrderPdfInTask.delay(purchaseOrder.id,request.user.profile.sourceCompany.id)
            #purchaseOrderPdf(purchaseOrder.id)
            pageLoad(request,100,100,"true")
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)

   
class PurchaseOrderDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Purchase Order")
        
        idList = list.split(",")
        
        elementTag = "purchaseOrder"
        elementTagSub = "purchaseOrderPart"
        elementTagId = idList[0]
        
        if len(idList) == 1:
            purchaseOrder = PurchaseOrder.objects.filter(id = int(idList[0])).first()
            collections = Collection.objects.filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)
        
        for id in idList:
            print(int(id))
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        if len(collections) > 0:
            alertMessage = f"{purchaseOrder.purchaseOrderNo} cannot be deleted because it has collection in order tracking"
            context = {
                "tag": tag,
                "alertMessage" : alertMessage
            }
            return render(request, 'sale/purchase_order/purchase_order_alert.html', context)
        else:
            context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId
            }  
            return render(request, 'sale/purchase_order/purchase_order_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList): 
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            purchaseOrder = get_object_or_404(PurchaseOrder, id = id)
            
            purchaseOrder.delete()
            
            orderConfirmation = purchaseOrder.orderConfirmation
            otherPurchaseOrders = orderConfirmation.purchase_order_order_confirmation.all()
            if not otherPurchaseOrders:
                project = orderConfirmation.project
                project.stage = "order_confirmation"
                project.save()
            
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)

class PurchaseOrderPdfView(LoginRequiredMixin, View):
    def get(self, request, id, source, *args, **kwargs):
        tag = _("Purchase Order PDF")
        
        if source == "po":
            elementTag = "purchaseOrder"
            elementTagSub = "purchaseOrderPart"
            elementTagId = str(id) + "-pdf"
        elif source == "ot":
            elementTag = "orderTracking"
            elementTagSub = "orderTrackingPart"
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
        
        return render(request, 'sale/purchase_order/purchase_order_pdf.html', context)


class PurchaseOrderAllExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Purchase Order Excel")
        
        elementTag = "purchaseOrderExcel"
        elementTagSub = "purchaseOrderPartExcel"
        
        companies = []
        purchaseOrders = PurchaseOrder.objects.select_related("inquiry__supplier").filter(sourceCompany = request.user.profile.sourceCompany)
        for purchaseOrder in purchaseOrders:
            companies.append(purchaseOrder.inquiry.supplier)

        companies = set(companies)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "sessionKey" : request.session.session_key,
                "companies" : companies
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/purchase_order/purchase_order_excel.html', context)       

class PurchaseOrderExportExcelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "sale", "purchase_order", "documents")

        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
        projectExcludeStages = []
        
        if request.GET.get("start") == "":
            startDate = "01/01/2024"
        else:
            startDate = datetime.strptime(request.GET.get("start"), "%d/%m/%Y").date()
            
        if request.GET.get("end") == "":
            endDate = datetime.today().date().strftime('%d/%m/%Y')
        else:
            endDate = datetime.strptime(request.GET.get("end"), "%d/%m/%Y").date()
            
        if request.GET.get("po") == "false":
            projectExcludeStages.append("request")
            projectExcludeStages.append("inquiry")
            projectExcludeStages.append("quotation")
            projectExcludeStages.append("order_confirmation")
            projectExcludeStages.append("order_not_confirmation")
            projectExcludeStages.append("purchase_order")
        
        if request.GET.get("ot") == "false":
            projectExcludeStages.append("order_tracking")
            
        if request.GET.get("i") == "false":
            projectExcludeStages.append("invoiced")
        
        companies = request.GET.get("s")
        customers = request.GET.get("c")
        vessels = request.GET.get("v")
        
        purchaseOrders = PurchaseOrder.objects.select_related(
            "project","orderConfirmation__quotation__inquiry","orderConfirmation__quotation__inquiry__theRequest"
        ).exclude(
            project__stage__in=projectExcludeStages
        ).filter(
            sourceCompany = request.user.profile.sourceCompany,
            created_date__date__range=(startDate,endDate)
        ).order_by("-id")
        
        if companies:
            companies = companies.split(",")
            purchaseOrders = purchaseOrders.filter(inquiry__supplier__id__in=companies).order_by("-id")
           
        if customers:
            customers = customers.split(",")
            purchaseOrders = purchaseOrders.filter(inquiry__theRequest__customer__id__in=customers).order_by("-id")
         
        if vessels:
            vessels = vessels.split(",")
            purchaseOrders = purchaseOrders.filter(inquiry__theRequest__vessel__id__in=vessels).order_by("-id")
        
        
        
        data = {
            "Line": [],
            "Project No": [],
            "SPO": [],
            "PO Date": [],
            "Reference": [],
            "Supplier": [],
            "Customer": [],
            "Vessel": [],
            "Maker": [],
            "Type": [],
            "B. Total": [],
            "Currency": [],
            "Project Creator": [],
            "Project Status": []
        }
        
        channel_layer = get_channel_layer()
        
        seq = 0
        for purchaseOrder in purchaseOrders:
            # async_to_sync(channel_layer.group_send)(
            #     'order_onfirmation_room',
            #     {
            #         "type": "create_excel",
            #         "message": seq
            #     }
            # )
        
            async_to_sync(channel_layer.group_send)(
                'private_' + str(request.user.id),
                {
                    "type": "send_percent",
                    "message": seq,
                    "location" : "purchase_order_excel",
                    "totalCount" : len(purchaseOrders),
                    "ready" : "false"
                }
            )
            
            if purchaseOrder.orderConfirmation.quotation.inquiry.theRequest.vessel:
                vessel = purchaseOrder.orderConfirmation.quotation.inquiry.theRequest.vessel.name
            else:
                vessel = ""
            
            if purchaseOrder.orderConfirmation.quotation.inquiry.theRequest.maker:
                maker = purchaseOrder.orderConfirmation.quotation.inquiry.theRequest.maker.name
            else:
                maker = ""
            
            if purchaseOrder.orderConfirmation.quotation.inquiry.theRequest.makerType:
                makerType = purchaseOrder.orderConfirmation.quotation.inquiry.theRequest.makerType.type
            else:
                makerType = ""
            
            buyingTotalPrice = 0
            
            parts = PurchaseOrderPart.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)
    
            partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
            
            partsTotal = 0
            
            for part in parts:
                partsTotal  = partsTotal + part.totalPrice
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
            
            if purchaseOrder.discountAmount > 0:
                partsTotals["totalDiscount"] = purchaseOrder.discountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (purchaseOrder.discount/100)
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
            
            buyingTotalPrice = buyingTotalPrice + round(partsTotals["totalFinal"],2)
            
            data["Line"].append(seq)
            data["Project No"].append(purchaseOrder.project.projectNo)
            data["SPO"].append(purchaseOrder.purchaseOrderNo)
            data["PO Date"].append(purchaseOrder.purchaseOrderDate)
            data["Reference"].append(purchaseOrder.inquiry.supplierRef)
            data["Supplier"].append(purchaseOrder.inquiry.supplier.name)
            data["Customer"].append(purchaseOrder.orderConfirmation.quotation.inquiry.theRequest.customer.name)
            data["Vessel"].append(vessel)
            data["Maker"].append(maker)
            data["Type"].append(makerType)
            data["B. Total"].append(buyingTotalPrice)
            data["Currency"].append(purchaseOrder.currency.code)
            data["Project Creator"].append(str(purchaseOrder.project.user.first_name)+" "+str(purchaseOrder.project.user.last_name))
            data["Project Status"].append(purchaseOrder.project.stage)
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/all-purchase-orders.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Purchase Order', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        if purchaseOrders:
            purchaseOrdersCount = len(purchaseOrders)
        else:
            purchaseOrdersCount = 0
        async_to_sync(channel_layer.group_send)(
            'private_' + str(request.user.id),
            {
                "type": "send_percent",
                "message": seq,
                "location" : "purchase_order_excel",
                "totalCount" : purchaseOrdersCount,
                "ready" : "true"
            }
        )
        
        return HttpResponse(status=204)

class PurchaseOrderDownloadExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/sale/purchase_order/documents/all-purchase-orders.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'
        
        return response
       

  
class PurchaseOrderPartUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Purchase Order Part Detail")
        
        elementTag = "purchaseOrder"
        elementTagSub = "purchaseOrderPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        purchaseOrderPart = get_object_or_404(PurchaseOrderPart, id = id)
        print(purchaseOrderPart.sessionKey)
        form = PurchaseOrderPartForm(request.POST or None, request.FILES or None, instance = purchaseOrderPart)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "refererPath" : refererPath,
                "form" : form,
                "purchaseOrderPart" : purchaseOrderPart
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/purchase_order/purchase_order_part_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        purchaseOrderPart = get_object_or_404(PurchaseOrderPart, id = id)
        purchaseOrder = purchaseOrderPart.purchaseOrder
        sessionKey = purchaseOrderPart.sessionKey
        user = purchaseOrderPart.user
        inquiryPart = purchaseOrderPart.inquiryPart
        unitPrice = purchaseOrderPart.unitPrice
        totalPrice = purchaseOrderPart.totalPrice
        availabilityType = purchaseOrderPart.availabilityType
        availability = purchaseOrderPart.availability
        sourceCompany = purchaseOrderPart.sourceCompany
        form = PurchaseOrderPartForm(request.POST, request.FILES or None, instance = purchaseOrderPart)
        if form.is_valid():
            purchaseOrderPart = form.save(commit = False)
            purchaseOrderPart.sourceCompany = sourceCompany
            purchaseOrderPart.purchaseOrder = purchaseOrder
            purchaseOrderPart.sessionKey = sessionKey
            purchaseOrderPart.user = user
            purchaseOrderPart.inquiryPart = inquiryPart
            purchaseOrderPart.unitPrice = unitPrice
            purchaseOrderPart.totalPrice = totalPrice
            purchaseOrderPart.availability = availability
            purchaseOrderPart.availabilityType = availabilityType
            purchaseOrderPart.save()
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
        return render(request, 'sale/purchase_order/purchase_order_part_detail.html', context)
    