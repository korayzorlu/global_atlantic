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


class OfferDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Offers")
        elementTag = "offer"
        elementTagSub = "offerPart"

        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'service/offer/offers.html', context)
    
class OfferAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Offer")
        elementTag = "offer"
        elementTagSub = "offerPart"
        
        form = OfferForm(request.POST or None, request.FILES or None, user = request.user)
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
        
        return render(request, 'service/offer/offer_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = OfferForm(request.POST, request.FILES or None, user = request.user)
        
        if form.is_valid():
            offer = form.save(commit = False)
            offer.sourceCompany = request.user.profile.sourceCompany
            print(request.POST)
            identificationCode = request.user.profile.sourceCompany.serviceOfferCode
            yearCode = int(str(datetime.today().date().year)[-2:])
            startCodeValue = 1
            
            lastRequest = Offer.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
            
            if lastRequest:
                lastCode = lastRequest.code
            else:
                lastCode = startCodeValue - 1
            
            code = int(lastCode) + 1
            offer.code = code
            
            offer.yearCode = yearCode
            
            offerNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
            offer.offerNo = offerNo
            
            offer.user = request.user
            offer.save()

            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)
        
class OfferUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Offer Detail")
        elementTag = "offer"
        elementTagSub = "offerPart"
        elementTagId = id
        
        offers = Offer.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        offer = get_object_or_404(Offer, id = id)
        
        serviceCards = OfferServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = offer)
        
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
        
        if offer.discountAmount > 0:
            partsTotals["totalDiscount"] = offer.discountAmount
        else:
            partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (offer.discount/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
        
        #parts = RequestPart.objects.filter(theRequest = requestt)
        
        #addParts = Part.objects.filter(maker = requestt.maker, type = requestt.makerType)
        #partsLength = len(addParts)
        
        form = OfferForm(request.POST or None, request.FILES or None, instance = offer, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "offers" : offers,
                "offer" : offer,
                "partsTotals" : partsTotals,
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
        
        return render(request, 'service/offer/offer_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        offer = get_object_or_404(Offer, id = id)
        identificationCode = offer.identificationCode
        code = offer.code
        yearCode = offer.yearCode
        offerNo = offer.offerNo
        sourceCompany = offer.sourceCompany
        form = OfferForm(request.POST, request.FILES or None, instance = offer, user = request.user)
        if form.is_valid():
            offer = form.save(commit = False)
            offer.sourceCompany = sourceCompany
            offer.identificationCode = identificationCode
            offer.code = code
            offer.yearCode = yearCode
            offer.offerNo = offerNo
            if offer.confirmed == True:
                offer.status = "active"
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
                    offer = offer,
                    type = "service"
                )
                
                processStatus.save()
                #process status oluştur-end
                
            serviceCards = OfferServiceCard.objects.filter(offer = offer)
        
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
            
            if offer.discountAmount > 0:
                partsTotals["totalDiscount"] = offer.discountAmount
            else:
                partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (offer.discount/100)
            partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
            
            offer.totalDiscountPrice = round(partsTotals["totalDiscount"],2)
            offer.totalTotalPrice = round(partsTotals["totalFinal"],2)
            
            offer.save()
            
            # sessionRequestParts = RequestPart.objects.filter(sessionKey = request.session.session_key, user = request.user, theRequest = None)
            # for sessionRequestPart in sessionRequestParts:
            #     sessionRequestPart.theRequest = requestt
            #     sessionRequestPart.save()
            
            offerPdf(offer,request.user.profile.sourceCompany)
                
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)
class OfferDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Offer")
        elementTag = "offer"
        elementTagSub = "offerPart"
        
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
        
        return render(request, 'service/offer/offer_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:   
            offer = get_object_or_404(Offer, id = int(id))
            #process status sil
            processStatus = offer.process_status_offer.first()
            if processStatus:
                processStatus.delete()
            #process status sil-end
            offer.delete()
        return HttpResponse(status=204)
    
class OfferServiceCardInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Offer Service Card")
        elementTag = "offer"
        elementTagSub = "offerPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        offerId = refererPath.replace("/service/offer_update/","").replace("/","")
        offer = get_object_or_404(Offer, id = id)
        
        form = OfferServiceCardForm(request.POST or None, request.FILES or None, user = request.user)
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
        offerId = refererPath.replace("/service/offer_update/","").replace("/","")
        
        offer = Offer.objects.get(id = id)
        offerServiceCards = OfferServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany,offer = offer)
        
        serviceCards = []
        
        # for offerServiceCard in offerServiceCards:
        #     serviceCards.append(offerServiceCard.serviceCard)
        
        form = OfferServiceCardForm(request.POST, request.FILES or None, user = request.user)
        if form.is_valid():
            offerServiceCard = form.save(commit = False)
            offerServiceCard.sourceCompany = request.user.profile.sourceCompany
            
            # if offerServiceCard.serviceCard in serviceCards:
            #     return HttpResponse(status=500)
            # else:
            offerServiceCard.user = request.user
            offerServiceCard.offer = get_object_or_404(Offer, id = id)
            offerServiceCard.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form,
                    "offerId" : offerId
            }
            return render(request, 'service/offer/offer_service_card_add_in_detail.html', context)
        
class OfferServiceCardDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Offer Service Card")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/request/request_part_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            offerServiceCard = get_object_or_404(OfferServiceCard, id = int(id))
            offerServiceCard.delete()
        return HttpResponse(status=204)

class OfferPdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Offer PDF")
        
        elementTag = "offer"
        elementTagSub = "offerPart"
        elementTagId = str(id) + "-pdf"
        
        offer = Offer.objects.get(id = id)
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #inquiryPdf(inquiry)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "offer" : offer,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'service/offer/offer_pdf.html', context)
