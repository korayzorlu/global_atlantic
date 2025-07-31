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

from django.utils import timezone
from datetime import datetime, timedelta

from ..forms import *
from ..tasks import *
from ..pdfs.proforma_invoice_pdfs import *

from sale.models import OrderTracking, OrderConfirmation, Delivery
from source.models import Company as SourceCompany

import random
import string


class ProformaInvoiceDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Proforma Invoice")
        elementTag = "proformaInvoice"
        elementTagSub = "proformaInvoicePart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/proforma_invoice/proforma_invoices.html', context)
    
class ProformaInvoiceAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Proforma Invoice")
        
        elementTag = "proformaInvoiceAdd"
        elementTagSub = "proformaInvoicePartInAdd"
        elementTagId = id
        
        orderConfirmation = get_object_or_404(OrderConfirmation, id = id)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderConfirmation" : orderConfirmation
        }
        return render(request, 'account/proforma_invoice/proforma_invoice_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        orderConfirmation = get_object_or_404(OrderConfirmation, id = id)
        quotation = orderConfirmation.quotation
        parts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
        
        if orderConfirmation.quotation.inquiry.theRequest.vessel:
            billing = Billing.objects.filter(sourceCompany = request.user.profile.sourceCompany,vessel = orderConfirmation.quotation.inquiry.theRequest.vessel).first()
        else:
            billing = None
        
        proformaInvoice = ProformaInvoice.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            project = orderConfirmation.project,
            theRequest = quotation.inquiry.theRequest,
            orderConfirmation = orderConfirmation,
            seller = SourceCompany.objects.get(id = request.user.profile.sourceCompany.id),
            customer = orderConfirmation.quotation.inquiry.theRequest.customer,
            vessel = orderConfirmation.quotation.inquiry.theRequest.vessel,
            billing = billing,
            exchangeRate = quotation.currency.forexBuying,
            currency = quotation.currency,
            vat = orderConfirmation.vat
        )
        
        orderConfirmation.invoiced = True
        orderConfirmation.proformaInvoiced = True
        orderConfirmation.save()
        
        identificationCode = request.user.profile.sourceCompany.accountProformaInvoiceCode
        yearCode = int(str(datetime.today().date().year)[-2:])
        startCodeValue = 1
        
        lastProformaInvoice = ProformaInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
        
        if lastProformaInvoice:
            lastCode = lastProformaInvoice.code
        else:
            lastCode = startCodeValue - 1
        
        code = int(lastCode) + 1
        proformaInvoice.code = code
        
        proformaInvoice.yearCode = yearCode
        
        proformaInvoiceNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        proformaInvoice.proformaInvoiceNo = proformaInvoiceNo
        
        proformaInvoice.save()
        
        proformaInvoice.paymentDate = timezone.now() + timedelta(days=proformaInvoice.customer.creditPeriod)
        proformaInvoice.save()
        
        expenses =ProformaInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = proformaInvoice)
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
            
            proformaInvoicePart = ProformaInvoiceItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    invoice = proformaInvoice,
                    quotationPart = part,
                    part = part.inquiryPart.requestPart.part,
                    name = part.inquiryPart.requestPart.part.partNo,
                    description = part.inquiryPart.requestPart.part.description,
                    unit = part.inquiryPart.requestPart.part.unit,
                    quantity = part.quantity,
                    unitPrice = part.unitPrice3,
                    totalPrice = part.totalPrice3
                )
            proformaInvoicePart.save()
        
        proformaInvoiceParts = ProformaInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = proformaInvoice).order_by("quotationPart__sequency")
        sequencyCount = 0
        for proformaInvoicePart in proformaInvoiceParts:
            proformaInvoicePart.sequency = sequencyCount + 1
            proformaInvoicePart.save()
            sequencyCount = sequencyCount + 1
            
        for expense in expenses:
            partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
        
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
        
        if proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount > 0:
            partsTotals["totalDiscount"] = proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount
        else:
            partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (proformaInvoice.orderConfirmation.quotation.manuelDiscount/100)
        partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (proformaInvoice.vat/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
        
        remainingPrice = float(partsTotals["totalFinal"]) - float(proformaInvoice.paidPrice)
        
        proformaInvoice.discountPrice = round(partsTotals["totalDiscount"],2)
        proformaInvoice.vatPrice = round(partsTotals["totalVat"],2)
        proformaInvoice.netPrice = round(partsTotals["totalTotalPrice3"],2)
        proformaInvoice.totalPrice = round(partsTotals["totalFinal"],2)
        proformaInvoice.save()
        
        project = orderConfirmation.project
        theRequest = Request.objects.get(project = project)
        orderTracking = OrderTracking.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = theRequest).first()
        delivery = Delivery.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking).first()
        activeProject = Offer.objects.none().first()
        
        proformaInvoicePdf(theRequest, orderConfirmation, proformaInvoice, delivery, activeProject, request.user.profile.sourceCompany)
          
        return HttpResponse(status=204)

class ServiceProformaInvoiceAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Proforma Invoice")
        
        elementTag = "serviceProformaInvoiceAdd"
        elementTagSub = "serviceProformaInvoicePartInAdd"
        elementTagId = id
        
        activeProject = get_object_or_404(Offer, id = id)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "activeProject" : activeProject
        }
        return render(request, 'account/service_proforma_invoice_add.html', context)
    
    def post(self, request, id, *args, **kwargs):
        activeProject = get_object_or_404(Offer, id = id)
        serviceCards = OfferServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        print(serviceCards)
        parts = OfferPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        activeProjectExpenses = OfferExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        
        if activeProject.vessel:
            billing = Billing.objects.filter(sourceCompany = request.user.profile.sourceCompany,vessel = activeProject.vessel).first()
        else:
            billing = None
        
        proformaInvoice = ProformaInvoice.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            offer = activeProject,
            seller = SourceCompany.objects.get(id = request.user.profile.sourceCompany.id),
            customer = activeProject.customer,
            vessel = activeProject.vessel,
            billing = billing,
            exchangeRate = activeProject.currency.forexBuying,
            currency = activeProject.currency,
            group = "service"
        )
        
        # activeProject.invoiced = True
        # activeProject.proformaInvoiced = True
        # activeProject.save()
        
        identificationCode = request.user.profile.sourceCompany.accountProformaInvoiceCode
        yearCode = int(str(datetime.today().date().year)[-2:])
        startCodeValue = 1
        
        lastProformaInvoice = ProformaInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
        
        if lastProformaInvoice:
            lastCode = lastProformaInvoice.code
        else:
            lastCode = startCodeValue - 1
        
        code = int(lastCode) + 1
        proformaInvoice.code = code
        
        proformaInvoice.yearCode = yearCode
        
        proformaInvoiceNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        proformaInvoice.proformaInvoiceNo = proformaInvoiceNo
        
        proformaInvoice.save()
        
        proformaInvoice.paymentDate = timezone.now() + timedelta(days=proformaInvoice.customer.creditPeriod)
        proformaInvoice.save()
        
        expenses =ProformaInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = proformaInvoice)
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
        
        partsTotal = 0
        
        sequencyCount = 0
        
        for serviceCard in serviceCards:
            partsTotal  = partsTotal + serviceCard.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + serviceCard.unitPrice1
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + serviceCard.unitPrice2
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + serviceCard.unitPrice3
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + serviceCard.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + serviceCard.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + serviceCard.totalPrice
            
            proformaInvoicePart = ProformaInvoiceItem.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                user = request.user,
                invoice = proformaInvoice,
                offerServiceCard = serviceCard,
                serviceCard = serviceCard.serviceCard,
                name = serviceCard.serviceCard.code,
                description = serviceCard.serviceCard.name,
                unit = serviceCard.serviceCard.unit,
                quantity = serviceCard.quantity,
                unitPrice = serviceCard.unitPrice3,
                totalPrice = serviceCard.totalPrice,
                sequency = sequencyCount + 1
            )
            proformaInvoicePart.save()
            sequencyCount = sequencyCount + 1
        
        for part in parts:
            partsTotal  = partsTotal + part.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
            
            proformaInvoicePart = ProformaInvoiceItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    invoice = proformaInvoice,
                    offerPart = part,
                    part = part.part,
                    name = part.part.partNo,
                    description = part.part.description,
                    unit = part.part.unit,
                    quantity = part.quantity,
                    unitPrice = part.unitPrice,
                    totalPrice = part.totalPrice,
                    sequency = sequencyCount + 1
                )
            proformaInvoicePart.save()
            sequencyCount = sequencyCount + 1
            
        for activeProjectExpense in activeProjectExpenses:
            partsTotal  = partsTotal + activeProjectExpense.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + activeProjectExpense.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + activeProjectExpense.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + activeProjectExpense.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + activeProjectExpense.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + activeProjectExpense.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + activeProjectExpense.totalPrice
            
            proformaInvoicePart = ProformaInvoiceItem.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    invoice = proformaInvoice,
                    offerExpense = activeProjectExpense,
                    expense = activeProjectExpense.expense,
                    name = activeProjectExpense.expense.code,
                    description = activeProjectExpense.expense.name,
                    unit = activeProjectExpense.expense.unit,
                    quantity = activeProjectExpense.quantity,
                    unitPrice = activeProjectExpense.unitPrice,
                    totalPrice = activeProjectExpense.totalPrice,
                    sequency = sequencyCount + 1
                )
            proformaInvoicePart.save()
            sequencyCount = sequencyCount + 1
            
        for expense in expenses:
            partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
        
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
        
        if proformaInvoice.orderConfirmation:
            if proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount > 0:
                partsTotals["totalDiscount"] = proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (proformaInvoice.orderConfirmation.quotation.manuelDiscount/100)
            
        if proformaInvoice.offer:   
            if proformaInvoice.offer.discountAmount > 0:
                partsTotals["totalDiscount"] = proformaInvoice.offer.discountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (proformaInvoice.offer.discount/100)
        
        partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (proformaInvoice.vat/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
        
        remainingPrice = float(partsTotals["totalFinal"]) - float(proformaInvoice.paidPrice)
        
        proformaInvoice.discountPrice = round(partsTotals["totalDiscount"],2)
        proformaInvoice.vatPrice = round(partsTotals["totalVat"],2)
        proformaInvoice.netPrice = round(partsTotals["totalTotalPrice3"],2)
        proformaInvoice.totalPrice = round(partsTotals["totalFinal"],2)
        proformaInvoice.save()
        
        theRequest = Request.objects.none().first()
        orderTracking = OrderTracking.objects.none().first()
        delivery = Delivery.objects.none().first()
        orderConfirmation = OrderConfirmation.objects.none().first()
        
        proformaInvoicePdf(theRequest, orderConfirmation, proformaInvoice, delivery, activeProject, request.user.profile.sourceCompany)
          
        return HttpResponse(status=204)

class ProformaInvoiceUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Proforma Invoice Detail")
        elementTag = "proformaInvoice"
        elementTagSub = "proformaInvoicePart"
        elementTagId = id
        
        proformaInvoices = ProformaInvoice.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        proformaInvoice = get_object_or_404(ProformaInvoice, id = id)
        #quotationParts = QuotationPart.objects.filter(quotation = orderConfirmation.quotation)
        
        parts = ProformaInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = proformaInvoice)
        expenses = ProformaInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = proformaInvoice)
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
        
        proformaInvoicePartList = []
        
        partsTotal = 0
        
        for part in parts:
            proformaInvoicePartList.append(part.id)
            
            partsTotal  = partsTotal + part.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
        for expense in expenses:
            partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
        
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
        
        if proformaInvoice.orderConfirmation:
            if proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount > 0:
                partsTotals["totalDiscount"] = proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (proformaInvoice.orderConfirmation.quotation.manuelDiscount/100)
        else:
            partsTotals["totalDiscount"] = 0

        if proformaInvoice.offer:   
            if proformaInvoice.offer.discountAmount > 0:
                partsTotals["totalDiscount"] = proformaInvoice.offer.discountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (proformaInvoice.offer.discount/100)
            
        partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (proformaInvoice.vat/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
        
        remainingPrice = float(partsTotals["totalFinal"]) - float(proformaInvoice.paidPrice)
        
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
        
        form = ProformaInvoiceForm(request.POST or None, request.FILES or None, instance = proformaInvoice, user=request.user)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "proformaInvoices" : proformaInvoices,
                "proformaInvoice" : proformaInvoice,
                "proformaInvoicePartList" : proformaInvoicePartList,
                "partsTotals" : partsTotals,
                "parts" : parts,
                "partsTotal" : partsTotal,
                "remainingPrice" : remainingPrice,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        return render(request, 'account/proforma_invoice/proforma_invoice_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        proformaInvoice = get_object_or_404(ProformaInvoice, id = id)
        user = proformaInvoice.user
        activeProject = proformaInvoice.offer
        project = proformaInvoice.project
        theRequest = proformaInvoice.theRequest
        orderConfirmation = proformaInvoice.orderConfirmation
        seller = proformaInvoice.seller
        customer = proformaInvoice.customer
        identificationCode = proformaInvoice.identificationCode
        code = proformaInvoice.code
        yearCode = proformaInvoice.yearCode
        proformaInvoiceNo = proformaInvoice.proformaInvoiceNo
        currency = proformaInvoice.currency
        sourceCompany = proformaInvoice.sourceCompany
        #parts = SendInvoicePart.objects.filter(invoice = sendInvoice)
        
        form = ProformaInvoiceForm(request.POST, request.FILES or None, instance = proformaInvoice, user=request.user)
        
        vessel = request.POST.getlist("vessel")[0]
        if vessel:
            form.fields['billing'].queryset = Billing.objects.filter(sourceCompany = request.user.profile.sourceCompany,vessel=int(vessel))
        
        if form.is_valid():
            if not request.POST.get("exchangeRate"):
                data = {'message': 'Please fill out the "Exchange Rate" field.'}
                return JsonResponse(data, status=404)
            proformaInvoice = form.save(commit = False)
            proformaInvoice.sourceCompany = sourceCompany
            proformaInvoice.user = user
            proformaInvoice.offer = activeProject
            proformaInvoice.project = project
            proformaInvoice.orderConfirmation = orderConfirmation
            proformaInvoice.theRequest = theRequest
            proformaInvoice.seller = seller
            proformaInvoice.customer = customer
            proformaInvoice.identificationCode = identificationCode
            proformaInvoice.code = code
            proformaInvoice.yearCode = yearCode
            proformaInvoice.proformaInvoiceNo = proformaInvoiceNo
            proformaInvoice.currency = currency
            
            proformaInvoice.save()
            
            parts = ProformaInvoiceItem.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = proformaInvoice)
            expenses = ProformaInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = proformaInvoice)
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
            for expense in expenses:
                partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
            
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
            
            if proformaInvoice.orderConfirmation:
                if proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount > 0:
                    partsTotals["totalDiscount"] = proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount
                else:
                    partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (proformaInvoice.orderConfirmation.quotation.manuelDiscount/100)
            
            if proformaInvoice.offer:   
                if proformaInvoice.offer.discountAmount > 0:
                    partsTotals["totalDiscount"] = proformaInvoice.offer.discountAmount
                else:
                    partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (proformaInvoice.offer.discount/100)
            
            partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (proformaInvoice.vat/100)
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
            
            remainingPrice = float(partsTotals["totalFinal"]) - float(proformaInvoice.paidPrice)
            
            proformaInvoice.discountPrice = round(partsTotals["totalDiscount"],2)
            proformaInvoice.vatPrice = round(partsTotals["totalVat"],2)
            proformaInvoice.netPrice = round(partsTotals["totalTotalPrice3"],2)
            proformaInvoice.totalPrice = round(partsTotals["totalFinal"],2)
            proformaInvoice.save()
            
            orderTracking = OrderTracking.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = theRequest).first()
            delivery = Delivery.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking).first()
            
            proformaInvoicePdf(theRequest, orderConfirmation, proformaInvoice, delivery, activeProject, request.user.profile.sourceCompany)
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'account/proforma_invoice_detail.html', context)

class ProformaInvoiceDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Invoice")
        
        elementTag = "proformaInvoice"
        elementTagSub = "proformaInvoicePart"
        
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
        
        return render(request, 'account/proforma_invoice/proforma_invoice_delete.html', context)
    
    def post(self, request, list,  *args, **kwargs):
        idList = list.split(",")
        for id in idList:   
            proformaInvoice = get_object_or_404(ProformaInvoice, id = int(id))
            proformaInvoice.delete()
            orderConfirmation = proformaInvoice.orderConfirmation
            orderConfirmation.proformaInvoiced = False
            orderConfirmation.save()
        return HttpResponse(status=204)

class ProformaInvoicePdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Order Confirmation PDF")
        
        elementTag = "proformaInvoice"
        elementTagSub = "proformaInvoicePart"
        elementTagId = str(id) + "-pdf"
        
        proformaInvoice = get_object_or_404(ProformaInvoice, id = id)
        orderConfirmation = proformaInvoice.orderConfirmation
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #orderConfirmationPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderConfirmation" : orderConfirmation,
                "proformaInvoice" : proformaInvoice,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/proforma_invoice/proforma_invoice_pdf.html', context)

class ProformaInvoiceExpenseInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Proforma ")
        elementTag = "proformaInvoice"
        elementTagSub = "proformaInvoicePart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        invoiceId = refererPath.replace("/account/proforma_invoice_update/","").replace("/","")
        invoice = get_object_or_404(ProformaInvoice, id = id)
        
        form = ProformaInvoiceExpenseForm(request.POST or None, request.FILES or None, user = request.user)
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

        return render(request, 'account/proforma_invoice/proforma_invoice_expense_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        invoiceId = refererPath.replace("/account/proforma_invoice_update/","").replace("/","")
        
        invoice = ProformaInvoice.objects.get(id = id)
        proformaInvoiceExpenses = ProformaInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = invoice)
        
        form = ProformaInvoiceExpenseForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            proformaInvoiceExpense = form.save(commit = False)
            proformaInvoiceExpense.sourceCompany = request.user.profile.sourceCompany
            
            proformaInvoiceExpense.user = request.user
            proformaInvoiceExpense.invoice = invoice
            proformaInvoiceExpense.save()
            
            orderTracking = OrderTracking.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = invoice.theRequest).first()
            delivery = Delivery.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking).first()
            
            proformaInvoicePdf(invoice.theRequest, invoice.orderConfirmation, invoice, delivery, invoice.offer, request.user.profile.sourceCompany)
        
            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)

class ProformaInvoiceExpenseDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Proforma Invoice")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/proforma_invoice/proforma_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            proformaInvoiceExpense = get_object_or_404(ProformaInvoiceExpense, id = int(id))
            
            invoice = proformaInvoiceExpense.invoice
            
            proformaInvoiceExpense.delete()
            
            orderTracking = OrderTracking.objects.filter(sourceCompany = request.user.profile.sourceCompany,theRequest = invoice.theRequest).first()
            delivery = Delivery.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderTracking = orderTracking).first()
        
            proformaInvoicePdf(invoice.theRequest, invoice.orderConfirmation, invoice, delivery, invoice.offer, request.user.profile.sourceCompany)
            
        return HttpResponse(status=204)

class ProformaInvoicePartCurrencyUpdateView(LoginRequiredMixin, View):
    def post(self, request, id, cid, *args, **kwargs):
        proformaInvoice = ProformaInvoice.objects.filter(id = id).first()
        oldCurrency = proformaInvoice.currency
        newCurrency = Currency.objects.filter(id = cid).first()
        
        parts = ProformaInvoicePart.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = proformaInvoice)
        expenses = ProformaInvoiceExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,invoice = proformaInvoice)
        
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
        
        partsTotal = 0
        
        for part in parts:
            unitPrice = round((part.unitPrice * oldCurrency.forexBuying) / newCurrency.forexBuying,2)
            totalPrice = float(unitPrice) * float(part.quantity)
            part.unitPrice = unitPrice
            part.totalPrice = totalPrice
            part.save()
            proformaInvoice.currency = newCurrency
            proformaInvoice.save()
            
            partsTotal  = partsTotal + part.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice

        if proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount > 0:
            partsTotals["totalDiscount"] = proformaInvoice.orderConfirmation.quotation.manuelDiscountAmount
        else:
            partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (proformaInvoice.orderConfirmation.quotation.manuelDiscount/100)
            
        for expense in expenses:
            unitPrice = round((expense.unitPrice * oldCurrency.forexBuying) / newCurrency.forexBuying,2)
            totalPrice = float(unitPrice) * float(expense.quantity)
            expense.unitPrice = unitPrice
            expense.totalPrice = totalPrice
            expense.save()
            
            partsTotals["totalExpense"] = partsTotals["totalExpense"] + expense.totalPrice
        
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
        partsTotals["totalVat"] = (partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]) * (proformaInvoice.vat/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"] + partsTotals["totalVat"]
        
        proformaInvoice.discountPrice = round(partsTotals["totalDiscount"],2)
        proformaInvoice.vatPrice = round(partsTotals["totalVat"],2)
        proformaInvoice.netPrice = round(partsTotals["totalTotalPrice3"],2)
        proformaInvoice.totalPrice = round(partsTotals["totalFinal"],2)
        proformaInvoice.save()
            
        return HttpResponse(status=204)

class ProformaInvoicePartDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Proforma Invoice Part")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/proforma_invoice/proforma_invoice_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            proformaInvoicePart = get_object_or_404(ProformaInvoicePart, id = int(id))
            proformaInvoicePart.delete()
        return HttpResponse(status=204)
