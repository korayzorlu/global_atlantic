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
from ..pdfs.order_confirmation_pdfs import *
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

class OrderConfirmationDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Order Confirmations")
        elementTag = "orderConfirmation"
        elementTagSub = "quotationPartOC"
        
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
        
        return render(request, 'sale/order_confirmation/order_confirmations.html', context)

class OrderConfirmationAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Order Confirmation")
        
        quotation = Quotation.objects.select_related().get(id = id)
        quotationParts = quotation.quotationpart_set.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        
        nonProfitParts = []
        
        for quotationPart in quotationParts:
            if quotationPart.profit == 0:
                nonProfitParts.append(quotationParts)
        
        elementTag = "orderConfirmationAdd"
        elementTagSub = "orderConfirmationPartInAdd"
        elementTagId = id
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "quotation" : quotation,
                "nonProfitParts" : nonProfitParts
        }
        return render(request, 'sale/order_confirmation/order_confirmation_add.html', context)
    def post(self, request, id, *args, **kwargs):
        quotation = Quotation.objects.get(id = id)
        quotation.approval = "notified"
        quotation.save()
        
        identificationCode = request.user.profile.sourceCompany.saleOrderConfirmationCode
        yearCode = int(str(datetime.today().date().year)[-2:])
        startCodeValue = 1
        
        lastOrderConfirmation = OrderConfirmation.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
        
        if lastOrderConfirmation:
            lastCode = lastOrderConfirmation.code
        else:
            lastCode = startCodeValue - 1
        
        code = int(lastCode) + 1
        
        orderConfirmationNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        
        orderConfirmation = OrderConfirmation.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            project = quotation.project,
            quotation = quotation,
            identificationCode = identificationCode,
            yearCode = yearCode,
            code = code,
            orderConfirmationNo = orderConfirmationNo,
            sessionKey = request.session.session_key,
            user = request.user
        )
        
        orderConfirmation.save()
        
        project = orderConfirmation.project
        project.stage = "order_confirmation"
        project.save()
        
        quotation.soc = orderConfirmationNo
        quotation.save()
        
        project = orderConfirmation.project
        theRequest = Request.objects.get(project = project)
        
        orderConfirmationPdf(theRequest, orderConfirmation, request.user.profile.sourceCompany)
        
        return HttpResponse(status=204)
        
class OrderConfirmationUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Order Confirmation Detail")
        elementTag = "orderConfirmation"
        elementTagSub = "quotationPartOC"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        
        orderConfirmations = OrderConfirmation.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        orderConfirmation = get_object_or_404(OrderConfirmation, id = id)
        purchaseOrders = PurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderConfirmation = orderConfirmation)
        proformaInvoices = ProformaInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderConfirmation = orderConfirmation)
        
        quotationParts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = orderConfirmation.quotation)
        pageLoad(request,20,100,"false")
        inquiryIdList = []

        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
        partsTotal = 0
        
        for index, part in enumerate(quotationParts):
            percent = (60/len(quotationParts)) * (index + 1)
            pageLoad(request,20+percent,100,"false")
            partsTotal  = partsTotal + part.totalPrice3
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice1
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice2
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice3
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice1
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice2
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice3
        
        if orderConfirmation.quotation.manuelDiscountAmount > 0:
            partsTotals["totalDiscount"] = orderConfirmation.quotation.manuelDiscountAmount
        else:
            partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (orderConfirmation.quotation.manuelDiscount/100)
        partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (orderConfirmation.vat/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
        
        if partsTotals["totalFinal"] == 0 or partsTotals["totalFinal"] < 0 and partsTotals["totalTotalPrice1"] == 0:
            totalProfitPrice = 0
        else:
            totalProfitPrice = round((((partsTotals["totalFinal"] - partsTotals["totalVat"]) / partsTotals["totalTotalPrice1"]) - 1) * 100,2)
        
        # Para miktarını belirtilen formatta gösterme
        totalBuyingPriceFixed = "{:,.2f}".format(round(partsTotals["totalTotalPrice1"],2))
        totalGrossPriceFixed = "{:,.2f}".format(round(partsTotals["totalTotalPrice3"],2))
        totalDiscountPriceFixed = "{:,.2f}".format(round(partsTotals["totalDiscount"],2))
        totalVatPriceFixed = "{:,.2f}".format(round(partsTotals["totalVat"],2))
        totalSellingPriceFixed = "{:,.2f}".format(round(partsTotals["totalFinal"],2))
        totalProfitAmountPriceFixed = "{:,.2f}".format(round(partsTotals["totalFinal"] - partsTotals["totalVat"] - partsTotals["totalTotalPrice1"],2))
        # Nokta ile virgülü değiştirme
        totalBuyingPriceFixed = totalBuyingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalGrossPriceFixed = totalGrossPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalDiscountPriceFixed = totalDiscountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalVatPriceFixed = totalVatPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalSellingPriceFixed = totalSellingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalProfitAmountPriceFixed = totalProfitAmountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        for quotationPart in quotationParts:
            inquiryIdList.append(quotationPart.inquiryPart.inquiry.id)
        
        form = OrderConfirmationForm(request.POST or None, request.FILES or None, instance = orderConfirmation)
        pageLoad(request,90,100,"false")
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "orderConfirmations" : orderConfirmations,
                "orderConfirmation" : orderConfirmation,
                "purchaseOrders" : purchaseOrders,
                "proformaInvoices" : proformaInvoices,
                "quotationParts" : quotationParts,
                "partsTotals" : partsTotals,
                "totalBuyingPriceFixed" : totalBuyingPriceFixed,
                "totalGrossPriceFixed" : totalGrossPriceFixed,
                "totalDiscountPriceFixed" : totalDiscountPriceFixed,
                "totalVatPriceFixed" : totalVatPriceFixed,
                "totalSellingPriceFixed" : totalSellingPriceFixed,
                "totalProfitAmountPriceFixed" : totalProfitAmountPriceFixed,
                "totalProfitPrice" : totalProfitPrice,
                "inquiryIdList" : inquiryIdList,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/order_confirmation/order_confirmation_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        orderConfirmation = get_object_or_404(OrderConfirmation, id = id)
        project = orderConfirmation.project
        theRequest = Request.objects.get(project = project)
        quotation = orderConfirmation.quotation
        identificationCode = orderConfirmation.identificationCode
        code = orderConfirmation.code
        yearCode = orderConfirmation.yearCode
        orderConfirmationNo = orderConfirmation.orderConfirmationNo
        sessionKey = orderConfirmation.sessionKey
        user = orderConfirmation.user
        sourceCompany = orderConfirmation.sourceCompany
        pageLoad(request,20,100,"false")
        form = OrderConfirmationForm(request.POST, request.FILES or None, instance = orderConfirmation)

        if form.is_valid():
            orderConfirmation = form.save(commit = False)
            orderConfirmation.sourceCompany = sourceCompany
            orderConfirmation.project = project
            orderConfirmation.quotation = quotation
            orderConfirmation.identificationCode = identificationCode
            orderConfirmation.code = code
            orderConfirmation.yearCode = yearCode
            orderConfirmation.orderConfirmationNo = orderConfirmationNo
            orderConfirmation.sessionKey = sessionKey
            orderConfirmation.user = user
            orderConfirmation.save()
            
            vatAmount = quotation.totalSellingPrice * (orderConfirmation.vat/100)
            
            if quotation.totalSellingPrice == 0 or quotation.totalSellingPrice < 0 and quotation.totalBuyingPrice == 0:
                totalProfitPrice = 0
            else:
                totalProfitPrice = round(((quotation.totalSellingPrice / quotation.totalBuyingPrice) - 1) * 100,2)
            
            # Para miktarını belirtilen formatta gösterme
            totalBuyingPriceFixed = "{:,.2f}".format(quotation.totalBuyingPrice)
            totalGrossPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice + quotation.totalDiscountPrice)
            totalDiscountPriceFixed = "{:,.2f}".format(quotation.totalDiscountPrice)
            totalVatPriceFixed = "{:,.2f}".format(vatAmount)
            totalSellingPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice + vatAmount)
            totalProfitAmountPriceFixed = "{:,.2f}".format(round(quotation.totalSellingPrice - quotation.totalBuyingPrice,2))
            # Nokta ile virgülü değiştirme
            totalBuyingPriceFixed = totalBuyingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalGrossPriceFixed = totalGrossPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalDiscountPriceFixed = totalDiscountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalVatPriceFixed = totalVatPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalSellingPriceFixed = totalSellingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalProfitAmountPriceFixed = totalProfitAmountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            totalPrices = {"orderConfirmation":orderConfirmation.id,
                                "totalBuyingPrice":totalBuyingPriceFixed,
                                "totalGrossPrice":totalGrossPriceFixed,
                                "totalDiscountPrice":totalDiscountPriceFixed,
                                "totalVatPrice":totalVatPriceFixed,
                                "totalSellingPrice":totalSellingPriceFixed,
                                "totalProfitAmountPrice":totalProfitAmountPriceFixed,
                                "totalProfitPrice":totalProfitPrice,
                                "currency":quotation.currency.symbol}
                
            updateDetail(totalPrices,"order_confirmation_update")
            
            pageLoad(request,80,100,"false")
            orderConfirmationPdf(theRequest, orderConfirmation, request.user.profile.sourceCompany)
            pageLoad(request,100,100,"true")
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)
        
class OrderConfirmationPdfView(LoginRequiredMixin, View):
    def get(self, request, id, source, *args, **kwargs):
        tag = _("Order Confirmation PDF")
        
        if source == "oc":
            elementTag = "orderConfirmation"
            elementTagSub = "orderConfirmationPart"
            elementTagId = str(id) + "-pdf"
        elif source == "ot":
            elementTag = "orderTracking"
            elementTagSub = "orderTrackingPart"
            elementTagId = str(id) + "-pdf"
        
        pageLoad(request,0,100,"false")
        
        orderConfirmation = get_object_or_404(OrderConfirmation, id = id)
        pageLoad(request,50,100,"false")
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
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/order_confirmation/order_confirmation_pdf.html', context)

class OrderConfirmationAllExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Download Order Confirmation Excel")
        
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "sale", "order_confirmation", "documents")

        orderConfirmations = OrderConfirmation.objects.select_related("project","quotation__inquiry__theRequest").filter(
            sourceCompany = request.user.profile.sourceCompany
        ).order_by("-id")
        
        data = {
            "Line": [],
            "Project No": [],
            "SOC": [],
            "Confirm": [],
            "Reference": [],
            "Customer": [],
            "Vessel": [],
            "Maker": [],
            "Type": [],
            "B. Total": [],
            "S. Total": [],
            "Currency": [],
            "Project Creator": [],
            "Project Status": []
        }
        
        channel_layer = get_channel_layer()
        
        seq = 1
        for orderConfirmation in orderConfirmations:
            # async_to_sync(channel_layer.group_send)(
            #     'order_onfirmation_room',
            #     {
            #         "type": "create_excel",
            #         "message": seq
            #     }
            # )
            
            if orderConfirmation.quotation.inquiry.theRequest.vessel:
                vessel = orderConfirmation.quotation.inquiry.theRequest.vessel.name
            else:
                vessel = ""
            
            if orderConfirmation.quotation.inquiry.theRequest.maker:
                maker = orderConfirmation.quotation.inquiry.theRequest.maker.name
            else:
                maker = ""
            
            if orderConfirmation.quotation.inquiry.theRequest.makerType:
                makerType = orderConfirmation.quotation.inquiry.theRequest.makerType.type
            else:
                makerType = ""
                
            purchaseOrders = orderConfirmation.purchase_order_order_confirmation.order_by("-id").filter(sourceCompany = request.user.profile.sourceCompany)
            
            buyingTotalPrice = 0
            for purchaseOrder in purchaseOrders:
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
            data["Project No"].append(orderConfirmation.project.projectNo)
            data["SOC"].append(orderConfirmation.orderConfirmationNo)
            data["Confirm"].append(orderConfirmation.orderConfirmationDate)
            data["Reference"].append(orderConfirmation.quotation.inquiry.theRequest.customerRef)
            data["Customer"].append(orderConfirmation.quotation.inquiry.theRequest.customer.name)
            data["Vessel"].append(vessel)
            data["Maker"].append(maker)
            data["Type"].append(makerType)
            data["B. Total"].append(buyingTotalPrice)
            data["S. Total"].append(orderConfirmation.quotation.totalSellingPrice)
            data["Currency"].append(orderConfirmation.quotation.currency.code)
            data["Project Creator"].append(str(orderConfirmation.project.user.first_name)+" "+str(orderConfirmation.project.user.last_name))
            data["Project Status"].append(orderConfirmation.project.stage)
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/all-order-confirmations.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Order Confirmation', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/sale/order_confirmation/documents/all-order-confirmations.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'
        
        return response

class OrderConfirmationDailyExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Download Order Confirmation Excel")
        
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "sale", "order_confirmation", "documents")

        orderConfirmations = OrderConfirmation.objects.select_related("project","quotation__inquiry__theRequest").filter(
            sourceCompany = request.user.profile.sourceCompany,
            orderConfirmationDate = datetime.today().date()
        ).order_by("-id")
        
        data = {
            "Line": [],
            "Project No": [],
            "SOC": [],
            "Confirm": [],
            "Reference": [],
            "Customer": [],
            "Vessel": [],
            "Maker": [],
            "Type": [],
            "B. Total": [],
            "S. Total": [],
            "Currency": [],
            "Project Creator": [],
            "Project Status": []
        }
        
        channel_layer = get_channel_layer()
        
        seq = 1
        for orderConfirmation in orderConfirmations:
            # async_to_sync(channel_layer.group_send)(
            #     'order_onfirmation_room',
            #     {
            #         "type": "create_excel",
            #         "message": seq
            #     }
            # )
            
            if orderConfirmation.quotation.inquiry.theRequest.vessel:
                vessel = orderConfirmation.quotation.inquiry.theRequest.vessel.name
            else:
                vessel = ""
            
            if orderConfirmation.quotation.inquiry.theRequest.maker:
                maker = orderConfirmation.quotation.inquiry.theRequest.maker.name
            else:
                maker = ""
            
            if orderConfirmation.quotation.inquiry.theRequest.makerType:
                makerType = orderConfirmation.quotation.inquiry.theRequest.makerType.type
            else:
                makerType = ""
                
            purchaseOrders = orderConfirmation.purchase_order_order_confirmation.order_by("-id").all()
            
            buyingTotalPrice = 0
            for purchaseOrder in purchaseOrders:
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
            data["Project No"].append(orderConfirmation.project.projectNo)
            data["SOC"].append(orderConfirmation.orderConfirmationNo)
            data["Confirm"].append(orderConfirmation.orderConfirmationDate)
            data["Reference"].append(orderConfirmation.quotation.inquiry.theRequest.customerRef)
            data["Customer"].append(orderConfirmation.quotation.inquiry.theRequest.customer.name)
            data["Vessel"].append(vessel)
            data["Maker"].append(maker)
            data["Type"].append(makerType)
            data["B. Total"].append(buyingTotalPrice)
            data["S. Total"].append(orderConfirmation.quotation.totalSellingPrice)
            data["Currency"].append(orderConfirmation.quotation.currency.code)
            data["Project Creator"].append(str(orderConfirmation.project.user.first_name)+" "+str(orderConfirmation.project.user.last_name))
            data["Project Status"].append(orderConfirmation.project.stage)
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/all-order-confirmations.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Order Confirmation', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/sale/order_confirmation/documents/all-order-confirmations.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'
        
        return response

class OrderConfirmationFilterExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("OrderConfirmation Excel")
        
        elementTag = "orderConfirmationExcel"
        elementTagSub = "orderConfirmationPartExcel"
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "sessionKey" : request.session.session_key
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/order_confirmation/order_confirmation_excel.html', context)       

class OrderConfirmationExportExcelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "sale", "order_confirmation", "documents")
        
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
            
        if request.GET.get("oc") == "false":
            projectExcludeStages.append("request")
            projectExcludeStages.append("inquiry")
            projectExcludeStages.append("quotation")
            projectExcludeStages.append("order_confirmation")
            projectExcludeStages.append("order_not_confirmation")
        
        if request.GET.get("po") == "false":
            projectExcludeStages.append("purchase_order")
            
        if request.GET.get("ot") == "false":
            projectExcludeStages.append("order_tracking")
            
        if request.GET.get("i") == "false":
            projectExcludeStages.append("invoiced")
        
        companies = request.GET.get("c")
        
        if companies:
            companies = companies.split(",")
        else:
            companies = []
        
        orderConfirmations = OrderConfirmation.objects.select_related("project","quotation__inquiry__theRequest").exclude(
            project__stage__in=projectExcludeStages
        ).filter(
            sourceCompany = request.user.profile.sourceCompany,
            created_date__date__range=(startDate,endDate),quotation__inquiry__theRequest__customer__id__in=companies
        ).order_by("-id")
        
        data = {
            "Line": [],
            "Project No": [],
            "SOC": [],
            "Confirm": [],
            "Reference": [],
            "Customer": [],
            "Vessel": [],
            "Maker": [],
            "Type": [],
            "B. Total": [],
            "S. Total": [],
            "Currency": [],
            "Project Creator": [],
            "Project Status": []
        }
        
        channel_layer = get_channel_layer()
        
        seq = 0
        for orderConfirmation in orderConfirmations:
            async_to_sync(channel_layer.group_send)(
                'private_' + str(request.user.id),
                {
                    "type": "send_percent",
                    "message": seq,
                    "location" : "order_confirmation_excel",
                    "totalCount" : len(orderConfirmations),
                    "ready" : "false"
                }
            )
            
            if orderConfirmation.quotation.inquiry.theRequest.vessel:
                vessel = orderConfirmation.quotation.inquiry.theRequest.vessel.name
            else:
                vessel = ""
            
            if orderConfirmation.quotation.inquiry.theRequest.maker:
                maker = orderConfirmation.quotation.inquiry.theRequest.maker.name
            else:
                maker = ""
            
            if orderConfirmation.quotation.inquiry.theRequest.makerType:
                makerType = orderConfirmation.quotation.inquiry.theRequest.makerType.type
            else:
                makerType = ""
                
            purchaseOrders = orderConfirmation.purchase_order_order_confirmation.order_by("-id").filter(sourceCompany = request.user.profile.sourceCompany)
            
            parts = orderConfirmation.quotation.quotationpart_set.all()
            
            buyingTotalPrice = 0
            
            partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
                
            partsTotal = 0
            
            for part in parts:
                partsTotal  = partsTotal + part.totalPrice1
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice1
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice1
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice1
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice1
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice1
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice1
            
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
            
            buyingTotalPrice = buyingTotalPrice + round(partsTotals["totalFinal"],2)
            
            
            # for purchaseOrder in purchaseOrders:
                
            #     parts = PurchaseOrderPart.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,purchaseOrder = purchaseOrder)
        
            #     partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
                
            #     partsTotal = 0
                
            #     for part in parts:
            #         partsTotal  = partsTotal + part.totalPrice
            #         partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
            #         partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
            #         partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
            #         partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
            #         partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
            #         partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
                
            #     if purchaseOrder.discountAmount > 0:
            #         partsTotals["totalDiscount"] = purchaseOrder.discountAmount
            #     else:
            #         partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (purchaseOrder.discount/100)
            #     partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
                
            #     buyingTotalPrice = buyingTotalPrice + round(partsTotals["totalFinal"],2)
            
            data["Line"].append(seq)
            data["Project No"].append(orderConfirmation.project.projectNo)
            data["SOC"].append(orderConfirmation.orderConfirmationNo)
            data["Confirm"].append(orderConfirmation.orderConfirmationDate)
            data["Reference"].append(orderConfirmation.quotation.inquiry.theRequest.customerRef)
            data["Customer"].append(orderConfirmation.quotation.inquiry.theRequest.customer.name)
            data["Vessel"].append(vessel)
            data["Maker"].append(maker)
            data["Type"].append(makerType)
            data["B. Total"].append(buyingTotalPrice)
            data["S. Total"].append(orderConfirmation.quotation.totalSellingPrice)
            data["Currency"].append(orderConfirmation.quotation.currency.code)
            data["Project Creator"].append(str(orderConfirmation.project.user.first_name)+" "+str(orderConfirmation.project.user.last_name))
            data["Project Status"].append(orderConfirmation.project.stage)
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)
        
        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/all-order-confirmations.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Order Confirmation', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        if orderConfirmations:
            orderConfirmationsCount = len(orderConfirmations)
        else:
            orderConfirmationsCount = 0
        async_to_sync(channel_layer.group_send)(
            'private_' + str(request.user.id),
            {
                "type": "send_percent",
                "message": seq,
                "location" : "order_confirmation_excel",
                "totalCount" : orderConfirmationsCount,
                "ready" : "true"
            }
        )
        
        return HttpResponse(status=204)

class OrderConfirmationDownloadExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/sale/order_confirmation/documents/all-order-confirmations.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'
        
        return response
  

class OrderConfirmationDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Order Confirmation")
        
        idList = list.split(",")
        
        elementTag = "orderConfirmation"
        elementTagSub = "orderConfirmationPart"
        elementTagId = idList[0]
        
        if len(idList) == 1:
            orderConfirmation = OrderConfirmation.objects.filter(id = int(idList[0])).first()
            purchaseOrders = PurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderConfirmation = orderConfirmation)
            proformaInvoices = ProformaInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderConfirmation = orderConfirmation)
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        if len(purchaseOrders) > 0:
            alertMessage = f"{orderConfirmation.orderConfirmationNo} cannot be deleted because it has purchase order"
            context = {
                "tag": tag,
                "alertMessage" : alertMessage
            }
            return render(request, 'sale/order_confirmation/order_confirmation_alert.html', context)
        elif len(proformaInvoices) > 0:
            alertMessage = f"{orderConfirmation.orderConfirmationNo} cannot be deleted because it has proforma invoice"
            context = {
                "tag": tag,
                "alertMessage" : alertMessage
            }
            return render(request, 'sale/order_confirmation/order_confirmation_alert.html', context)
        else:
            context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId
            }  
            return render(request, 'sale/order_confirmation/order_confirmation_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        for index, id in enumerate(idList):
            percent = (80/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false") 
            orderConfirmation = get_object_or_404(OrderConfirmation, id = id)
            
            quotation = orderConfirmation.quotation
            quotation.approval = "approved"
            quotation.save()
            project = orderConfirmation.project
            project.stage = "quotation"
            project.save()
            
            orderConfirmation.delete()
        pageLoad(request,100,100,"true")
        
        return HttpResponse(status=204)
  