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

class QuotationDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pageLoad(request,0,100,"false")
        
        tag = _("Quotations")
        elementTag = "quotation"
        elementTagSub = "quotationPart"
        
        quotations = Quotation.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany)
        quotationsCount = len(quotations)
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "quotationsCount" : quotationsCount
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'sale/quotation/quotations.html', context)
    
class QuotationAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Create Inquiry")
        elementTag = "quotationAdd"
        elementTagSub = "quotationPartInAdd"
        elementTagId = id
        
        parts = InquiryPart.objects.filter(inquiry = id).order_by("sequency")
        theInquiry = get_object_or_404(Inquiry, id = id)
        usd = Currency.objects.filter(id=106).first()
        
        partsTotal = 0
        
        for part in parts:
            partsTotal  = partsTotal + part.totalPrice
        
        theInquiryParts = []
        
        thePartsTotals = {}
        thePartsAvailabilities = {}
        
        for part in parts:
            theInquiryParts.append(part)
            thePartsTotals[part.requestPart.id] = []
            thePartsAvailabilities[part.requestPart.id] = []
        
        inquiries = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany,project = theInquiry.project)
        
        inquiryPartss = InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry__project = inquiries[0].project) #bunu incele
        
        inquiryParts = []
        inquiryPartsTotal = []
        
        projectParts = {}

        tjInquiries = []
        
        for inquiry in inquiries:
            theParts = InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry = inquiry).order_by("sequency")
            thePartsForQ = []
            for thePart in theParts:
                thePartsForQ.append({
                    "inquiry" : thePart.inquiry,
                    "requestPart" : thePart.requestPart.id,
                    "id" : thePart.id,
                    "sequency" : thePart.sequency,
                    "partNo" : thePart.requestPart.part.partNo,
                    "description" : thePart.requestPart.part.description,
                    "quantity" : thePart.quantity,
                    "unit" : thePart.requestPart.part.unit,
                    "unitPriceOriginal" : thePart.unitPrice,
                    "totalPriceOriginal" : thePart.totalPrice,
                    "unitPrice" : ((thePart.unitPrice * inquiry.currency.forexBuying) / usd.forexBuying),
                    "totalPrice" : ((thePart.totalPrice * inquiry.currency.forexBuying) / usd.forexBuying),
                    "availabilityType" : thePart.availabilityType,
                    "availability" : thePart.availability
                })
            
            thePartsTotal = 0
            
            tjParts = []
            for tjPart in theParts:
                tjParts.append({"part" : tjPart, "min" : False})
            tjInquiries.append({
                                "inquiry" : inquiry,
                                "parts" : tjParts
            })
            
            
            for i, thePart in enumerate(theParts):
                #print(str(i) + str(thePart.requestPart.part.partNo));
                if thePart.requestPart.id in thePartsTotals.keys():
                    thePartsTotal = thePartsTotal + ((thePart.totalPrice * inquiry.currency.forexBuying) / usd.forexBuying)
                    thePartsTotals[thePart.requestPart.id].append(((thePart.totalPrice * inquiry.currency.forexBuying) / usd.forexBuying))
                    thePartsAvailabilities[thePart.requestPart.id].append(thePart.availability)
                    if thePart.requestPart.id not in projectParts:
                        projectParts[thePart.requestPart.id] = {
                            "inquiry" : thePart.inquiry,
                            "requestPart" : thePart.requestPart.id,
                            "id" : thePart.id,
                            "sequency" : thePart.sequency,
                            "partNo" : thePart.requestPart.part.partNo,
                            "description" : thePart.requestPart.part.description,
                            "quantity" : thePart.quantity,
                            "unit" : thePart.requestPart.part.unit,
                            "unitPriceOriginal" : thePart.unitPrice,
                            "totalPriceOriginal" : thePart.totalPrice,
                            "unitPrice" : ((thePart.unitPrice * inquiry.currency.forexBuying) / usd.forexBuying),
                            "totalPrice" : ((thePart.totalPrice * inquiry.currency.forexBuying) / usd.forexBuying),
                            "availability" : thePart.availability
                        }
                else:
                    thePartsTotal = thePartsTotal + ((thePart.totalPrice * inquiry.currency.forexBuying) / usd.forexBuying)
                    thePartsTotals[thePart.requestPart.id] = [((thePart.totalPrice * inquiry.currency.forexBuying) / usd.forexBuying)]
                    thePartsAvailabilities[thePart.requestPart.id] = [thePart.availability]
                    projectParts[thePart.requestPart.id] = {
                            "inquiry" : thePart.inquiry,
                            "requestPart" : thePart.requestPart.id,
                            "id" : thePart.id,
                            "sequency" : thePart.sequency,
                            "partNo" : thePart.requestPart.part.partNo,
                            "description" : thePart.requestPart.part.description,
                            "quantity" : thePart.quantity,
                            "unit" : thePart.requestPart.part.unit,
                            "unitPriceOriginal" : thePart.unitPrice,
                            "totalPriceOriginal" : thePart.totalPrice,
                            "unitPrice" : ((thePart.unitPrice * inquiry.currency.forexBuying) / usd.forexBuying),
                            "totalPrice" : ((thePart.totalPrice * inquiry.currency.forexBuying) / usd.forexBuying),
                            "availability" : thePart.availability
                        }
            inquiryParts.append({"parts" : thePartsForQ, "total" : thePartsTotal, "min" : False})
            inquiryPartsTotal.append(thePartsTotal)
        
        part_groups = {}
        
        for item in tjInquiries:
            for part_data in item["parts"]:
                part_item = part_data["part"]
                
                part_name = str(part_item.requestPart.part.partNo)
                
                part_price = float((part_item.unitPrice * part_item.inquiry.currency.forexBuying) / usd.forexBuying)
                
                if part_name not in part_groups:
                    part_groups[part_name] = {"min_price": part_price, "min_item": part_data}
                else:
                    if part_price < part_groups[part_name]["min_price"]:
                        part_groups[part_name]["min_price"] = part_price
                        part_groups[part_name]["min_item"] = part_data

        # Minimum fiyatlı parçaların "min" alanını True yapalım
        for item in tjInquiries:
            for part_data in item["parts"]:
                part_item = part_data["part"]
                part_name = str(part_item.requestPart.part.partNo)
                if part_data == part_groups[part_name]["min_item"]:
                    part_data["min"] = True

        # Sonuçları gösterelim
        print(tjInquiries)
        
        for inquiryPart in inquiryParts:
            if inquiryPart["total"] == min(inquiryPartsTotal):
                inquiryPart["min"] = True

        for thePartsTotal in thePartsTotals:
            thePartsTotals[thePartsTotal] = min(thePartsTotals[thePartsTotal])
            
        for thePartsAvailability in thePartsAvailabilities:
            thePartsAvailabilities[thePartsAvailability] = min(thePartsAvailabilities[thePartsAvailability])

        form = QuotationForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "parts" : parts,
                "projectParts" : projectParts,
                "theInquiry" : theInquiry,
                "inquiries" : inquiries,
                "partsTotal" : partsTotal,
                "thePartsTotals" : thePartsTotals,
                "thePartsAvailabilities" : thePartsAvailabilities,
                "theInquiryParts" : theInquiryParts,
                "inquiryParts" : inquiryParts,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "parts" : parts,
                "form" : form,
                "tjInquiries" : tjInquiries,
                "usd" : usd
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/quotation/quotation_add.html', context)
    def post(self, request, id, *args, **kwargs):
        form = QuotationForm(request.POST, request.FILES or None)
        
        identificationCode = request.user.profile.sourceCompany.saleQuotationCode
        yearCode = int(str(datetime.today().date().year)[-2:])
        startCodeValue = 1
        
        lastRequest = Quotation.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
        
        if lastRequest:
            lastCode = lastRequest.code
        else:
            lastCode = startCodeValue - 1
        
        code = int(lastCode) + 1
        
        quotationNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
        
        inquiry = get_object_or_404(Inquiry, id = id)
        
        inquiries = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany,project = inquiry.project)
        
        partKeys = {}
        
        inquiryParts = InquiryPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,inquiry__project = inquiries[0].project)
        
        for inquiryPart in inquiryParts:
            partKeys[inquiryPart.id] = inquiryPart.requestPart.id
            
        parts = []
        parts2 = []
        
        for key, value in partKeys.items():
            try:
                if len(request.POST.getlist("name-" + str(key) + "-" + str(value) + "-alternative")) > 0:
                    parts.append({"iPart" : key,
                                "rPart" : request.POST.getlist("name-" + str(key) + "-" + str(value))[0],
                                "alternative" : True})
                else:
                    parts.append({"iPart" : key,
                                "rPart" : request.POST.getlist("name-" + str(key) + "-" + str(value))[0],
                                "alternative" : False})
                parts2.append(key)
            except:
                pass
        
        if not parts and not parts2:
            data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"At least one part must be selected!"
                }
            
            sendAlert(data,"default")
            return HttpResponse(status=200)
        
        currency = Currency.objects.get(id = int(request.POST.get("quotationCurrencyForm")))
        requestPart = RequestPart.objects.filter(id = int(parts[0]["rPart"])).first()
        theInquiryPart = InquiryPart.objects.filter(requestPart = requestPart, id = parts2[0]).first()
        quotation = Quotation.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            code = code,
            yearCode = yearCode,
            quotationNo = quotationNo,
            project = get_object_or_404(Project, id = inquiry.project.id),
            inquiry = theInquiryPart.inquiry,
            currency = currency,
            sessionKey = request.session.session_key,
            user = request.user
        )
        
        quotation.save()
        
        project = quotation.project
        project.stage = "quotation"
        project.save()
        
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
        
        quotationTotal = 0
        
        inquiryList = []
        
        for part in parts:
            requestPart = RequestPart.objects.filter(id = int(part["rPart"])).first()
            inquiryPart = InquiryPart.objects.filter(requestPart = requestPart, id = int(part["iPart"])).first()
            if part["alternative"]:
                alternative = True
            else:
                alternative = False
            
            #inquiryPart = get_object_or_404(InquiryPart, id = int(part))
            inquiryList.append(inquiryPart.inquiry)
            unitPrice1 = (inquiryPart.unitPrice * inquiryPart.inquiry.currency.forexBuying) / currency.forexBuying
            totalPrice1 = float(unitPrice1) * float(inquiryPart.quantity)
            print(inquiryPart.inquiry.currency.forexBuying)
            
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + unitPrice1
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + unitPrice1
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + unitPrice1
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + totalPrice1
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + totalPrice1
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + totalPrice1
            print(partsTotals)
            quotationPart = QuotationPart.objects.create(
                sourceCompany = request.user.profile.sourceCompany,
                user = request.user,
                sessionKey = request.session.session_key,
                quotation = quotation,
                maker = inquiryPart.maker,
                makerType = inquiryPart.makerType,
                inquiryPart = inquiryPart,
                quantity = inquiryPart.quantity,
                unitPrice1 = unitPrice1,
                totalPrice1 = totalPrice1,
                unitPrice2 = unitPrice1,
                totalPrice2 = totalPrice1,
                unitPrice3 = unitPrice1,
                totalPrice3 = totalPrice1,
                availability = inquiryPart.availability,
                availabilityChar = str(inquiryPart.availability),
                alternative = alternative,
                sequency = inquiryPart.sequency
            )
            
            quotationPart.save()
                
            
            quotationTotal = quotationTotal + quotationPart.totalPrice1
        partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (quotation.manuelDiscount/100)
        
        quotationParts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation, alternative = False).order_by("inquiryPart__sequency")
        sequencyCount = 0
        for quotationPart in quotationParts:
            quotationPart.sequency = sequencyCount + 1
            quotationPart.save()
            sequencyCount = sequencyCount + 1
            
        quotationPartAlternatives = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation, alternative = True).order_by("inquiryPart__sequency")
        for quotationPartAlternative in quotationPartAlternatives:
            quotationPart = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation, alternative = False, inquiryPart__requestPart_id = quotationPartAlternative.inquiryPart.requestPart_id).order_by("inquiryPart__sequency").first()
            if quotationPart:
                quotationPartAlternative.sequency = quotationPart.sequency
                quotationPartAlternative.save()
            
        for inquiry in inquiryList:
            quotation.inquiries.add(inquiry)
            
        partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + partsTotals["totalExpense"]
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
        
        quotation.totalDiscountPrice = round(partsTotals["totalDiscount"],2)
        quotation.totalBuyingPrice = round(partsTotals["totalTotalPrice1"],2)
        quotation.totalSellingPrice = round(partsTotals["totalFinal"],2)
        quotation.save()
        
        currencyUSD = Currency.objects.get(code = "USD")
        
        if request.user.profile.positionType.name == "Sales Assistant":
            quotation.approvalClass = "specialist"
            quotation.save()
            # if currency.code == "JPY":
            #     quotationTotalUSD = (quotationTotal * (currency.forexBuying / 100)) / currencyUSD.forexBuying
            # else:
            #     quotationTotalUSD = (quotationTotal * currency.forexBuying) / currencyUSD.forexBuying
            quotationTotalUSD = (quotationTotal * currency.forexBuying) / currencyUSD.forexBuying
            if quotationTotalUSD < 5000:
                quotation.approval = "approved"
                quotation.save()
                
        if request.user.profile.positionType.name == "Sales Specialist":
            quotation.approvalClass = "executivor"
            quotation.save()
            quotationTotalUSD = (quotationTotal * currency.forexBuying) / currencyUSD.forexBuying
            if quotationTotalUSD < 10000:
                quotation.approval = "approved"
                quotation.save()
                
        if request.user.profile.positionType.name == "Sales Executive":
            quotation.approvalClass = "director"
            quotation.save()
            quotationTotalUSD = (quotationTotal * currency.forexBuying) / currencyUSD.forexBuying
            if quotationTotalUSD < 25000:
                quotation.approval = "approved"
                quotation.save()
                
        if request.user.profile.positionType.name == "Sales Director":
            quotation.approvalClass = "generalManager"
            quotation.save()
            quotationTotalUSD = (quotationTotal * currency.forexBuying) / currencyUSD.forexBuying
            if quotationTotalUSD < 50000:
                quotation.approval = "approved"
                quotation.save()
                
        if request.user.profile.positionType.name == "Managing Director":
            quotation.approvalClass = "generalManager"
            quotation.save()
            quotation.approval = "approved"
            quotation.save()
        
        #sourceCompany = SourceCompany.objects.get(id = request.user.profile.sourceCompany.id)
        
        quotationPdfInTask.delay(quotation.id,request.user.profile.sourceCompany.id)
        #quotationPdff(quotation)
            
        return HttpResponse(status=204)

class QuotationUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Quotation Detail")
        elementTag = "quotation"
        elementTagSub = "quotationPart"
        elementTagId = id
        
        pageLoad(request,0,100,"false")
        quotation = Quotation.objects.select_related("project").filter(id = id).first()
        
        if hasattr(quotation, "order_confirmation_quotation"):
            orderConfirmation = 1
        else:
            orderConfirmation = 0
            
        #parts = QuotationPart.objects.select_related("inquiryPart","inquiryPart__requestPart__part").filter(quotation = quotation).order_by("sequency")
        parts = quotation.quotationpart_set.select_related("inquiryPart","inquiryPart__requestPart__part").all()
        extras = quotation.quotationextra_set.select_related().all()
        pageLoad(request,20,100,"false")
        quotationPartList = []
        
        quotationInquiryParts = []
        
        thePartsTotals = {}
        thePartsAvailabilities = {}
        
        partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
        partsTotal = 0
        
        for index, part in enumerate(parts):
            percent = (60/len(parts)) * (index + 1)
            pageLoad(request,20+percent,100,"false")
            quotationPartList.append(part.id)
            
            quotationInquiryParts.append(part.inquiryPart)
            thePartsTotals[part.inquiryPart.requestPart.part.partNo] = []
            thePartsAvailabilities[part.inquiryPart.requestPart.part.partNo] = []
            
            partsTotal  = partsTotal + part.totalPrice3
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice1
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice2
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice3
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice1
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice2
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice3
            
        for index, extra in enumerate(extras):
            partsTotal  = partsTotal + extra.totalPrice
            partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + extra.unitPrice
            partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + extra.unitPrice
            partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + extra.unitPrice
            partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + extra.totalPrice
            partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + extra.totalPrice
            partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + extra.totalPrice
        
        if quotation.manuelDiscountAmount > 0:
            partsTotals["totalDiscount"] = quotation.manuelDiscountAmount
        else:
            partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (quotation.manuelDiscount/100)
        partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
        print(partsTotals["totalFinal"])
        print(partsTotals["totalTotalPrice1"])
        if partsTotals["totalFinal"] == 0 or partsTotals["totalFinal"] < 0 and partsTotals["totalTotalPrice1"] == 0:
            totalProfitPrice = 0
        else:
            totalProfitPrice = round(((partsTotals["totalFinal"] / partsTotals["totalTotalPrice1"]) - 1) * 100,2)
        
        # Para miktarını belirtilen formatta gösterme
        totalBuyingPriceFixed = "{:,.2f}".format(round(partsTotals["totalTotalPrice1"],2))
        totalGrossPriceFixed = "{:,.2f}".format(round(partsTotals["totalTotalPrice3"],2))
        totalDiscountPriceFixed = "{:,.2f}".format(round(partsTotals["totalDiscount"],2))
        totalSellingPriceFixed = "{:,.2f}".format(round(partsTotals["totalFinal"],2))
        totalProfitAmountPriceFixed = "{:,.2f}".format(round(partsTotals["totalFinal"] - partsTotals["totalTotalPrice1"],2))
        # Nokta ile virgülü değiştirme
        totalBuyingPriceFixed = totalBuyingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalGrossPriceFixed = totalGrossPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalDiscountPriceFixed = totalDiscountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalSellingPriceFixed = totalSellingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        totalProfitAmountPriceFixed = totalProfitAmountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #inquiries = Inquiry.objects.select_related().filter(project = quotation.project)
        inquiries = quotation.project.inquiry.select_related().all()
        
        inquiryParts = []
        inquiryPartsTotal = []
        
        projectParts = {}
        
        for inquiry in inquiries:
            #theParts = InquiryPart.objects.select_related("requestPart__part").filter(inquiry = inquiry)
            theParts = inquiry.inquirypart_set.select_related("requestPart__part").all()
            thePartsTotal = 0
            for thePart in theParts:
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
        pageLoad(request,90,100,"false")    
        for inquiryPart in inquiryParts:
            if inquiryPart["total"] == min(inquiryPartsTotal):
                inquiryPart["min"] = True

        for thePartsTotal in thePartsTotals:
            thePartsTotals[thePartsTotal] = min(thePartsTotals[thePartsTotal])
            
        for thePartsAvailability in thePartsAvailabilities:
            thePartsAvailabilities[thePartsAvailability] = min(thePartsAvailabilities[thePartsAvailability])
        
        
        pageLoad(request,100,100,"true")
        form = QuotationForm(request.POST or None, request.FILES or None, instance = quotation)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "quotation" : quotation,
                "orderConfirmation" : orderConfirmation,
                "quotationPartList" : quotationPartList,
                "parts" : parts,
                "projectParts" : projectParts,
                "partsTotals" : partsTotals,
                "partsTotal" : partsTotal,
                "totalBuyingPriceFixed" : totalBuyingPriceFixed,
                "totalGrossPriceFixed" : totalGrossPriceFixed,
                "totalDiscountPriceFixed" : totalDiscountPriceFixed,
                "totalSellingPriceFixed" : totalSellingPriceFixed,
                "totalProfitAmountPriceFixed" : totalProfitAmountPriceFixed,
                "totalProfitPrice" : totalProfitPrice,
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
        
        return render(request, 'sale/quotation/quotation_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        pageLoad(request,0,100,"false")
        quotation = get_object_or_404(Quotation, id = id)
        orderConfirmation = OrderConfirmation.objects.filter(quotation = quotation).first()
        if orderConfirmation:
            soc = orderConfirmation.orderConfirmationNo
        else:
            soc = ""
        project = quotation.project
        inquiry = quotation.inquiry
        identificationCode = quotation.identificationCode
        code = quotation.code
        yearCode = quotation.yearCode
        quotationNo = quotation.quotationNo
        approval = quotation.approval
        sessionKey = quotation.sessionKey
        user = quotation.user
        sourceCompany = quotation.sourceCompany
        pageLoad(request,10,100,"false")
        form = QuotationForm(request.POST, request.FILES or None, instance = quotation)
        if form.is_valid():
            if "saveButton" in request.POST:
                quotation = form.save(commit = False)
                quotation.sourceCompany = sourceCompany
                quotation.project = project
                quotation.inquiry = inquiry
                quotation.identificationCode = identificationCode
                quotation.code = code
                quotation.yearCode = yearCode
                quotation.quotationNo = quotationNo
                quotation.approval = approval
                quotation.soc = soc
                quotation.sessionKey = sessionKey
                quotation.user = user
                if not request.POST.get("manuelDiscount"):
                    quotation.manuelDiscount = 0
                if not request.POST.get("manuelDiscountAmount"):
                    quotation.manuelDiscountAmount = 0
                parts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
                extras = QuotationExtra.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
                partsTotals = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
                pageLoad(request,20,100,"false")
                partsTotal = 0
                

                for index, part in enumerate(parts):
                    percent = (60/len(parts)) * (index + 1)
                    pageLoad(request,20+percent,100,"false")
                    partsTotal  = partsTotal + part.totalPrice3
                    partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + part.unitPrice1
                    partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + part.unitPrice2
                    partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + part.unitPrice3
                    partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + part.totalPrice1
                    partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + part.totalPrice2
                    partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + part.totalPrice3
                    
                for index, extra in enumerate(extras):
                    partsTotal  = partsTotal + extra.totalPrice
                    partsTotals["totalUnitPrice1"] = partsTotals["totalUnitPrice1"] + extra.unitPrice
                    partsTotals["totalUnitPrice2"] = partsTotals["totalUnitPrice2"] + extra.unitPrice
                    partsTotals["totalUnitPrice3"] = partsTotals["totalUnitPrice3"] + extra.unitPrice
                    partsTotals["totalTotalPrice1"] = partsTotals["totalTotalPrice1"] + extra.totalPrice
                    partsTotals["totalTotalPrice2"] = partsTotals["totalTotalPrice2"] + extra.totalPrice
                    partsTotals["totalTotalPrice3"] = partsTotals["totalTotalPrice3"] + extra.totalPrice
                
                if quotation.manuelDiscountAmount > 0:
                    partsTotals["totalDiscount"] = quotation.manuelDiscountAmount
                else:
                    partsTotals["totalDiscount"] = partsTotals["totalTotalPrice3"] * (quotation.manuelDiscount/100)
                partsTotals["totalFinal"] = partsTotals["totalTotalPrice3"] - partsTotals["totalDiscount"]
                
                
                
                quotation.totalDiscountPrice = round(partsTotals["totalDiscount"],2)
                quotation.totalBuyingPrice = round(partsTotals["totalTotalPrice1"],2)
                quotation.totalSellingPrice = round(partsTotals["totalFinal"],2)
                quotation.save()
                pageLoad(request,100,100,"true")
                print(quotation.totalDiscountPrice)
                if quotation.totalSellingPrice == 0 or quotation.totalSellingPrice < 0 and quotation.totalBuyingPrice == 0:
                    totalProfitPrice = 0
                else:
                    totalProfitPrice = round(((quotation.totalSellingPrice / quotation.totalBuyingPrice) - 1) * 100,2)
                
                # Para miktarını belirtilen formatta gösterme
                totalBuyingPriceFixed = "{:,.2f}".format(quotation.totalBuyingPrice)
                totalGrossPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice + quotation.totalDiscountPrice)
                totalDiscountPriceFixed = "{:,.2f}".format(quotation.totalDiscountPrice)
                totalSellingPriceFixed = "{:,.2f}".format(quotation.totalSellingPrice)
                totalProfitAmountPriceFixed = "{:,.2f}".format(round(quotation.totalSellingPrice - quotation.totalBuyingPrice,2))
                # Nokta ile virgülü değiştirme
                totalBuyingPriceFixed = totalBuyingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalGrossPriceFixed = totalGrossPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalDiscountPriceFixed = totalDiscountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalSellingPriceFixed = totalSellingPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalProfitAmountPriceFixed = totalProfitAmountPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                totalPrices = {"quotation":quotation.id,
                                "totalBuyingPrice":totalBuyingPriceFixed,
                                "totalGrossPrice":totalGrossPriceFixed,
                                "totalDiscountPrice":totalDiscountPriceFixed,
                                "totalSellingPrice":totalSellingPriceFixed,
                                "totalProfitAmountPrice":totalProfitAmountPriceFixed,
                                "totalProfitPrice":totalProfitPrice,
                                "currency":quotation.currency.symbol}
                
                updateDetail(totalPrices,"quotation_update")
                return HttpResponse(status=204)
            
            elif "approvalButton" in request.POST:
                quotation = form.save(commit = False)
                quotation.sourceCompany = sourceCompany
                quotation.project = project
                quotation.inquiry = inquiry
                quotation.identificationCode = identificationCode
                quotation.code = code
                quotation.yearCode = yearCode
                quotation.quotationNo = quotationNo
                quotation.approval = "sent"
                quotation.sessionKey = sessionKey
                quotation.user = user
                if not request.POST.get("manuelDiscount"):
                    quotation.manuelDiscount = 0
                if not request.POST.get("manuelDiscountAmount"):
                    quotation.manuelDiscountAmount = 0
                quotation.save()
                pageLoad(request,100,100,"true")
                return HttpResponse(status=204)
            
            elif "oncButton" in request.POST:
                quotation = form.save(commit = False)
                quotation.sourceCompany = sourceCompany
                quotation.project = project
                quotation.inquiry = inquiry
                quotation.identificationCode = identificationCode
                quotation.code = code
                quotation.yearCode = yearCode
                quotation.quotationNo = quotationNo
                quotation.approval = "notNotified"
                quotation.sessionKey = sessionKey
                quotation.user = user
                if not request.POST.get("manuelDiscount"):
                    quotation.manuelDiscount = 0
                if not request.POST.get("manuelDiscountAmount"):
                    quotation.manuelDiscountAmount = 0
                quotation.save()
                
                identificationCode = request.user.profile.sourceCompany.saleOrderNotConfirmationCode
                yearCode = int(str(datetime.today().date().year)[-2:])
                startCodeValue = 1
                
                lastOrderNotConfirmation = OrderNotConfirmation.objects.filter(sourceCompany = request.user.profile.sourceCompany,yearCode = yearCode).extra(select =  {'myinteger': 'CAST(code AS INTEGER)'}).order_by('-myinteger').first()
                pageLoad(request,90,100,"false")
                if lastOrderNotConfirmation:
                    lastCode = lastOrderNotConfirmation.code
                else:
                    lastCode = startCodeValue - 1
                
                code = int(lastCode) + 1
                
                orderNotConfirmationNo = str(identificationCode) + "-" + str(yearCode).zfill(3) + "-" + str(code).zfill(8)
                
                orderNotConfirmation = OrderNotConfirmation.objects.create(
                    sourceCompany = request.user.profile.sourceCompany,
                    project = quotation.project,
                    quotation = quotation,
                    identificationCode = identificationCode,
                    yearCode = yearCode,
                    code = code,
                    orderNotConfirmationNo = orderNotConfirmationNo
                )
                
                orderNotConfirmation.save()
                
                quotation.soc = orderNotConfirmationNo
                quotation.save()
                pageLoad(request,100,100,"true")
                return HttpResponse(status=204)
            
            
        
            #sourceCompany = SourceCompany.objects.get(id = request.user.profile.sourceCompany.id)
            #sourceCompanyId = sourceCompany.id
            quotation = get_object_or_404(Quotation, id = id)
            quotationPdfInTask.delay(quotation.id,request.user.profile.sourceCompany.id)
            #quotationPdff(quotation)
            pageLoad(request,100,100,"true")
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            return HttpResponse(status=404)

class QuotationRevisionView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Revision Quotation")
        
        elementTag = "orderConfirmationAdd"
        elementTagSub = "orderConfirmationPartInAdd"
        elementTagId = id
        
        quotation = Quotation.objects.filter(id = id).first()
        
        ocpoList = []
        orderConfirmations = OrderConfirmation.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
        if len(orderConfirmations) > 0:
            for orderConfirmation in orderConfirmations:
                ocpoList.append(orderConfirmation.orderConfirmationNo)
                purchaseOrders = PurchaseOrder.objects.filter(sourceCompany = request.user.profile.sourceCompany,orderConfirmation__quotation = quotation)
                if len(purchaseOrders) > 0:
                    for purchaseOrder in purchaseOrders:
                        ocpoList.append(purchaseOrder.purchaseOrderNo)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "quotation" : quotation,
                "ocpoList" : ocpoList
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/quotation/quotation_revision.html', context)
    
    def post(self, request, id, *args, **kwargs):
        quotation = Quotation.objects.filter(id = id).first()
        orderConfirmations = OrderConfirmation.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
        if orderConfirmations:
            for orderConfirmation in orderConfirmations:
                orderConfirmation.delete()
        
        parts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
        extras = QuotationExtra.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
        
        #old quotation
        oldApproval = quotation.approval
        quotation.revised = True
        quotation.rev= False
        quotation.approval = "revised"
        quotation.save()
        
        quotationPdfInTask.delay(quotation.id,request.user.profile.sourceCompany.id)
        
        #new quotation
        quotation.pk = None
        quotation.quotationNo = quotation.quotationNo[:16] + str("-REV-") + str(quotation.revNo + 1)
        quotation.revised = False
        quotation.rev= True
        quotation.revNo = quotation.revNo + 1
        quotation.approval = oldApproval
        quotation.save()
        
        currencyUSD = Currency.objects.get(code = "USD")
        quotation.approval = "notSent"
        if request.user.profile.positionType.name == "Sales Assistant":
            quotation.approvalClass = "specialist"
            quotation.save()
            
            quotationTotalUSD = (quotation.totalBuyingPrice * quotation.currency.forexBuying) / currencyUSD.forexBuying
            if quotationTotalUSD < 5000:
                quotation.approval = "approved"
                quotation.save()
                
        if request.user.profile.positionType.name == "Sales Specialist":
            quotation.approvalClass = "executivor"
            quotation.save()
            quotationTotalUSD = (quotation.totalBuyingPrice * quotation.currency.forexBuying) / currencyUSD.forexBuying
            if quotationTotalUSD < 10000:
                quotation.approval = "approved"
                quotation.save()
                
        if request.user.profile.positionType.name == "Sales Executive":
            quotation.approvalClass = "director"
            quotation.save()
            quotationTotalUSD = (quotation.totalBuyingPrice * quotation.currency.forexBuying) / currencyUSD.forexBuying
            if quotationTotalUSD < 25000:
                quotation.approval = "approved"
                quotation.save()
                
        if request.user.profile.positionType.name == "Sales Director":
            quotation.approvalClass = "generalManager"
            quotation.save()
            quotationTotalUSD = (quotation.totalBuyingPrice * quotation.currency.forexBuying) / currencyUSD.forexBuying
            if quotationTotalUSD < 50000:
                quotation.approval = "approved"
                quotation.save()
                
        if request.user.profile.positionType.name == "Managing Director":
            quotation.approvalClass = "generalManager"
            quotation.save()
            quotation.approval = "approved"
            quotation.save()
        
        for part in parts:
            part.pk = None
            part.quotation = quotation
            part.save()
            
        for extra in extras:
            extra.pk = None
            extra.quotation = quotation
            extra.save()
            
        quotationPdfInTask.delay(quotation.id,request.user.profile.sourceCompany.id)
        
        return HttpResponse(status=204)

class QuotationDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Quotations")
        
        idList = list.split(",")
        
        elementTag = "quotation"
        elementTagSub = "quotationPart"
        elementTagId = idList[0]
        
        if len(idList) == 1:
            quotation = Quotation.objects.filter(id = int(idList[0])).first()
            orderConfirmation = OrderConfirmation.objects.filter(quotation = quotation).first()
            
        
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        if quotation.revised:
            alertMessage = "This quotation cannot be deleted because it has been revised"
            context = {
                "tag": tag,
                "alertMessage" : alertMessage
            }
            return render(request, 'sale/quotation/quotation_alert.html', context)
        elif orderConfirmation:
            alertMessage = "This quotation cannot be deleted because it has been confirmed"
            context = {
                "tag": tag,
                "alertMessage" : alertMessage
            }
            return render(request, 'sale/quotation/quotation_alert.html', context)
        else:
            context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId
            }  
            return render(request, 'sale/quotation/quotation_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        pageLoad(request,0,100,"false")
        idList = list.split(",")
        
        for index, id in enumerate(idList):
            percent = (90/len(idList)) * (index + 1)
            pageLoad(request,percent,100,"false")
            
            quotation = get_object_or_404(Quotation, id = id)
            if quotation.rev:
                oldQuotation = Quotation.objects.filter(revNo = quotation.revNo - 1, yearCode = quotation.yearCode, code = quotation.code).first()
                oldQuotation.revised = False
                if oldQuotation.revNo > 0:
                    oldQuotation.rev = True
                else:
                    oldQuotation.rev = False
                oldQuotation.save()
                
                currencyUSD = Currency.objects.get(code = "USD")
                oldQuotation.approval = "notSent"
                if oldQuotation.project.user.profile.positionType.name == "Sales Assistant":
                    oldQuotation.approvalClass = "specialist"
                    oldQuotation.save()
                    
                    oldQuotationTotalUSD = (oldQuotation.totalBuyingPrice * oldQuotation.currency.forexBuying) / currencyUSD.forexBuying
                    if oldQuotationTotalUSD < 5000:
                        oldQuotation.approval = "approved"
                        oldQuotation.save()
                        
                if oldQuotation.project.user.profile.positionType.name == "Sales Specialist":
                    oldQuotation.approvalClass = "executivor"
                    oldQuotation.save()
                    oldQuotationTotalUSD = (oldQuotation.totalBuyingPrice * oldQuotation.currency.forexBuying) / currencyUSD.forexBuying
                    if oldQuotationTotalUSD < 10000:
                        oldQuotation.approval = "approved"
                        oldQuotation.save()
                        
                if oldQuotation.project.user.profile.positionType.name == "Sales Executive":
                    oldQuotation.approvalClass = "director"
                    oldQuotation.save()
                    oldQuotationTotalUSD = (oldQuotation.totalBuyingPrice * oldQuotation.currency.forexBuying) / currencyUSD.forexBuying
                    if oldQuotationTotalUSD < 25000:
                        oldQuotation.approval = "approved"
                        oldQuotation.save()
                        
                if oldQuotation.project.user.profile.positionType.name == "Sales Director":
                    oldQuotation.approvalClass = "generalManager"
                    oldQuotation.save()
                    oldQuotationTotalUSD = (oldQuotation.totalBuyingPrice * oldQuotation.currency.forexBuying) / currencyUSD.forexBuying
                    if oldQuotationTotalUSD < 50000:
                        oldQuotation.approval = "approved"
                        oldQuotation.save()
                        
                if oldQuotation.project.user.profile.positionType.name == "Managing Director":
                    oldQuotation.approvalClass = "generalManager"
                    oldQuotation.save()
                    oldQuotation.approval = "approved"
                    oldQuotation.save()
                
                quotationPdfInTask.delay(quotation.id,request.user.profile.sourceCompany.id)
                
            quotation.delete()
            
        pageLoad(request,100,100,"true")
        return HttpResponse(status=204)

 
class QuotationPdfView(LoginRequiredMixin, View):
    def get(self, request, id, source, *args, **kwargs):
        tag = _("Quotation PDF")
        
        if source == "q":
            elementTag = "quotation"
            elementTagSub = "quotationPart"
            elementTagId = str(id) + "-pdf"
        elif source == "ot":
            elementTag = "orderTracking"
            elementTagSub = "orderTrackingPart"
            elementTagId = str(id) + "-pdf"

        pageLoad(request,0,100,"false")
        quotation = get_object_or_404(Quotation, id = id)
        pageLoad(request,50,100,"false")
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #quotationPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "quotation" : quotation,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        return render(request, 'sale/quotation/quotation_pdf.html', context)

class QuotationAllExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Download Quotation Excel")
        
        base_path = os.path.join(os.getcwd(), "media", "sale", "quotation", "documents")

        quotations = Quotation.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotationDate = datetime.today().date()).order_by("-id")
        
        data = {
            "Line": [],
            "Project No": [],
            "Quotation No": [],
            "Quotation Date": [],
            "Customer": [],
            "Vessel": [],
            "Customer Ref": [],
            "SOC": [],
            "Total B. Price": [],
            "Discount Price": [],
            "Total S. Price": [],
            "Currency": [],
            "Quotation Status": [],
            "Project Status": []
        }
        
        channel_layer = get_channel_layer()
        
        seq = 1
        for quotation in quotations:
            async_to_sync(channel_layer.group_send)(
                'quotation_room',
                {
                    "type": "create_excel",
                    "message": seq
                }
            )
            
            if quotation.inquiry.theRequest.vessel:
                vessel = quotation.inquiry.theRequest.vessel.name
            else:
                vessel = ""
            
            data["Line"].append(seq)
            data["Project No"].append(quotation.project.projectNo)
            data["Quotation No"].append(quotation.quotationNo)
            data["Quotation Date"].append(quotation.quotationDate)
            data["Customer"].append(quotation.inquiry.theRequest.customer.name)
            data["Vessel"].append(vessel)
            data["Customer Ref"].append(quotation.inquiry.theRequest.customerRef)
            data["SOC"].append(quotation.soc)
            data["Total B. Price"].append(quotation.totalBuyingPrice)
            data["Discount Price"].append(quotation.totalDiscountPrice)
            data["Total S. Price"].append(quotation.totalSellingPrice)
            data["Currency"].append(quotation.currency.code)
            data["Quotation Status"].append(quotation.approval)
            data["Project Status"].append(quotation.project.stage)
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/all-quotations.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Quotation', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        response = FileResponse(open('./media/sale/quotation/documents/all-quotations.xlsx', 'rb'))
        return response

class QuotationDailyExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Download Quotation Excel")
        
        base_path = os.path.join(os.getcwd(), "media", "sale", "quotation", "documents")

        quotations = Quotation.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotationDate = datetime.today().date()).order_by("-id")
        
        data = {
            "Line": [],
            "Project No": [],
            "Quotation No": [],
            "Quotation Date": [],
            "Customer": [],
            "Vessel": [],
            "Customer Ref": [],
            "SOC": [],
            "Total B. Price": [],
            "Discount Price": [],
            "Total S. Price": [],
            "Currency": [],
            "Quotation Status": [],
            "Project Status": []
        }
        
        channel_layer = get_channel_layer()
        
        seq = 1
        for quotation in quotations:
            async_to_sync(channel_layer.group_send)(
                'quotation_room',
                {
                    "type": "create_excel",
                    "message": seq
                }
            )
            
            if quotation.inquiry.theRequest.vessel:
                vessel = quotation.inquiry.theRequest.vessel.name
            else:
                vessel = ""
            
            data["Line"].append(seq)
            data["Project No"].append(quotation.project.projectNo)
            data["Quotation No"].append(quotation.quotationNo)
            data["Quotation Date"].append(quotation.quotationDate)
            data["Customer"].append(quotation.inquiry.theRequest.customer.name)
            data["Vessel"].append(vessel)
            data["Customer Ref"].append(quotation.inquiry.theRequest.customerRef)
            data["SOC"].append(quotation.soc)
            data["Total B. Price"].append(quotation.totalBuyingPrice)
            data["Discount Price"].append(quotation.totalDiscountPrice)
            data["Total S. Price"].append(quotation.totalSellingPrice)
            data["Currency"].append(quotation.currency.code)
            data["Quotation Status"].append(quotation.approval)
            data["Project Status"].append(quotation.project.stage)
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/all-quotations.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Quotation', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        response = FileResponse(open('./media/sale/quotation/documents/all-quotations.xlsx', 'rb'))
        return response


class QuotationExcelView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Download Quotation Excel")
        
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "sale", "quotation", "documents")

        quotation = Quotation.objects.filter(id = id).first()
        parts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation).order_by("sequency")
        
        dataTo = {
            "To": [],
            quotation.inquiry.theRequest.customer.name: []
        }
        
        data = {
            "Line": [],
            "Item": [],
            "Description": [],
            "Availability": [],
            "Note": [],
            "Qty": [],
            "Unit": [],
            "Unit Price": [],
            "Total Price": [],
            "Currency": [],
            "Date": []
        }
        
        for part in parts:
            data["Line"].append(part.sequency)
            data["Item"].append(part.inquiryPart.requestPart.part.partNo)
            data["Description"].append(part.inquiryPart.requestPart.part.description)
            data["Availability"].append(part.availabilityChar)
            data["Note"].append(part.note)
            data["Qty"].append(part.quantity)
            data["Unit"].append(part.inquiryPart.requestPart.part.unit)
            data["Unit Price"].append(part.unitPrice3)
            data["Total Price"].append(part.totalPrice3)
            data["Currency"].append(quotation.currency.code)
            data["Date"].append(quotation.created_date.date())
            
        data["Line"].append("")
        data["Item"].append("")
        data["Description"].append("")
        data["Availability"].append("")
        data["Note"].append("")
        data["Qty"].append("")
        data["Unit"].append("")
        data["Unit Price"].append("")
        data["Total Price"].append("")
        data["Currency"].append("")
        data["Date"].append("")
        
        data["Line"].append("")
        data["Item"].append("")
        data["Description"].append("")
        data["Availability"].append("")
        data["Note"].append("")
        data["Qty"].append("")
        data["Unit"].append("")
        data["Unit Price"].append("SUB TOTAL")
        data["Total Price"].append(quotation.totalSellingPrice)
        data["Currency"].append(quotation.currency.code)
        data["Date"].append("")
        
        data["Line"].append("")
        data["Item"].append("")
        data["Description"].append("")
        data["Availability"].append("")
        data["Note"].append("")
        data["Qty"].append("")
        data["Unit"].append("")
        data["Unit Price"].append("DISCOUNT")
        data["Total Price"].append(quotation.totalDiscountPrice)
        data["Currency"].append(quotation.currency.code)
        data["Date"].append("")
        
        data["Line"].append("")
        data["Item"].append("")
        data["Description"].append("")
        data["Availability"].append("")
        data["Note"].append("")
        data["Qty"].append("")
        data["Unit"].append("")
        data["Unit Price"].append("NET TOTAL")
        data["Total Price"].append(quotation.totalSellingPrice - quotation.totalDiscountPrice)
        data["Currency"].append(quotation.currency.code)
        data["Date"].append("")

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)
        dfTo = pd.DataFrame(dataTo)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/" + quotation.quotationNo + ".xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Quotation', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/sale/quotation/documents/' + quotation.quotationNo + '.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'
        
        return response

class QuotationFilterExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Quotation Excel")
        
        elementTag = "quotationExcel"
        elementTagSub = "quotationPartExcel"
        
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
        
        return render(request, 'sale/quotation/quotation_excel.html', context)       

class QuotationExportExcelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "sale", "quotation", "documents")

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
        
        if request.GET.get("q") == "false":
            projectExcludeStages.append("request")
            projectExcludeStages.append("inquiry")
            projectExcludeStages.append("quotation")
        
        if request.GET.get("oc") == "false":
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
        
        quotations = Quotation.objects.select_related("project","inquiry__theRequest").exclude(project__stage__in=projectExcludeStages).filter(sourceCompany = request.user.profile.sourceCompany,created_date__date__range=(startDate,endDate),inquiry__theRequest__customer__id__in=companies).order_by("-id")
        
        data = {
            "Line": [],
            "Project No": [],
            "Quotation No": [],
            "Quotation Date": [],
            "Customer": [],
            "Vessel": [],
            "Customer Ref": [],
            "SOC": [],
            "Total B. Price": [],
            "Discount Price": [],
            "Total S. Price": [],
            "Currency": [],
            "Quotation Status": [],
            "Project Status": []
        }
        
        channel_layer = get_channel_layer()
        
        seq = 0
        for quotation in quotations:
            async_to_sync(channel_layer.group_send)(
                'private_' + str(request.user.id),
                {
                    "type": "send_percent",
                    "message": seq,
                    "location" : "quotation_excel",
                    "totalCount" : len(quotations),
                    "ready" : "false"
                }
            )
            
            if quotation.inquiry.theRequest.vessel:
                vessel = quotation.inquiry.theRequest.vessel.name
            else:
                vessel = ""
            
            if quotation.inquiry.theRequest.maker:
                maker = quotation.inquiry.theRequest.maker.name
            else:
                maker = ""
            
            if quotation.inquiry.theRequest.makerType:
                makerType = quotation.inquiry.theRequest.makerType.type
            else:
                makerType = ""
                
            data["Line"].append(seq)
            data["Project No"].append(quotation.project.projectNo)
            data["Quotation No"].append(quotation.quotationNo)
            data["Quotation Date"].append(quotation.quotationDate)
            data["Customer"].append(quotation.inquiry.theRequest.customer.name)
            data["Vessel"].append(vessel)
            data["Customer Ref"].append(quotation.inquiry.theRequest.customerRef)
            data["SOC"].append(quotation.soc)
            data["Total B. Price"].append(quotation.totalBuyingPrice)
            data["Discount Price"].append(quotation.totalDiscountPrice)
            data["Total S. Price"].append(quotation.totalSellingPrice)
            data["Currency"].append(quotation.currency.code)
            data["Quotation Status"].append(quotation.approval)
            data["Project Status"].append(quotation.project.stage)
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/all-quotations.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Quotation', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        if quotations:
            quotationsCount = len(quotations)
        else:
            quotationsCount = 0
        async_to_sync(channel_layer.group_send)(
            'private_' + str(request.user.id),
            {
                "type": "send_percent",
                "message": seq,
                "location" : "quotation_excel",
                "totalCount" : quotationsCount,
                "ready" : "true"
            }
        )
        
        return HttpResponse(status=204)

class QuotationDownloadExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/sale/quotation/documents/all-quotations.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'

        return response


class QuotationPartInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Quotation Part ")
        elementTag = "quotation"
        elementTagSub = "quotationPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        quotationId = refererPath.replace("/sale/quotation/quotation_update/","").replace("/","")
        quotation = get_object_or_404(Quotation, id = id)
        
        inquiries = Inquiry.objects.filter(sourceCompany = request.user.profile.sourceCompany,project = quotation.project)
        
        form = QuotationPartForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "quotation" : quotation,
                "inquiries" : inquiries,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/quotation/quotation_part_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        quotationId = refererPath.replace("/sale/quotation_update/","").replace("/","")
        
        quotation = Quotation.objects.get(id = id)
        quotationParts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
        sequencyCount = len(quotationParts)
        
        inquiryPart = InquiryPart.objects.filter(id = int(request.POST.get("quotationPartAddInquiryPartForm"))).first()
        
        form = QuotationPartForm(request.POST, request.FILES or None)
        if form.is_valid():
            quotationPart = form.save(commit = False)
            quotationPart.sourceCompany = request.user.profile.sourceCompany
            quotationPart.user = request.user
            quotationPart.sessionKey = request.session.session_key
            quotationPart.quotation = quotation
            quotationPart.maker = inquiryPart.maker
            quotationPart.makerType = inquiryPart.makerType
            quotationPart.inquiryPart = inquiryPart
            quotationPart.quantity = inquiryPart.quantity
            quotationPart.unitPrice1 = inquiryPart.unitPrice
            quotationPart.totalPrice1 = inquiryPart.totalPrice
            quotationPart.unitPrice2 = inquiryPart.unitPrice
            quotationPart.totalPrice2 = inquiryPart.totalPrice
            quotationPart.unitPrice3 = inquiryPart.unitPrice
            quotationPart.totalPrice3 = inquiryPart.totalPrice
            quotationPart.availability = inquiryPart.availability
            quotationPart.availabilityChar = str(inquiryPart.availability)
            quotationPart.sequency = sequencyCount + 1
            
            quotationPart.save()
            
            quotationPdfInTask.delay(quotation.id,request.user.profile.sourceCompany.id)
            
            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)


class QuotationPartUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Quotation Part Detail")
        
        elementTag = "quotation"
        elementTagSub = "quotationPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        quotationPart = get_object_or_404(QuotationPart, id = id)
        print(quotationPart.sessionKey)
        form = QuotationPartForm(request.POST or None, request.FILES or None, instance = quotationPart)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "refererPath" : refererPath,
                "form" : form,
                "quotationPart" : quotationPart
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/quotation/quotation_part_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        quotationPart = get_object_or_404(QuotationPart, id = id)
        quotation = quotationPart.quotation
        sessionKey = quotationPart.sessionKey
        user = quotationPart.user
        inquiryPart = quotationPart.inquiryPart
        unitPrice1 = quotationPart.unitPrice1
        sourceCompany = quotationPart.sourceCompany
        form = QuotationPartForm(request.POST, request.FILES or None, instance = quotationPart)
        if form.is_valid():
            quotationPart = form.save(commit = False)
            quotationPart.sourceCompany = sourceCompany
            quotationPart.quotation = quotation
            quotationPart.sessionKey = sessionKey
            quotationPart.user = user
            quotationPart.inquiryPart = inquiryPart
            quotationPart.unitPrice1 = unitPrice1
            quotationPart.save()
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
        return render(request, 'sale/quotation/quotation_part_detail.html', context)

class QuotationPartProfitDuplicateView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        theQuotationPart = QuotationPart.objects.filter(id = id).first()
        quotationParts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation=theQuotationPart.quotation)
        
        for quotationPart in quotationParts:
            quotationPart.profit = theQuotationPart.profit
            quotationPart.save()
            
        return HttpResponse(status=204)

class QuotationPartDiscountDuplicateView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        theQuotationPart = QuotationPart.objects.filter(id = id).first()
        quotationParts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation=theQuotationPart.quotation)
        
        for quotationPart in quotationParts:
            quotationPart.discount = theQuotationPart.discount
            quotationPart.save()
            
        return HttpResponse(status=204)

class QuotationPartAvailabilityDuplicateView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        theQuotationPart = QuotationPart.objects.filter(id = id).first()
        quotationParts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation=theQuotationPart.quotation)
        
        for quotationPart in quotationParts:
            quotationPart.availabilityChar = theQuotationPart.availabilityChar
            quotationPart.save()
            
        return HttpResponse(status=204)
    
class QuotationPartNoteDuplicateView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        theQuotationPart = QuotationPart.objects.filter(id = id).first()
        quotationParts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation=theQuotationPart.quotation)
        
        for quotationPart in quotationParts:
            quotationPart.note = theQuotationPart.note
            quotationPart.save()
            
        return HttpResponse(status=204)
    
class QuotationPartRemarkDuplicateView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        theQuotationPart = QuotationPart.objects.filter(id = id).first()
        quotationParts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation=theQuotationPart.quotation)
        
        for quotationPart in quotationParts:
            quotationPart.remark = theQuotationPart.remark
            quotationPart.save()
            
        return HttpResponse(status=204)
    
class QuotationPartBulkUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Maker Detail")
        elementTagSub = "quotationPart"
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        quotationPart = get_object_or_404(QuotationPart, id = id)

        form = QuotationPartForm(request.POST or None, request.FILES or None, instance = quotationPart)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "refererPath" : refererPath,
                "form" : form,
                "quotationPart" : quotationPart
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/quotation/quotation_part_detail.html', context)
    
    def post(self, request, id, list, *args, **kwargs):
        idList = json.loads(list)
        print(len(idList))
        for theId in idList:
            quotationPart = QuotationPart.objects.filter(id=int(theId)).first()
            quotation = quotationPart.quotation
            currency = Currency.objects.get(id = id)
            profit = quotationPart.profit
            unitPrice1 = round((quotationPart.unitPrice1 * quotation.currency.forexBuying) / currency.forexBuying)
            totalPrice1 = round(float(unitPrice1) * float(quotationPart.quantity))
            unitPrice2 = round(float(unitPrice1) * float(1 + (float(quotationPart.profit)/100)), 2)
            totalPrice2 = round(float(unitPrice2) * float(quotationPart.quantity), 2)
            unitPrice3 = round(float(unitPrice2) * float(1 - (float(quotationPart.discount)/100)), 2)
            totalPrice3 = round(float(unitPrice3) * float(quotationPart.quantity), 2)
            quotationPart.unitPrice1 = unitPrice1
            quotationPart.totalPrice1 = totalPrice1
            quotationPart.unitPrice2 = unitPrice2
            quotationPart.totalPrice2 = totalPrice2
            quotationPart.unitPrice3 = unitPrice3
            quotationPart.totalPrice3 = totalPrice3
            quotationPart.save()
            quotationPart.profit = profit
            quotationPart.save()
            quotation.currency = currency
            quotation.save()
            
        return HttpResponse(status=204)

class QuotationPartReorderView(LoginRequiredMixin, View):
    def post(self, request, quotationId, id, old, new, *args, **kwargs):
        idList = id.split(",")
        oldList = old.split(",")
        newList = new.split(",")
        
        quotationParts = QuotationPart.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotationId, alternative = False).order_by("sequency")
        sequency = 1
        for quotationPart in quotationParts:
            quotationPart.sequency = sequency
            quotationPart.save()
            sequency = sequency + 1
        
        for i in range(len(idList)):
            quotationPart = QuotationPart.objects.select_related().filter(id = idList[i]).first()
            quotationPart.sequency = newList[i]
            quotationPart.save()
            
        quotationPartAlternatives = QuotationPart.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotationId, alternative = True).order_by("sequency")
        for quotationPartAlternative in quotationPartAlternatives:
            quotationPart = QuotationPart.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotationId, alternative = False, inquiryPart__requestPart_id = quotationPartAlternative.inquiryPart.requestPart_id).order_by("sequency").first()
            if quotationPart:
                quotationPartAlternative.sequency = quotationPart.sequency
                quotationPartAlternative.save()
            
        return HttpResponse(status=204)

class QuotationPartSourceView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Quotation Part Source")
        
        elementTag = "quotationSource"
        elementTagSub = "quotationPartSource"
        
        quotationPart = QuotationPart.objects.select_related("inquiryPart__requestPart","inquiryPart__requestPart__part").filter(id = int(request.GET.get("qp"))).first()
        inquiryParts = InquiryPart.objects.select_related("requestPart__part","inquiry__supplier","inquiry__currency").filter(sourceCompany = request.user.profile.sourceCompany,requestPart = quotationPart.inquiryPart.requestPart).order_by("inquiry__supplier__name")
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "quotationPart" : quotationPart,
                "inquiryParts" : inquiryParts,
                "sessionKey" : request.session.session_key
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/quotation/quotation_part_source.html', context)
    
    def post(self, request, *args, **kwargs):
        quotationPart = QuotationPart.objects.select_related("quotation__currency").filter(id = int(request.GET.get("qp"))).first()
        inquiryPart = InquiryPart.objects.select_related("inquiry__currency").filter(id = int(request.GET.get("ip"))).first()
        
        oldUnitPrice2 = quotationPart.unitPrice2
        
        quotationPart.inquiryPart = inquiryPart
        quotationPart.unitPrice1 = (inquiryPart.unitPrice * inquiryPart.inquiry.currency.forexBuying) / quotationPart.quotation.currency.forexBuying
        quotationPart.quantity = inquiryPart.quantity
        quotationPart.unitPrice2 = quotationPart.unitPrice1*(1 + (quotationPart.profit/100))
        quotationPart.save()
        quotationPart.unitPrice2 = oldUnitPrice2
        quotationPart.save()
        
        messageDict = {"quotation":int(request.GET.get("q"))}
                
        updateDetail(messageDict,"quotation_part_source_change")
        
        return HttpResponse(status=204)

class QuotationBuyingTotalView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Quotation Buying Total")
        
        elementTag = "quotationBuyingTotal"
        elementTagSub = "quotationPartBuyingTotal"
        
        quotation = Quotation.objects.select_related("currency").filter(id = int(request.GET.get("q"))).first()
        quotationParts = quotation.quotationpart_set.select_related("inquiryPart__inquiry__supplier").all()
        
        inquiryParts = []
        
        for quotationPart in quotationParts:
            inquiryParts.append({"supplierId" : quotationPart.inquiryPart.inquiry.supplier.id,
                                "supplier" : quotationPart.inquiryPart.inquiry.supplier.name,
                                 "totalPrice" : quotationPart.totalPrice1,
                                 "currency" : quotation.currency.code
                                 })
        
        temp_dict = {}
        for item in inquiryParts:
            supplierId = item['supplierId']
            supplier = item['supplier']
            total_price = item['totalPrice']
            
            if supplier in temp_dict:
                temp_dict[supplier] += total_price
            else:
                temp_dict[supplier] = total_price
        
        inquiries = [{'supplier': supplier, 'totalPrice': total_price} for supplier, total_price in temp_dict.items()]
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "quotation" : quotation,
                "inquiries" : inquiries,
                "sessionKey" : request.session.session_key
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/quotation/quotation_buying_total.html', context)
   

class QuotationPartDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Quotation Part")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/quotation/quotation_part_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            quotationPart = get_object_or_404(QuotationPart, id = int(id))
            quotation = quotationPart.quotation
            quotationPart.delete()
        
        quotationParts = QuotationPart.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation).order_by("sequency")
        if len(quotationParts) > 0:
            sequency = 1
            for quotationPart in quotationParts:
                quotationPart.sequency = sequency
                quotationPart.save()
                sequency = sequency +1
        return HttpResponse(status=204)

class QuotationExtraInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Add Quotation Extra ")
        elementTag = "quotation"
        elementTagSub = "quotationPart"
        elementTagId = id
        
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        quotationId = refererPath.replace("/sale/quotation/quotation_update/","").replace("/","")
        quotation = get_object_or_404(Quotation, id = id)
        
        form = QuotationExtraForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "quotation" : quotation,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/quotation/quotation_extra_add_in_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        quotationId = refererPath.replace("/sale/quotation_update/","").replace("/","")
        
        quotation = Quotation.objects.get(id = id)
        quotationExtras = QuotationExtra.objects.filter(sourceCompany = request.user.profile.sourceCompany,quotation = quotation)
        
        form = QuotationExtraForm(request.POST, request.FILES or None)
        if form.is_valid():
            quotationExtra = form.save(commit = False)
            quotationExtra.sourceCompany = request.user.profile.sourceCompany
            
            quotationExtra.user = request.user
            quotationExtra.quotation = quotation
            quotationExtra.save()
            return HttpResponse(status=204)
        else:
            print(form.errors)
            return HttpResponse(status=404)

class QuotationExtraDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Quotation Extra")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/quotation/quotation_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            quotationExtra = get_object_or_404(QuotationExtra, id = int(id))
            quotationExtra.delete()
        return HttpResponse(status=204)
