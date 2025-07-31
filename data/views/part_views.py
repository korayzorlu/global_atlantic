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

class PartUniqueDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Part Uniques")
        part_uniques = PartUnique.objects.filter()
        context = {
                    "tag" : tag,
                    "part_uniques" : part_uniques
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/part_uniques.html', context)

class PartUniqueAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Part Unique")
        form = PartUniqueForm(request.POST or None, request.FILES or None)
        context = {
                "tag": tag,
                "form" : form
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/part_unique_add.html', context)
    
    def post(self, request, *args, **kwargs):
        form = PartUniqueForm(request.POST, request.FILES or None)
        if form.is_valid():
            partUnique = form.save()
            partUnique.sourceCompany = request.user.profile.sourceCompany
            partUnique.save()
            return HttpResponse(status=204)
        else:
            context = {
                    "form" : form
            }
            return render(request, 'data/part_unique_add.html', context)
        
class PartUniqueUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Part Unique Detail")
        partUniques = PartUnique.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        partUnique = get_object_or_404(PartUnique, id = id)
        form = PartUniqueForm(request.POST or None, request.FILES or None, instance = partUnique)
        context = {
                "tag": tag,
                "form" : form,
                "partUniques" : partUniques,
                "partUnique" : partUnique
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/part_unique_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        part_unique = get_object_or_404(PartUnique, id = id)
        sourceCompany = part_unique.sourceCompany
        form = PartUniqueForm(request.POST, request.FILES or None, instance = part_unique)
        if form.is_valid():
            part_unique = form.save(commit = False)
            part_unique.sourceCompany = sourceCompany
            part_unique.save()
            
        else:
            context = {
                    "form" : form
            }
        return redirect(request.path)
    
class PartUniqueDeleteView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Delete Part Unique")
        part_unique = get_object_or_404(PartUnique, id = id)
        context = {
                "tag": tag,
                "part_unique" : part_unique
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/part_unique_delete.html', context)
    
    def post(self, request, id, *args, **kwargs):
        part_unique = get_object_or_404(PartUnique, id = id)
        part_unique.delete()
        return HttpResponse(status=204)

class PartDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Parts")
        elementTag = "part"
        elementTagSub = "partPart"
        
        dataAuthorizations = request.user.profile.dataAuth.all()
        
        dataAuthorizationList = []
        
        for dataAuthorization in dataAuthorizations:
            dataAuthorizationList.append(dataAuthorization.code)
        
        #parts = Part.objects.filter()
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "dataAuthorizationList" : dataAuthorizationList
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/parts.html', context)

class PartAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Add Part")
        elementTag = "part"
        elementTagSub = "partPart"
        elementTagId = "new"
        
        form = PartForm(request.POST or None, request.FILES or None, user = request.user)
        
        if is_ajax(request=request):
            term = request.GET.get("term")
            parts = PartUnique.objects.filter(sourceCompany = request.user.profile.sourceCompany,code__icontains = term)
            response_content = list(parts.values())
            
            return JsonResponse(response_content, safe=False)
        
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
        
        return render(request, 'data/part_add.html', context)
    
    def post(self, request, *args, **kwargs):
        elementTag = "part"
        elementTagSub = "partPart"
        elementTagId = "new"

        form = PartForm(request.POST, request.FILES or None, user = request.user)
        techSpecCustom = request.POST.getlist("techSpecName")[0]
        if form.is_valid():
            unique = form.cleaned_data.get("unique")
            maker = form.cleaned_data.get("maker")
            type = form.cleaned_data.get("type")
            manufacturer = form.cleaned_data.get("manufacturer")
            partNo = form.cleaned_data.get("partNo")
            group = form.cleaned_data.get("group")
            description = form.cleaned_data.get("description")
            crossRef = form.cleaned_data.get("crossRef")
            ourRef = form.cleaned_data.get("ourRef")
            drawingNr = form.cleaned_data.get("drawingNr")
            barcode = form.cleaned_data.get("barcode")
            quantity = form.cleaned_data.get("quantity")
            unit = form.cleaned_data.get("unit")
            buyingPrice = form.cleaned_data.get("buyingPrice")
            retailPrice = form.cleaned_data.get("retailPrice")
            dealerPrice = form.cleaned_data.get("dealerPrice")
            wholesalePrice = form.cleaned_data.get("wholesalePrice")
            currency = form.cleaned_data.get("currency")
            note = form.cleaned_data.get("note")
            
            part = form.save(commit = False)
            
            if unique:
                part.partUnique = unique
            
            part.sourceCompany = request.user.profile.sourceCompany
            part.maker = maker
            part.type = type
            part.manufacturer = manufacturer
            part.partNo = partNo
            part.group = group
            part.description = description
            part.crossRef = crossRef
            part.ourRef = ourRef
            part.drawingNr = drawingNr
            part.barcode = barcode
            part.quantity = quantity
            part.unit = unit
            part.buyingPrice = buyingPrice
            part.retailPrice = retailPrice
            part.dealerPrice = dealerPrice
            part.wholesalePrice = wholesalePrice
            part.currency = currency
            part.note = note
            
            startPartUniqueCodeValue = 1
            startPartUniqueValue = 101
            
            if unique:
                lastPart = Part.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,partUnique = unique).order_by('-partUniqueCode').first()
                if lastPart:
                    # En son oluşturulan nesnenin id'sini al
                    lastpartUniqueCode = lastPart.partUniqueCode
                    part.techncialSpecification = lastPart.techncialSpecification
                    part.quantity = lastPart.quantity
                else:
                    # Veritabanında hiç nesne yoksa, start_value değerini kullan
                    lastpartUniqueCode = startPartUniqueCodeValue - 1
                part.partUniqueCode = int(lastpartUniqueCode) + 1
            else:
                if len(techSpecCustom) > 0:
                    checkParts = Part.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,techncialSpecification = techSpecCustom)
                    if len(checkParts) > 0:
                        checkPart = checkParts[0]
                        lastPart = Part.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany,partUnique = checkPart.partUnique).order_by('-partUniqueCode').first()
                        if lastPart:
                            # En son oluşturulan nesnenin id'sini al
                            lastpartUniqueCode = lastPart.partUniqueCode
                            part.techncialSpecification = lastPart.techncialSpecification
                            part.quantity = lastPart.quantity
                        else:
                            # Veritabanında hiç nesne yoksa, start_value değerini kullan
                            lastpartUniqueCode = startPartUniqueCodeValue - 1
                        part.partUnique = checkPart.partUnique
                        part.partUniqueCode = int(lastpartUniqueCode) + 1
                    else:   
                        lastPartUnique = PartUnique.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany).order_by('-code').first()
                        
                        if lastPartUnique:  
                            newPartUnique = PartUnique(sourceCompany = request.user.profile.sourceCompany,code = int(lastPartUnique.code) + 1)
                            newPartUnique.save()
                        else:
                            newPartUnique = PartUnique(sourceCompany = request.user.profile.sourceCompany,code = int(startPartUniqueValue))
                            newPartUnique.save()
                        
                        part.partUnique = newPartUnique
                        part.partUniqueCode = int(startPartUniqueCodeValue)
                        
                        part.techncialSpecification = techSpecCustom
                else:
                    lastPartUnique = PartUnique.objects.select_related().filter(sourceCompany = request.user.profile.sourceCompany).order_by('-code').first()
                        
                    if lastPartUnique:  
                        newPartUnique = PartUnique(sourceCompany = request.user.profile.sourceCompany,code = int(lastPartUnique.code) + 1)
                        newPartUnique.save()
                    else:
                        newPartUnique = PartUnique(sourceCompany = request.user.profile.sourceCompany,code = int(startPartUniqueValue))
                        newPartUnique.save()
                    
                    part.partUnique = newPartUnique
                    part.partUniqueCode = int(startPartUniqueCodeValue)
            
                
            part.save()
            return HttpResponse(status=204)
        else:
            data = {
                "block":f"message-container-{elementTag}-{elementTagId}",
                "icon":"circle-check",
                "message":form.errors
            }
            
            sendAlert(data,"form")
            return HttpResponse(status=404)
        
class PartUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("Part Detail")
        elementTag = "part"
        elementTagSub = "partPart"
        elementTagId = id
        
        part = Part.objects.select_related("partUnique").filter(id = id).first()
        requestParts = part.request_part_part.order_by("-id").all()
        
        unique = str(part.partUnique) + "." + str(str(part.partUniqueCode).zfill(3))
        form = PartUpdateForm(request.POST or None, request.FILES or None, instance = part, user = request.user)
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "form" : form,
                "part" : part,
                "requestParts" : requestParts,
                "unique" : unique
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/part_detail.html', context)
    
    def post(self, request, id, *args, **kwargs):
        elementTag = "part"
        elementTagSub = "partPart"
        elementTagId = id

        part = Part.objects.select_related("partUnique").filter(id=id).first()
        sourceCompany = part.sourceCompany
        partUniqueCode = part.partUniqueCode
        partUnique = part.partUnique
        form = PartUpdateForm(request.POST, request.FILES or None, instance = part, user = request.user)
        if form.is_valid():
            part = form.save(commit = False)

            part.partUnique = partUnique
            part.partUniqueCode = partUniqueCode
            part.sourceCompany = sourceCompany
            part.save()
            
            # matchedParts = Part.objects.filter(partUnique = partUnique)
            # for matchedPart in matchedParts:
            #     matchedPart.techncialSpecification = part.techncialSpecification
            #     matchedPart.quantity = part.quantity
            #     matchedPart.save()
                
            
            
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

class PartDeleteView(LoginRequiredMixin, View):
    def get(self, request, list, *args, **kwargs):
        tag = _("Delete Part")
        idList = list.split(",")
        context = {
                "tag": tag
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/part_delete.html', context)
    
    def post(self, request, list, *args, **kwargs):
        idList = list.split(",")
        for id in idList:
            part = get_object_or_404(Part, id = int(id))
            part.delete()
        return HttpResponse(status=204)

class PartFilterExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Part Excel")
        
        elementTag = "partExcel"
        elementTagSub = "partPartExcel"
        
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
        
        return render(request, 'data/part_excel.html', context)       

class PartExportExcelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "data", "part", "documents")
        
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        partExcludeUnits = []
        
        if request.GET.get("pc") == "false":
            partExcludeUnits.append("pc")
        
        if request.GET.get("kg") == "false":
            partExcludeUnits.append("kg")
        
        if request.GET.get("mm") == "false":
            partExcludeUnits.append("mm")
            
        makers = request.GET.get("m")
        types = request.GET.get("t")
            
        if request.GET.get("o") == "true":
            parts = Part.objects.select_related("maker","type").exclude(unit__in=partExcludeUnits).filter(
                sourceCompany = request.user.profile.sourceCompany,
                request_part_part__isnull=False
            ).order_by("maker__name","type__type").distinct()
        elif request.GET.get("no") == "true":
            parts = Part.objects.select_related("maker","type").exclude(unit__in=partExcludeUnits).filter(
                sourceCompany = request.user.profile.sourceCompany,
                request_part_part__isnull=True
            ).order_by("maker__name","type__type").distinct()
        else:
            parts = Part.objects.select_related("maker","type").exclude(unit__in=partExcludeUnits).filter(
                sourceCompany = request.user.profile.sourceCompany
            ).order_by("maker__name","type__type")

        if makers:
            makers = makers.split(",")
            parts = parts.filter(maker__id__in=makers).order_by("maker__name","type__type")
            
        if types:
            types = types.split(",")
            parts = parts.filter(type__id__in=types).order_by("maker__name","type__type")

        data = {
            "Line": [],
            "ID": [],
            "Maker": [],
            "Type": [],
            "Part No": [],
            "Description": [],
            "Group": [],
            "Technical Specification": [],
            "Drawing Nr.": [],
            "Manufacturer": [],
            "Cross Ref.": [],
            "Our Ref.": [],
            "Unit": []
            
        }
        
        channel_layer = get_channel_layer()
        
        seq = 0
        for part in parts:
            async_to_sync(channel_layer.group_send)(
                'private_' + str(request.user.id),
                {
                    "type": "send_percent",
                    "message": seq,
                    "location" : "part_excel",
                    "totalCount" : len(parts),
                    "ready" : "false"
                }
            )
            
            if part.maker:
                maker = part.maker.name
            else:
                maker = ""
                
            if part.type:
                type = part.type.type
            else:
                type = ""
                
            data["Line"].append(seq+1)
            data["ID"].append(part.id)
            data["Maker"].append(maker)
            data["Type"].append(type)
            data["Part No"].append(part.partNo)
            data["Description"].append(part.description)
            data["Group"].append(part.group)
            data["Technical Specification"].append(part.techncialSpecification)
            data["Drawing Nr."].append(part.drawingNr)
            data["Manufacturer"].append(part.manufacturer)
            data["Cross Ref."].append(part.crossRef)
            data["Our Ref."].append(part.ourRef)
            data["Unit"].append(part.unit)
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/part-list.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Quotation', index=False)
            # dfTo.to_excel(writer, sheet_name='Quotation', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='Quotation', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)
        
        if parts:
            partsCount = len(parts)
        else:
            partsCount = 0
        async_to_sync(channel_layer.group_send)(
            'private_' + str(request.user.id),
            {
                "type": "send_percent",
                "message": seq,
                "location" : "part_excel",
                "totalCount" : partsCount,
                "ready" : "true"
            }
        )
        
        return HttpResponse(status=204)

class PartDownloadExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/data/part/documents/part-list.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'
        
        return response


class PartDocumentView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        elementTag = "part"
        elementTagSub = "partPart"
        elementTagId = id
        
        parts = Part.objects.filter(sourceCompany = request.user.profile.sourceCompany)
        part = get_object_or_404(Part, id = id)
        
        images = PartImage.objects.filter(sourceCompany = request.user.profile.sourceCompany, part = part)
        
        imageForm = PartImageForm(request.POST or None, request.FILES or None)
        context = {
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "imageForm" : imageForm,
                "parts" : parts,
                "part" : part,
                "images" : images,
                "sessionKey" : request.session.session_key,
                "user" : request.user
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'data/part_document.html', context)       
class PartImageAddView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        part = get_object_or_404(Part, id = id)
        
        image = PartImage.objects.create(
            sourceCompany = request.user.profile.sourceCompany,
            user = request.user,
            part = part,
            image = request.FILES.get("image")
        )
        
        image.save()
            
        return HttpResponse(status=204)
    
class PartImageDeleteView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        
        image = PartImage.objects.get(id = id)
        image.delete()
            
        return HttpResponse(status=204)

