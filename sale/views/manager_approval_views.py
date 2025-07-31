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

class ManagerApprovalDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Pending Approvals")
        elementTag = "managerApproval"
        elementTagSub = "quotationPartMA"
        
        
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "user" : request.user
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/manager_approval/manager_approvals.html', context)
    
class ManagerApprovalUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Manager Approval Detail")
        elementTag = "managerApproval"
        elementTagSub = "quotationPartMA"
        elementTagId = id
    
        quotations = Quotation.objects.filter()
        quotation = get_object_or_404(Quotation, id = id)
        requestt = get_object_or_404(Request, project = quotation.project)
        parts = QuotationPart.objects.filter(quotation = quotation)
        
        partsTotal = 0
        
        quotationInquiryParts = []
        
        thePartsTotals = {}
        thePartsAvailabilities = {}
        
        for part in parts:
            quotationInquiryParts.append(part.inquiryPart)
            partsTotal  = partsTotal + part.totalPrice3
            thePartsTotals[part.inquiryPart.requestPart.part.partNo] = []
            thePartsAvailabilities[part.inquiryPart.requestPart.part.partNo] = []
        
        inquiries = Inquiry.objects.filter(project = quotation.project)
        
        inquiryParts = []
        inquiryPartsTotal = []
        inquiryPartss = InquiryPart.objects.filter(inquiry__project = inquiries[0].project)
        
        projectParts = {}
        
        for inquiry in inquiries:
            theParts = InquiryPart.objects.filter(inquiry = inquiry)
            thePartsTotal = 0
            for thePart in theParts:
                print("buraşura-" + str(thePart.requestPart.part.partNo));
                if thePart.requestPart.part.partNo in thePartsTotals.keys():
                    thePartsTotal = thePartsTotal + thePart.totalPrice
                    thePartsTotals[thePart.requestPart.part.partNo].append(thePart.totalPrice)
                    thePartsAvailabilities[thePart.requestPart.part.partNo].append(thePart.availability)
                    if thePart.requestPart.part.partNo not in projectParts:
                        projectParts[thePart.requestPart.part.partNo] = thePart
                else:
                    thePartsTotal = thePartsTotal + thePart.totalPrice
                    thePartsTotals[thePart.requestPart.part.partNo] = [thePart.totalPrice]
                    thePartsAvailabilities[thePart.requestPart.part.partNo] = [thePart.availability]
                    projectParts[thePart.requestPart.part.partNo] = thePart
            inquiryParts.append({"parts" : theParts, "total" : thePartsTotal, "min" : False})
            inquiryPartsTotal.append(thePartsTotal)
            
        for inquiryPart in inquiryParts:
            if inquiryPart["total"] == min(inquiryPartsTotal):
                inquiryPart["min"] = True

        for thePartsTotal in thePartsTotals:
            thePartsTotals[thePartsTotal] = min(thePartsTotals[thePartsTotal])
            
        for thePartsAvailability in thePartsAvailabilities:
            thePartsAvailabilities[thePartsAvailability] = min(thePartsAvailabilities[thePartsAvailability])
        
        form = QuotationForm(request.POST or None, request.FILES or None, instance = quotation)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "quotations" : quotations,
                "quotation" : quotation,
                "requestt" : requestt,
                "parts" : parts,
                "projectParts" : projectParts,
                "partsTotal" : partsTotal,
                "thePartsTotals" : thePartsTotals,
                "thePartsAvailabilities" : thePartsAvailabilities,
                "quotationInquiryParts" : quotationInquiryParts,
                "inquiries" : inquiries,
                "inquiryParts" : inquiryParts,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/manager_approval/manager_approval_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        quotation = get_object_or_404(Quotation, id = id)
        project = quotation.project
        inquiry = quotation.inquiry
        soc = quotation.soc
        identificationCode = quotation.identificationCode
        code = quotation.code
        yearCode = quotation.yearCode
        quotationNo = quotation.quotationNo
        person = quotation.person
        validity = quotation.validity
        currency = quotation.currency
        payment = quotation.payment
        delivery = quotation.delivery
        remark = quotation.remark
        parts = quotation.parts
        approval = quotation.approval
        quotationDate = quotation.quotationDate
        
        form = QuotationForm(request.POST, request.FILES or None, instance = quotation)
        
        if form.is_valid():
            if "approvedButton" in request.POST:
                quotation = form.save(commit = False)
                quotation.project = project
                quotation.inquiry = inquiry
                quotation.soc = soc
                quotation.identificationCode = identificationCode
                quotation.code = code
                quotation.yearCode = yearCode
                quotation.quotationNo = quotationNo
                quotation.person = person
                quotation.validity = validity
                quotation.currency = currency
                quotation.payment = payment
                quotation.delivery = delivery
                quotation.remark = remark
                quotation.quotationDate = quotationDate
                quotation.approval = "approved"
                quotation.save()
                
                return HttpResponse(status=204)
            
            elif "notApprovedButton" in request.POST:
                quotation = form.save(commit = False)
                quotation.project = project
                quotation.inquiry = inquiry
                quotation.soc = soc
                quotation.identificationCode = identificationCode
                quotation.code = code
                quotation.yearCode = yearCode
                quotation.quotationNo = quotationNo
                quotation.person = person
                quotation.validity = validity
                quotation.currency = currency
                quotation.payment = payment
                quotation.delivery = delivery
                quotation.remark = remark
                quotation.quotationDate = quotationDate
                quotation.approval = "notApproved"
                quotation.save()
                
                return HttpResponse(status=204)
            
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'sale/manager_approval/manager_approval_detail.html', context)
        
class ManagerApprovalUpdateInDashboardView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Manager Approval Detail")
        elementTag = "managerApproval"
        elementTagSub = "quotationPartMA"
    
        quotations = Quotation.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        quotation = get_object_or_404(Quotation, id = id)
        requestt = get_object_or_404(Request, project = quotation.project)
        parts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
        
        inquirires = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany,project = quotation.project)
        
        inquiryParts = []
        
        for inquiry in inquirires:
            inquiryParts.append(InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry))
        
        print(inquiryParts)
        
        total = 0
        
        for part in parts:
            total = total + part.totalPrice3
        
        form = QuotationForm(request.POST or None, request.FILES or None, instance = quotation)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "form" : form,
                "quotations" : quotations,
                "quotation" : quotation,
                "requestt" : requestt,
                "parts" : parts,
                "inquirires" : inquirires,
                "inquiryParts" : inquiryParts,
                "total" : total,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/manager_approval/manager_approval_detail_in_dashboard.html', context)
    
    def post(self, request, id, *args, **kwargs):
        quotation = get_object_or_404(Quotation, id = id)
        project = quotation.project
        inquiry = quotation.inquiry
        soc = quotation.soc
        identificationCode = quotation.identificationCode
        code = quotation.code
        yearCode = quotation.yearCode
        quotationNo = quotation.quotationNo
        person = quotation.person
        validity = quotation.validity
        currency = quotation.currency
        payment = quotation.payment
        delivery = quotation.delivery
        remark = quotation.remark
        parts = quotation.parts
        approval = quotation.approval
        quotationDate = quotation.quotationDate
        sourceCompany = quotation.sourceCompany
        
        form = QuotationForm(request.POST, request.FILES or None, instance = quotation)
        
        if form.is_valid():
            if "confirmButton" in request.POST:
                quotation = form.save(commit = False)
                quotation.sourceCompany = sourceCompany
                quotation.project = project
                quotation.inquiry = inquiry
                quotation.soc = soc
                quotation.identificationCode = identificationCode
                quotation.code = code
                quotation.yearCode = yearCode
                quotation.quotationNo = quotationNo
                quotation.person = person
                quotation.validity = validity
                quotation.currency = currency
                quotation.payment = payment
                quotation.delivery = delivery
                quotation.remark = remark
                quotation.quotationDate = quotationDate
                quotation.approval = "approved"
                quotation.save()
                
                return HttpResponse(status=204)
            
            elif "notConfirmButton" in request.POST:
                quotation = form.save(commit = False)
                quotation.sourceCompany = sourceCompany
                quotation.project = project
                quotation.inquiry = inquiry
                quotation.soc = soc
                quotation.identificationCode = identificationCode
                quotation.code = code
                quotation.yearCode = yearCode
                quotation.quotationNo = quotationNo
                quotation.person = person
                quotation.validity = validity
                quotation.currency = currency
                quotation.payment = payment
                quotation.delivery = delivery
                quotation.remark = remark
                quotation.quotationDate = quotationDate
                quotation.approval = "notApproved"
                quotation.save()
                
                return HttpResponse(status=204)
            
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'sale/manager_approval/manager_approval_detail.html', context)

class ManagerApprovalUpdateInTableConfirmView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        quotation = get_object_or_404(Quotation, id = id)
        project = quotation.project
        inquiry = quotation.inquiry
        soc = quotation.soc
        identificationCode = quotation.identificationCode
        code = quotation.code
        yearCode = quotation.yearCode
        quotationNo = quotation.quotationNo
        person = quotation.person
        validity = quotation.validity
        currency = quotation.currency
        payment = quotation.payment
        delivery = quotation.delivery
        remark = quotation.remark
        parts = quotation.parts
        approval = quotation.approval
        quotationDate = quotation.quotationDate
        sourceCompany = quotation.sourceCompany
        
        form = QuotationForm(request.POST, request.FILES or None, instance = quotation)
        
        if form.is_valid():
            quotation = form.save(commit = False)
            quotation.sourceCompany = sourceCompany
            quotation.project = project
            quotation.inquiry = inquiry
            quotation.soc = soc
            quotation.identificationCode = identificationCode
            quotation.code = code
            quotation.yearCode = yearCode
            quotation.quotationNo = quotationNo
            quotation.person = person
            quotation.validity = validity
            quotation.currency = currency
            quotation.payment = payment
            quotation.delivery = delivery
            quotation.remark = remark
            quotation.quotationDate = quotationDate
            quotation.approval = "approved"
            quotation.save()
            
            return HttpResponse(status=204)
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'sale/manager_approval/manager_approval_detail.html', context)
 
class ManagerApprovalUpdateInTableNotConfirmView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        quotation = get_object_or_404(Quotation, id = id)
        project = quotation.project
        inquiry = quotation.inquiry
        soc = quotation.soc
        identificationCode = quotation.identificationCode
        code = quotation.code
        yearCode = quotation.yearCode
        quotationNo = quotation.quotationNo
        person = quotation.person
        validity = quotation.validity
        currency = quotation.currency
        payment = quotation.payment
        delivery = quotation.delivery
        remark = quotation.remark
        parts = quotation.parts
        approval = quotation.approval
        quotationDate = quotation.quotationDate
        sourceCompany = quotation.sourceCompany
        
        form = QuotationForm(request.POST, request.FILES or None, instance = quotation)
        
        if form.is_valid():
            quotation = form.save(commit = False)
            quotation.sourceCompany = sourceCompany
            quotation.project = project
            quotation.inquiry = inquiry
            quotation.soc = soc
            quotation.identificationCode = identificationCode
            quotation.code = code
            quotation.yearCode = yearCode
            quotation.quotationNo = quotationNo
            quotation.person = person
            quotation.validity = validity
            quotation.currency = currency
            quotation.payment = payment
            quotation.delivery = delivery
            quotation.remark = remark
            quotation.quotationDate = quotationDate
            quotation.approval = "notApproved"
            quotation.save()
            
            return HttpResponse(status=204)
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'sale/manager_approval/manager_approval_detail.html', context)
        