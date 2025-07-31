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
from ..pdfs.commerical_invoice_pdfs import *

from sale.models import OrderTracking
from source.models import Company as SourceCompany



import random
import string

class CommericalInvoiceDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Commerical Inv.")
        elementTag = "commericalInvoice"
        elementTagSub = "commericalInvoicePart"

        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/commerical_invoices.html', context)

class CommericalInvoiceAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Commerical Invoice")
        
        elementTag = "commericalInvoiceAdd"
        elementTagSub = "commericalInvoicePartInAdd"
        elementTagId = id
        
        orderTracking = get_object_or_404(OrderTracking, id = id)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderTracking" : orderTracking
        }
        return render(request, 'account/commerical_invoice_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        orderTracking = get_object_or_404(OrderTracking, id = id)
        quotation = orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation
        parts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
        
        billing = Billing.objects.filter(sourceCompany = request.user.profile.sourceCompany,vessel = orderTracking.theRequest.vessel).first()
        commericalInvoice = CommericalInvoice.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            project = orderTracking.project,
            projectNo = orderTracking.project.projectNo,
            theRequest = orderTracking.theRequest,
            orderTracking = orderTracking,
            seller = SourceCompany.objects.get(id = request.user.profile.sourceCompany.id),
            customer = orderTracking.theRequest.customer,
            customerName = orderTracking.theRequest.customer.name,
            vessel = orderTracking.theRequest.vessel,
            billing = billing,
            currency = quotation.currency,
            vat = orderTracking.purchaseOrders.all()[0].orderConfirmation.vat
        )
        
        identificationCode = request.user.profile.sourceCompany.accountCommercialInvoiceCode
        yearCode = int(str(datetime.today().date().year)[-2:])
        startCodeValue = 1
        lastCommericalInvoice = CommericalInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
        
        if lastCommericalInvoice:
            lastCode = lastCommericalInvoice.code
        else:
            lastCode = startCodeValue - 1
        
        code = int(lastCode) + 1
        commericalInvoice.code = code
        
        commericalInvoice.yearCode = yearCode
        
        commericalInvoiceNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        commericalInvoice.commericalInvoiceNo = commericalInvoiceNo
        
        commericalInvoice.save()
        
        commericalInvoice.paymentDate = timezone.now() + timedelta(days=commericalInvoice.customer.creditPeriod)
        commericalInvoice.save()
        
        expenses = CommericalInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = commericalInvoice)
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
        
        partsTotal = 0
        
        for part in parts:
            partsTotal  = partsTotal + part.totalPrice3
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice1
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice2
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice3
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice1
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice2
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice3
            
            commericalInvoicePart = CommericalInvoiceItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    invoice = commericalInvoice,
                    quotationPart = part,
                    part = part.inquiryPart.requestPart.part,
                    name = part.inquiryPart.requestPart.part.partNo,
                    description = part.inquiryPart.requestPart.part.description,
                    unit = part.inquiryPart.requestPart.part.unit,
                    quantity = part.quantity,
                    unitPrice = part.unitPrice3,
                    totalPrice = part.totalPrice3
                )
            commericalInvoicePart.save()
        
        commericalInvoiceParts = CommericalInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = commericalInvoice).order_by("quotationPart__sequency")
        sequencyCount = 0
        for commericalInvoicePart in commericalInvoiceParts:
            commericalInvoicePart.sequency = sequencyCount + 1
            commericalInvoicePart.save()
            sequencyCount = sequencyCount + 1
            
        for expense in expenses:
            partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
        
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
        
        if commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscountAmount > 0:
            partsTotals["totalDiscount"] = commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscountAmount
        else:
            partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscount/100)
        partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (commericalInvoice.vat/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
        
        commericalInvoice.discountPrice = round(partsTotals["totalDiscount"],2)
        commericalInvoice.vatPrice = round(partsTotals["totalVat"],2)
        commericalInvoice.netPrice = round(partsTotals["totalTotalPrice3"],2)
        commericalInvoice.totalPrice = round(partsTotals["totalFinal"],2)
        commericalInvoice.save()
        
        project = commericalInvoice.project
        theRequest = Request.objects.get(project = project)
        orderConfirmation = commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation
        
        commericalInvoicePdf(theRequest, orderConfirmation, commericalInvoice, request.user.profile.sourceCompany)
          
        return HttpResponse(status=204)

class CommericalInvoiceUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Commerical Invoice Detail")
        elementTag = "commericalInvoice"
        elementTagSub = "commericalInvoicePart"
        elementTagId = id
        
        commericalInvoices = CommericalInvoice.objects.filter()
        commericalInvoice = get_object_or_404(CommericalInvoice, id = id)
            
        parts = CommericalInvoiceItem.objects.filter(invoice = commericalInvoice)
        expenses = CommericalInvoiceExpense.objects.filter(invoice = commericalInvoice)
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
        
        commericalInvoicePartList = []
        
        partsTotal = 0
        
        for part in parts:
            commericalInvoicePartList.append(part.id)
            
            partsTotal  = partsTotal + part.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
        
        if commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscountAmount > 0:
            partsTotals["totalDiscount"] = commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscountAmount
        else:
            partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscount/100)
        
        for expense in expenses:
            partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
        
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
        partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (commericalInvoice.vat/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
        
        # Para miktarını belirtilen formatta gösterme
        partsTotals["totalTotalPrice3"] = "{:,.2f}".format(round(partsTotals["totalTotalPrice3"],2))
        partsTotals["totalDiscount"] = "{:,.2f}".format(round(partsTotals["totalDiscount"],2))
        partsTotals["totalVat"] = "{:,.2f}".format(round(partsTotals["totalVat"],2))
        partsTotals["totalFinal"] = "{:,.2f}".format(round(partsTotals["totalFinal"],2))
        # Nokta ile virgülü değiştirme
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
        partsTotals["totalDiscount"] = partsTotals["totalDiscount"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
        partsTotals["totalVat"] = partsTotals["totalVat"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
        partsTotals["totalFinal"] = partsTotals["totalFinal"].replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        form = CommericalInvoiceForm(request.POST or None, request.FILES or None, instance = commericalInvoice, user = request.user)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "commericalInvoices" : commericalInvoices,
                "commericalInvoice" : commericalInvoice,
                "partsTotals" : partsTotals,
                "parts" : parts,
                "commericalInvoicePartList" : commericalInvoicePartList,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }

        return render(request, 'account/commerical_invoice_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        commericalInvoice = get_object_or_404(CommericalInvoice, id = id)
        user = commericalInvoice.user
        project = commericalInvoice.project
        projectNo = commericalInvoice.projectNo
        theRequest = commericalInvoice.theRequest
        orderTracking = commericalInvoice.orderTracking
        seller = commericalInvoice.seller
        customer = commericalInvoice.customer
        customerName = commericalInvoice.customer.name
        identificationCode = commericalInvoice.identificationCode
        code = commericalInvoice.code
        yearCode = commericalInvoice.yearCode
        commericalInvoiceNo = commericalInvoice.commericalInvoiceNo
        group = commericalInvoice.group
        sourceCompany = commericalInvoice.sourceCompany
        #parts = SendInvoicePart.objects.filter(invoice = commericalInvoice)
        
        form = CommericalInvoiceForm(request.POST, request.FILES or None, instance = commericalInvoice, user = request.user)
        
        vessel = request.POST.getlist("vessel")[0]
        if vessel:
            form.fields['billing'].queryset = Billing.objects.filter(vessel=int(vessel))
        else:
            form.fields['billing'].queryset = Billing.objects.none()

        if form.is_valid():
            commericalInvoice = form.save(commit = False)
            commericalInvoice.sourceCompany = sourceCompany
            commericalInvoice.user = user
            commericalInvoice.project = project
            commericalInvoice.projectNo = projectNo
            commericalInvoice.orderTracking = orderTracking
            commericalInvoice.theRequest = theRequest
            commericalInvoice.seller = seller
            commericalInvoice.customer = customer
            commericalInvoice.customerName = customerName
            commericalInvoice.identificationCode = identificationCode
            commericalInvoice.code = code
            commericalInvoice.yearCode = yearCode
            commericalInvoice.commericalInvoiceNo = commericalInvoiceNo
            commericalInvoice.group = group

            parts = CommericalInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = commericalInvoice)
            expenses = CommericalInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = commericalInvoice)
            partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
            
            partsTotal = 0
            
            for part in parts:
                partsTotal  = partsTotal + part.totalPrice
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
                
            if commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscountAmount > 0:
                partsTotals["totalDiscount"] = commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscountAmount
            else:
                    partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation.quotation.manuelDiscount/100)

                
            for expense in expenses:
                partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
            
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
            partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (commericalInvoice.vat/100)
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
            
            commericalInvoice.discountPrice = round(partsTotals["totalDiscount"],2)
            commericalInvoice.vatPrice = round(partsTotals["totalVat"],2)
            commericalInvoice.netPrice = round(partsTotals["totalTotalPrice3"],2)
            commericalInvoice.totalPrice = round(partsTotals["totalFinal"],2)
            commericalInvoice.save()
            
            orderTracking = OrderTracking.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = theRequest).first()
            orderConfirmation = commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation
            
            commericalInvoicePdf(theRequest, orderConfirmation, commericalInvoice, request.user.profile.sourceCompany)
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'account/commerical_invoice_detail.html', context)


class CommericalInvoicePdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Commerical Invoice PDF")
        
        elementTag = "commericalInvoice"
        elementTagSub = "commericalInvoicePart"
        elementTagId = str(id) + "-pdf"
        
        commericalInvoice = get_object_or_404(CommericalInvoice, id = id)
        orderConfirmation = commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #orderConfirmationPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "commericalInvoice" : commericalInvoice,
                "orderConfirmation" : orderConfirmation,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/commerical_invoice_pdf.html', context)

class CommericalInvoicePdfInOTView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Commerical Invoice PDF")
        
        elementTag = "orderTracking"
        elementTagSub = "orderTrackingPart"
        elementTagId = str(id) + "-pdf"
        
        commericalInvoice = get_object_or_404(CommericalInvoice, id = id)
        orderConfirmation = commericalInvoice.orderTracking.purchaseOrders.all()[0].orderConfirmation
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #orderConfirmationPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "commericalInvoice" : commericalInvoice,
                "orderConfirmation" : orderConfirmation,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/commerical_invoice_pdf.html', context)

class CommericalInvoiceDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Invoice")
        elementTag = "commericalInvoice"
        elementTagSub = "commericalInvoicePart"
        
        idList = list.split(",")
        #ypeList = types.split(",")
        
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
        
        return render(request, 'account/commerical_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        #typeList = types.split(",")
        #combinedList = [{"id": idList_item, "type": typeList_item} for idList_item, typeList_item in zip(idList, typeList)]
        for id in idList:
            commericalInvoice = get_object_or_404(CommericalInvoice, id = int(id)) 
            commericalInvoice.delete()
        return HttpResponse(status=204)

class CommericalInvoiceItemDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Commerical Invoice")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/commerical_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            commericalInvoicePart = get_object_or_404(CommericalInvoiceItem, id = int(id))
            commericalInvoicePart.delete()
        return HttpResponse(status=204)

class CommericalInvoiceExpenseInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Commerical Invoice Expense ")
        elementTag = "commericalInvoice"
        elementTagSub = "commericalInvoicePart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        invoiceId = refererPath.replace("/account/commerical_invoice_update/","").replace("/","")
        invoice = get_object_or_404(CommericalInvoice, id = id)
        
        form = CommericalInvoiceExpenseForm(request.POST or None, request.FILES or None)
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

        return render(request, 'account/commerical_invoice_expense_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        invoiceId = refererPath.replace("/account/commerical_invoice_update/","").replace("/","")
        
        invoice = CommericalInvoice.objects.get(id = id)
        commericalInvoiceExpenses = CommericalInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = invoice)
        
        form = CommericalInvoiceExpenseForm(request.POST, request.FILES or None)
        if form.is_valid():
            commericalInvoiceExpense = form.save(commit = False)
            commericalInvoiceExpense.sourceCompany = request.user.profile.sourceCompany
            
            commericalInvoiceExpense.user = request.user
            commericalInvoiceExpense.invoice = invoice
            commericalInvoiceExpense.save()
            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)

class CommericalInvoiceExpenseDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Commerical Invoice")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/commerical_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            commericalInvoiceExpense = get_object_or_404(CommericalInvoiceExpense, id = int(id))
            commericalInvoiceExpense.delete()
        return HttpResponse(status=204)
