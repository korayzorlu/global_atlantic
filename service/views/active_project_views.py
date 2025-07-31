from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage, send_mail
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa
from django.template.loader import get_template 

from ..forms import *
from ..pdfs.offer_pdfs import *
from ..pdfs.active_project_pdfs import *
from ..pdfs.finish_project_pdfs import *

from source.models import Company as SourceCompany
from account.models import ProcessStatus

import pandas as pd
import json
import random
import string
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
    

def sendProcess(request,message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'private_' + str(request.user.id),
        {
            "type": "send_process",
            "message": message,
            "location" : location
        }
    )

class ActiveProjectDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Active Projects")
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"

        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/active_project/active_projects.html', context)
    
class ActiveProjectUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Active Project Detail")
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"
        elementTagId = id
        
        activeProjects = Offer.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        activeProject = get_object_or_404(Offer, id = id)
        
        images = OfferImage.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        
        #parts = RequestPart.objects.filter(theRequest = requestt)
        
        #addParts = Part.objects.filter(maker = requestt.maker, type = requestt.makerType)
        #partsLength = len(addParts)
        
        serviceCards = OfferServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        expenses = OfferExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        parts = OfferPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        notes = OfferNote.objects.select_related("user").filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
        partsTotal = 0
        
        for serviceCard in serviceCards:
            partsTotal  = partsTotal + serviceCard.unitPrice1
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + serviceCard.unitPrice1
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + serviceCard.unitPrice2
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + serviceCard.unitPrice3
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + serviceCard.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + serviceCard.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + serviceCard.totalPrice
            
        for expense in expenses:
            partsTotal  = partsTotal + expense.unitPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + expense.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + expense.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + expense.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + expense.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + expense.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + expense.totalPrice
            
        for part in parts:
            partsTotal  = partsTotal + part.unitPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
        
        if activeProject.discountAmount > 0:
            partsTotals["totalDiscount"] = activeProject.discountAmount
        else:
            partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (activeProject.discount/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
        
        form = OfferForm(request.POST or None, request.FILES or None, instance = activeProject, user = request.user)
        imageForm = OfferImageForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "imageForm" : imageForm,
                "activeProjects" : activeProjects,
                "activeProject" : activeProject,
                "partsTotals" : partsTotals,
                "images" : images,
                "notes" : notes,
                #"parts" : parts,
                #"addParts" : addParts,
                #"partsLength" : partsLength,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/active_project/active_project_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        activeProject = get_object_or_404(Offer, id = id)
        identificationCode = activeProject.identificationCode
        code = activeProject.code
        yearCode = activeProject.yearCode
        offerNo = activeProject.offerNo
        status = activeProject.status
        offerNo = activeProject.offerNo
        customer = activeProject.customer
        vessel = activeProject.vessel
        person = activeProject.person
        equipment = activeProject.equipment
        customerRef = activeProject.customerRef
        machineType = activeProject.machineType
        offerDate = activeProject.offerDate
        paymentType = activeProject.paymentType
        deliveryMethod = activeProject.deliveryMethod
        period = activeProject.period
        currency = activeProject.currency
        discount = activeProject.discount
        confirmed = activeProject.confirmed
        sourceCompany = activeProject.sourceCompany
        
        form = OfferForm(request.POST, request.FILES or None, instance = activeProject, user = request.user)
        if form.is_valid():
            activeProject = form.save(commit = False)
            activeProject.sourceCompany = sourceCompany
            activeProject.identificationCode = identificationCode
            activeProject.code = code
            activeProject.yearCode = yearCode
            activeProject.offerNo = offerNo
            activeProject.status = status
            activeProject.offerDate = offerDate
            activeProject.confirmed = confirmed
            
            if activeProject.finished == True:
                activeProject.status = "finished"
                
                finishProjectPdf(activeProject,request.user.profile.sourceCompany)
                finishProjectPdfWithoutPrice(activeProject,request.user.profile.sourceCompany)
                
            serviceCards = OfferServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
            expenses = OfferExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
            parts = OfferPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
            
            partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
            
            partsTotal = 0
            
            for serviceCard in serviceCards:
                partsTotal  = partsTotal + serviceCard.unitPrice1
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + serviceCard.unitPrice1
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + serviceCard.unitPrice2
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + serviceCard.unitPrice3
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + serviceCard.totalPrice
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + serviceCard.totalPrice
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + serviceCard.totalPrice
                
            for expense in expenses:
                partsTotal  = partsTotal + expense.unitPrice
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + expense.unitPrice
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + expense.unitPrice
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + expense.unitPrice
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + expense.totalPrice
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + expense.totalPrice
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + expense.totalPrice
                
            for part in parts:
                partsTotal  = partsTotal + part.unitPrice
                partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice
                partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice
                partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice
                partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice
                partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice
                partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice
            
            if activeProject.discountAmount > 0:
                partsTotals["totalDiscount"] = activeProject.discountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (activeProject.discount/100)
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
            
            activeProject.totalDiscountPrice = round(partsTotals["totalDiscount"],2)
            activeProject.totalTotalPrice = round(partsTotals["totalFinal"],2)
            activeProject.save()

            activeProjectPdf(activeProject, request.user.profile.sourceCompany)
            activeProjectPdfWithoutPrice(activeProject, request.user.profile.sourceCompany)
            
            # sessionRequestParts = RequestPart.objects.filter(sessionKey = request.session.session_key, user = request.user, theRequest = None)
            # for sessionRequestPart in sessionRequestParts:
            #     sessionRequestPart.theRequest = requestt
            #     sessionRequestPart.save()
                
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)

class ActiveProjectAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Active project")
        
        acceptance = Acceptance.objects.select_related().get(id = id)
        
        elementTag = "activeProjectAdd"
        elementTagSub = "activeProjectPartInAdd"
        elementTagId = id
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "acceptance" : acceptance
        }
        return render(request, 'service/active_project/active_project_add_from_acceptance.html', context)
    def post(self, request, id, *args, **kwargs):
        acceptance = Acceptance.objects.get(id = id)
        acceptance.status = "active"
        acceptance.save()
        
        identificationCode = request.user.profile.sourceCompany.serviceOfferCode
        yearCode = int(str(datetime.today().date().year)[-2:])
        startCodeValue = 1
        
        lastActiveProject = Offer.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode, confirmed = True).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
        
        if lastActiveProject:
            lastCode = lastActiveProject.code
        else:
            lastCode = startCodeValue - 1
        
        code = int(lastCode) + 1
        
        activeProjectNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        
        if acceptance.customer:
            customer = acceptance.customer
        else:
            customer = ""
            
        if acceptance.vessel:
            vessel = acceptance.vessel
        else:
            vessel = ""
            
        if acceptance.equipment:
            equipment = acceptance.equipment
        else:
            equipment = ""
        
        activeProject = Offer.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            identificationCode = identificationCode,
            yearCode = yearCode,
            code = code,
            offerNo = activeProjectNo,
            sessionKey = request.session.session_key,
            user = request.user,
            customer = customer,
            vessel = vessel,
            equipment = equipment,
            confirmed = True,
            status = "active"
        )
        
        activeProject.save()
        
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
            offer = activeProject,
            type = "service"
        )
        
        processStatus.save()
        #process status oluştur-end
        
        return HttpResponse(status=204)
  

class ActiveProjectDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Active Project")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/active_project/active_project_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            activeProject = get_object_or_404(Offer, id = int(id))
            #process status sil
            processStatus = activeProject.process_status_offer.first()
            processStatus.delete()
            #process status sil-end
            activeProject.delete()
        return HttpResponse(status=204)

class ActiveProjectServiceCardInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Offer Service Card")
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        offerId = refererPath.replace("/service/offer_update/","").replace("/","")
        offer = get_object_or_404(Offer, id = id)
        
        form = OfferServiceCardForm(request.POST or None, request.FILES or None,user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "offer" : offer,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/offer/offer_service_card_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        offerId = refererPath.replace("/service/active_project_update/","").replace("/","")
        
        offer = Offer.objects.get(id = id)
        offerServiceCards = OfferServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = offer)
        
        # serviceCards = []
        
        # for offerServiceCard in offerServiceCards:
        #     serviceCards.append(offerServiceCard.serviceCard)
        
        form = OfferServiceCardForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            offerServiceCard = form.save(commit = False)
            
            # if offerServiceCard.serviceCard in serviceCards:
            #     return HttpResponse(status=500)
            # else:
            offerServiceCard.sourceCompany = request.user.profile.sourceCompany
            offerServiceCard.user = request.user
            offerServiceCard.offer = get_object_or_404(Offer, id = id)
            offerServiceCard.save()
                
            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=204)
              
class ActiveProjectServiceCardExtraInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Active Project Service Card")
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        activeProjectId = refererPath.replace("/service/active_project_update/","").replace("/","")
        activeProject = get_object_or_404(Offer, id = id)
        
        form = OfferServiceCardForm(request.POST or None, request.FILES or None,user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "activeProject" : activeProject,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/offer/offer_service_card_extra_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        activeProjectId = refererPath.replace("/service/offer_update/","").replace("/","")
        
        activeProject = Offer.objects.get(id = id)
        activeProjectServiceCards = OfferServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        
        serviceCards = []
        
        for activeProjectServiceCard in activeProjectServiceCards:
            serviceCards.append(activeProjectServiceCard.serviceCard)
        
        form = OfferServiceCardForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            activeProjectServiceCard = form.save(commit = False)
            activeProjectServiceCard.sourceCompany = request.user.profile.sourceCompany
            activeProjectServiceCard.user = request.user
            activeProjectServiceCard.offer = get_object_or_404(Offer, id = id)
            activeProjectServiceCard.unit = "pc"
            activeProjectServiceCard.extra = True
            activeProjectServiceCard.save()
            
            return HttpResponse(status=204)
            
            # if activeProjectServiceCard.serviceCard in serviceCards:
            #     return HttpResponse(status=500)
            # else:
            #     activeProjectServiceCard.user = request.user
            #     activeProjectServiceCard.offer = get_object_or_404(Offer, id = id)
            #     activeProjectServiceCard.unit = "pc"
            #     activeProjectServiceCard.extra = True
            #     activeProjectServiceCard.save()
                
            #     return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)

    
class ActiveProjectExpenseInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Active Project Expense")
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        activeProjectId = refererPath.replace("/service/active_project_update/","").replace("/","")
        activeProject = get_object_or_404(Offer, id = id)
        
        form = OfferExpenseForm(request.POST or None, request.FILES or None, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId"  :elementTagId,
                "activeProject" : activeProject,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/offer/offer_expense_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        activeProjectId = refererPath.replace("/service/offer_update/","").replace("/","")
        
        activeProject = Offer.objects.get(id = id)
        activeProjectExpenses = OfferExpense.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        
        expenses = []
        
        for activeProjectExpense in activeProjectExpenses:
            expenses.append(activeProjectExpense.expense)
        
        form = OfferExpenseForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            activeProjectExpense = form.save(commit = False)
            activeProjectExpense.sourceCompany = request.user.profile.sourceCompany
            
            if activeProjectExpense.expense in expenses:
                return HttpResponse(status=500)
            else:
                activeProjectExpense.user = request.user
                activeProjectExpense.offer = get_object_or_404(Offer, id = id)
                activeProjectExpense.unit = "pc"
                activeProjectExpense.extra = True
                activeProjectExpense.save()
                
                activeProjectPdf(activeProject, request.user.profile.sourceCompany)
                activeProjectPdfWithoutPrice(activeProject, request.user.profile.sourceCompany)
                
                return HttpResponse(status=204)
            
        else:
            context = {
                    "form" : form,
                    "activeProjectId" : activeProjectId
            }
            return render(request, 'service/offer/offer_expense_add_in_detail.html', context)

class ActiveProjectExpenseDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Active Project Expense")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/active_project/active_project_expense_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            expense = get_object_or_404(OfferExpense, id = int(id))
            
            activeProject = expense.offer
            
            expense.delete()
            
            activeProjectPdf(activeProject, request.user.profile.sourceCompany)
            activeProjectPdfWithoutPrice(activeProject, request.user.profile.sourceCompany)
        return HttpResponse(status=204)

class ActiveProjectPartInDetail2AddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Active Project Part")
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        activeProjectId = refererPath.replace("/service/active_project_update/","").replace("/","")
        activeProject = get_object_or_404(Offer, id = id)
        
        form = OfferPartForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "activeProject" : activeProject,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/offer/offer_part_add_in_detail_ex.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        activeProjectId = refererPath.replace("/service/offer_update/","").replace("/","")
        
        activeProject = Offer.objects.get(id = id)
        activeProjectParts = OfferPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        
        parts = []
        
        for activeProjectPart in activeProjectParts:
            parts.append(activeProjectPart.part)
        
        form = OfferPartForm(request.POST, request.FILES or None)
        if form.is_valid():
            activeProjectPart = form.save(commit = False)
            
            if activeProjectPart.part in parts:
                return HttpResponse(status=500)
            else:
                activeProjectPart.sourceCompany = request.user.profile.sourceCompany
                activeProjectPart.user = request.user
                activeProjectPart.offer = get_object_or_404(Offer, id = id)
                activeProjectPart.unit = "pc"
                activeProjectPart.extra = True
                activeProjectPart.save()
                
                activeProjectPdf(activeProject, request.user.profile.sourceCompany)
                activeProjectPdfWithoutPrice(activeProject, request.user.profile.sourceCompany)
                
                return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)

class ActiveProjectPartInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Request Part")
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        requestId = refererPath.replace("/sale/request_update/","").replace("/","")
        activeProject = get_object_or_404(Offer, id = id)
        form = OfferPartForm(request.POST or None, request.FILES or None)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "activeProject" : activeProject,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/offer/offer_part_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        # refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        # requestId = refererPath.replace("/sale/request_update/","").replace("/","")
        
        activeProject = Offer.objects.get(id = id)
        activeProjectParts = OfferPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        sequencyCount = len(activeProjectParts)
        parts = []
        
        for activeProjectPart in activeProjectParts:
            parts.append(activeProjectPart.part)
            
        activeProjectAppendingParts = request.POST.getlist("activeProjectParts")
        
        for item in activeProjectAppendingParts:
            part = Part.objects.get(id = int(item))
            newActiveProjectPart = OfferPart.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    user = request.user,
                    offer = activeProject,
                    part = part,
                    quantity = 1
                )
            newActiveProjectPart.save()
            
        activeProjectPdf(activeProject, request.user.profile.sourceCompany)
        activeProjectPdfWithoutPrice(activeProject, request.user.profile.sourceCompany)
        
        return HttpResponse(status=204)

class ActiveProjectPartDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Active Project Part")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/active_project/active_project_part_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            activeProjectPart = get_object_or_404(OfferPart, id = int(id))
            
            activeProject = activeProjectPart.offer
            
            activeProjectPart.delete()
            
            activeProjectPdf(activeProject, request.user.profile.sourceCompany)
            activeProjectPdfWithoutPrice(activeProject, request.user.profile.sourceCompany)
        return HttpResponse(status=204)

class ActiveProjectImageView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"
        elementTagId = id
        
        activeProjects = Offer.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        activeProject = get_object_or_404(Offer, id = id)
        
        images = OfferImage.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        
        imageForm = OfferImageForm(request.POST or None, request.FILES or None)
        context = {
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "imageForm" : imageForm,
                "activeProjects" : activeProjects,
                "activeProject" : activeProject,
                "images" : images,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/active_project/active_project_image.html', context)       
class ActiveProjectImageAddView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        activeProject = get_object_or_404(Offer, id = id)
        
        image = OfferImage.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            offer = activeProject,
            image = request.FILES.get("image")
        )
        
        image.save()
            
        return HttpResponse(status=204)
    
class ActiveProjectImageDeleteView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        
        image = OfferImage.objects.get(id = id)
        image.delete()
            
        return HttpResponse(status=204)

class ActiveProjectDocumentView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"
        elementTagId = id
        
        activeProjects = Offer.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        activeProject = Offer.objects.filter(id = id).first()
        
        activeProjectDocuments = OfferDocument.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)

        documents = OfferDocument.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = activeProject)
        
        activeProjectDocumentForm = OfferDocumentForm(request.POST or None, request.FILES or None)
        context = {
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "activeProjectDocumentForm" : activeProjectDocumentForm,
                "activeProjects" : activeProjects,
                "activeProject" : activeProject,
                "activeProjectDocuments" : activeProjectDocuments,
                "documents" : documents,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/active_project/active_project_document.html', context)

class ActiveProjectDocumentAddView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        activeProject = Offer.objects.filter(id=id).first()
        pageLoad(request,20,100,"false")
        activeProjectDocument = OfferDocument.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            sessionKey = request.session.session_key,
            offer = activeProject,
            file = request.FILES.get("file")
        )
        pageLoad(request,90,100,"false")
        activeProjectDocument.save()
        pageLoad(request,100,100,"true")
        return HttpResponse(status=204)

class ActiveProjectDocumentDeleteView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        
        activeProjectDocument = OfferDocument.objects.get(id = id)
        activeProjectDocument.delete()
            
        return HttpResponse(status=204)
    
class ActiveProjectDocumentPdfView(LoginRequiredMixin, View):
    def get(self, request, id, name, *args, **kwargs):
        tag = _("Active Project Document PDF")
        
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"
        elementTagId = str(id) + "-pdf"
        
        pageLoad(request,0,100,"false")
        
        activeProjectDocument = OfferDocument.objects.get(id = id, name = name)
        activeProject = activeProjectDocument.offer
        pageLoad(request,50,100,"false")
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "activeProjectDocument" : activeProjectDocument,
                "activeProject" : activeProject,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'service/active_project/active_project_document_pdf.html', context)

class ActiveProjectNoteAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Note")
        
        activeProject = Offer.objects.select_related().filter(id = id).first()
        print(request.GET.get("title"))
        newNote = OfferNote.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            title = request.GET.get("title"),
            text  =request.GET.get("text"),
            user = request.user,
            offer = activeProject
        )
        
        newNote.save()
        
        if request.user.first_name:
            firstName = request.user.first_name
        else:
            firstName = ""
            
        if request.user.last_name:
            lastName = request.user.last_name
        else:
            lastName = ""
        
        note = {
            "id" : newNote.id,
            "title" : newNote.title,
            "text" : newNote.text,
            "date" : newNote.created_date.strftime("%d.%m.%Y"),
            "user" : firstName + " " + lastName,
            "offerId" : activeProject.id
        }
        
        sendProcess(request,note,"offer_note_add")
        
        context = {
                "tag": tag
        }
        return HttpResponse(status=204)

class ActiveProjectNoteDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Delete Note")
        
        exNote = OfferNote.objects.select_related().filter(id = int(request.GET.get("note"))).first()
        exNoteId = exNote.id
        note = {
            "id" : exNoteId
        }
        
        exNote.delete()
        
        sendProcess(request,note,"offer_note_delete")
        
        context = {
                "tag": tag
        }
        return HttpResponse(status=204)


class ActiveProjectPdfView(LoginRequiredMixin, View):
    def get(self, request, id, type, *args, **kwargs):
        tag = _("Active Project PDF")
        
        elementTag = "activeProject"
        elementTagSub = "activeProjectPart"
        elementTagId = str(id) + "-pdf"
        
        activeProject = Offer.objects.get(id = id)
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        if type == "normal":
            src = "/media/docs/" + str(request.user.profile.sourceCompany.id) + "/service/active_project/documents/" + str(activeProject.offerNo) + ".pdf?v=" + str(version)
        elif type == "wop":
            src = "/media/docs/" + str(request.user.profile.sourceCompany.id) + "/service/active_project/documents/" + str(activeProject.offerNo) + "-without-price.pdf?v=" + str(version)
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "activeProject" : activeProject,
                "version" : version,
                "src" : src
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/active_project/active_project_pdf.html', context)
    