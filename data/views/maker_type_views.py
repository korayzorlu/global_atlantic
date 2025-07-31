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

class MakerTypeBulkAddExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Download Card Excel")
        response = FileResponse(open('./excelfile/maker-type-bulk-add.xls', 'rb'))
        return response

class MakerTypeAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Maker Type")
        elementTagSub = "makerType"
        form = MakerTypeForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'data/maker_type_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = MakerTypeForm(request.POST, request.FILES or None)
        if form.is_valid():
            type = form.save(commit = False)
            type.sourceCompany = request.user.profile.sourceCompany
            type.user = request.user
            type.sessionKey = request.session.session_key
            type.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'data/maker_type_add.html', context)

class MakerTypeInDetailAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Maker Type")
        elementTagSub = "makerType"
        form = MakerTypeForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/maker_type_add.html', context)
    
    def post(self, request, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        makerId = refererPath.replace("/data/maker_update/","").replace("/","")
        form = MakerTypeForm(request.POST, request.FILES or None)
        if form.is_valid():
            type = form.save(commit = False)
            type.sourceCompany = request.user.profile.sourceCompany
            type.user = request.user
            type.maker = get_object_or_404(Maker, id = makerId)
            type.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'data/maker_type_add.html', context)

class MakerTypeBulkAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Maker Type Bulk Add")
        form = ExcelForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/maker_type_bulk_add.html', context)
    
    def post(self, request, *args, **kwargs):
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        makerId = refererPath.replace("/data/maker_update/","").replace("/","")
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
                for i in range(len(df["Type"])):
                    if pd.isnull(df["Type"][i]):
                        newFile.delete()
                        messages.info(request, "Some 'Type' cell is null! Please, fill this cells and try again.")
                        return HttpResponse(status=204)
                    
                    newMakerType = MakerType.objects.create(
                        type = df["Type"][i],
                        maker = get_object_or_404(Maker, id = makerId),
                        name = df["Name"][i],
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

class MakerTypeDeleteView(LoginRequiredMixin, View):
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
        
        return render(request, 'data/maker_type_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            makerType = get_object_or_404(MakerType, id = int(id))
            makerType.delete()
        return HttpResponse(status=204)

class MakerTypeUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Maker Detail")
        elementTagSub = "makerType"
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        makerType = get_object_or_404(MakerType, id = id)
        form = MakerTypeForm(request.POST or None, request.FILES or None, instance = makerType)
        context = {
                "tag": tag,
                "elementTagSub" : elementTagSub,
                "refererPath" : refererPath,
                "form" : form,
                "makerType" : makerType
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/maker_type_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        makerType = get_object_or_404(MakerType, id = id)
        maker = makerType.maker
        sourceCompany = makerType.sourceCompany
        form = MakerTypeForm(request.POST, request.FILES or None, instance = makerType)
        if form.is_valid():
            makerType = form.save(commit = False)
            makerType.sourceCompany = sourceCompany
            makerType.maker = maker
            makerType.save()
            return HttpResponse(status=204)
            
        else:
            context = {
                    "form" : form
            }
        return render(request, 'data/maker_type_detail.html', context)
