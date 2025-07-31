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

class MakerDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Makers")
        elementTag = "maker"
        elementTagSub = "makerType"
        
        makers = Maker.objects.filter()
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "makers" : makers
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/makers.html', context)

class MakerBulkAddExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Download Card Excel")
        response = FileResponse(open('./excelfile/maker-bulk-add.xlsx', 'rb'))
        return response

class MakerAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Maker")
        elementTag = "maker"
        elementTagSub = "makerType"
        elementTagId = "new"
        
        form = MakerForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/maker_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = MakerForm(request.POST, request.FILES or None)
        if form.is_valid():
            maker = form.save()
            maker.sourceCompany = request.user.profile.sourceCompany
            maker.save()
            
            sessionTypes = MakerType.objects.filter(sessionKey = request.session.session_key, user = request.user, maker = None)
            for sessionType in sessionTypes:
                sessionType.maker = maker
                sessionType.save()
                
            return HttpResponse(status=204)
        else:
            data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":form.errors
                }
            
            sendAlert(data,"default")
            return HttpResponse(status=404)
        
class MakerDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Maker")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/maker_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            maker = get_object_or_404(Maker, id = int(id))
            maker.delete()
        return HttpResponse(status=204)

class MakerBulkAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Maker Bulk Add")
        form = ExcelForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/maker_bulk_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = ExcelForm(request.POST, request.FILES or None)
        if form.is_valid():
            newFile = form.save(commit = False)
            newFile.save()
            if request.FILES.getlist("file") == []:
                messages.warning(request, "File Not Found!")
                return HttpResponse(status=204)
            try:
                data = pd.read_excel(str(newFile.file.path))
                df = pd.DataFrame(data)
            except ValueError:
                newFile.delete()
                messages.warning(request, "The file must be excel format!")
                return HttpResponse(status=204)
            try:
                for i in range(len(df["Maker"])):
                    if pd.isnull(df["Maker"][i]):
                        newFile.delete()
                        messages.info(request, "Some 'Maker' cell is null! Please, fill this cells and try again.")
                        return HttpResponse(status=204)
                    
                    newMaker = Maker.objects.create(
                        name = df["Maker"][i],
                        info = df["Info"][i],
                        )
            except KeyError:
                newFile.delete()
                messages.info(request, "Error! Please, check the columns header and try again.")
                return HttpResponse(status=204)

            except ValueError as e:
                print(e)
                newFile.delete()
                messages.info(request, "Error! Other characters have been entered in the cells where numbers must be entered. Please, check this cells and try again.")
                return HttpResponse(status=204)

            newFile.delete()
            
            messages.success(request, "Added Successfuly!")
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
        return HttpResponse(status=204)
  
class MakerUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Maker Detail")
        elementTag = "maker"
        elementTagSub = "makerType"
        elementTagId = id
        
        makers = Maker.objects.filter()
        maker = get_object_or_404(Maker, id = id)
        form = MakerForm(request.POST or None, request.FILES or None, instance = maker)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "makers" : makers,
                "maker" : maker,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/maker_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "maker"
        elementTagSub = "makerType"
        elementTagId = id

        maker = get_object_or_404(Maker, id = id)
        sourceCompany = maker.sourceCompany
        form = MakerForm(request.POST, request.FILES or None, instance = maker)
        if form.is_valid():
            maker = form.save(commit = False)
            maker.sourceCompany = sourceCompany
            maker.save()
            
            sessionTypes = MakerType.objects.filter(sessionKey = request.session.session_key, user = request.user, maker = None)
            for sessionType in sessionTypes:
                sessionType.maker = maker
                sessionType.save()
                
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
                "icon":"triangle-exclamation",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
