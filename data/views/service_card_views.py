from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.translation import gettext_lazy as _
# Create your views here.
from django.views import View
from urllib.parse import urlparse
from django.contrib import messages
from django.db.models import Prefetch

from ..forms import *

from sale.models import RequestPart, InquiryPart, QuotationPart, PurchaseOrderPart
from account.models import SendInvoicePart, ProformaInvoicePart, IncomingInvoicePart
from service.models import OfferPart

import pandas as pd

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

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

class ServiceCardDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Service Cards")
        elementTag = "serviceCard"
        elementTagSub = "serviceCardPart"
        
        serviceCards = ServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "serviceCards" : serviceCards
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/service_cards.html', context)

class ServiceCardAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Service Card")
        elementTag = "serviceCard"
        elementTagSub = "serviceCardPart"
        elementTagId = "new"
        
        form = ServiceCardForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/service_card_add.html', context)
    
    def post(self, request, *args, **kwargs):
        elementTag = "serviceCard"
        elementTagSub = "serviceCardPart"
        elementTagId = "new"

        form = ServiceCardForm(request.POST, request.FILES or None)
        if form.is_valid():
            serviceCard = form.save()
            serviceCard.sourceCompany = request.user.profile.sourceCompany
            serviceCard.save()
            return HttpResponse(status=204)
        else:
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"circle-check",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
        
class ServiceCardUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Service Card Detail")
        elementTag = "serviceCard"
        elementTagSub = "serviceCardPart"
        elementTagId = id
        
        serviceCards = ServiceCard.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        serviceCard = get_object_or_404(ServiceCard, id = id)
        form = ServiceCardForm(request.POST or None, request.FILES or None, instance = serviceCard)
        context = {
                "tag": tag,
                "form" : form,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "serviceCards" : serviceCards,
                "serviceCard" : serviceCard
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/service_card_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "serviceCard"
        elementTagSub = "serviceCardPart"
        elementTagId = id

        serviceCard = get_object_or_404(ServiceCard, id = id)
        sourceCompany = serviceCard.sourceCompany
        form = ServiceCardForm(request.POST, request.FILES or None, instance = serviceCard)

        if form.is_valid():
            serviceCard.sourceCompany = sourceCompany
            serviceCard.save()
            
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"circle-check",
                "message":"Saved"
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=204)
            
        else:
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"circle-check",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
    
class ServiceCardDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Service Card")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/service_card_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            service_card = get_object_or_404(ServiceCard, id = int(id))
            service_card.delete()
        return HttpResponse(status=204)
    