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
from ..pdfs.order_not_confirmation_pdfs import *
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

class OrderNotConfirmationDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Order Not Confirmations")
        elementTag = "orderNotConfirmation"
        elementTagSub = "quotationPartONC"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/order_not_confirmation/order_not_confirmations.html', context)
    
class OrderNotConfirmationUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Order Not Confirmation Detail")
        elementTag = "orderNotConfirmation"
        elementTagSub = "quotationPartONC"
        elementTagId = id
        
        orderNotConfirmations = OrderNotConfirmation.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        orderNotConfirmation = get_object_or_404(OrderNotConfirmation, id = id)
        reasons = Reason.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        quotationParts = QuotationPart.objects.filter(quotation = orderNotConfirmation.quotation)
        
        orderNotConfirmationReasons = orderNotConfirmation.reasons.all()
        print(orderNotConfirmationReasons)
        orderNotConfirmationReasonsCounter = len(orderNotConfirmationReasons)
        
        form = OrderNotConfirmationForm(request.POST or None, request.FILES or None, instance = orderNotConfirmation, user = request.user)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "orderNotConfirmations" : orderNotConfirmations,
                "orderNotConfirmation" : orderNotConfirmation,
                "reasons" : reasons,
                "orderNotConfirmationReasons" : orderNotConfirmationReasons,
                "orderNotConfirmationReasonsCounter" : orderNotConfirmationReasonsCounter,
                "quotationParts" : quotationParts,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'sale/order_not_confirmation/order_not_confirmation_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        orderNotConfirmation = get_object_or_404(OrderNotConfirmation, id = id)
        project = orderNotConfirmation.project
        quotation = orderNotConfirmation.quotation
        identificationCode = orderNotConfirmation.identificationCode
        code = orderNotConfirmation.code
        yearCode = orderNotConfirmation.yearCode
        orderNotConfirmationNo = orderNotConfirmation.orderNotConfirmationNo
        sourceCompany = orderNotConfirmation.sourceCompany
        
        form = OrderNotConfirmationForm(request.POST, request.FILES or None, instance = orderNotConfirmation, user = request.user)
        
        reasons = request.POST.getlist("reasons")

        if form.is_valid():
            orderNotConfirmation = form.save(commit = False)
            orderNotConfirmation.sourceCompany = sourceCompany
            orderNotConfirmation.project = project
            orderNotConfirmation.quotation = quotation
            orderNotConfirmation.identificationCode = identificationCode
            orderNotConfirmation.code = code
            orderNotConfirmation.yearCode = yearCode
            orderNotConfirmation.orderNotConfirmationNo = orderNotConfirmationNo
            
            if len(reasons) > 0:
                orderNotConfirmation.reasons.set(reasons)
            orderNotConfirmation.save()
            
            return HttpResponse(status=204)
            
        else:
            print(form.errors)
            context = {
                    "form" : form
            }
            return render(request, 'sale/order_not_confirmation/order_not_confirmation_detail.html', context)

class OrderNotConfirmationDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Order Not Confirmation")
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
        
        return render(request, 'sale/order_not_confirmation/order_not_confirmation_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:   
            orderNotConfirmation = get_object_or_404(OrderNotConfirmation, id = id)
            orderNotConfirmation.delete()
        return HttpResponse(status=204)
            
class OrderNotConfirmationPdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Order Not Confirmation PDF")
        
        elementTag = "orderNotConfirmation"
        elementTagSub = "quotationPartONC"
        elementTagId = str(id) + "-pdf"
        
        orderNotConfirmation = get_object_or_404(OrderNotConfirmation, id = id)
        
        orderNotConfirmationPdf(orderNotConfirmation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "orderNotConfirmation" : orderNotConfirmation
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'sale/order_not_confirmation/order_not_confirmation_pdf.html', context)
    