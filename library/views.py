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
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa
from django.template.loader import get_template 

from .forms import *
from .pdfs import *

from datetime import datetime
import json
import random
import string

class LibraryDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Library")
        elementTag = "library"
        elementTagSub = "libraryPart"
            
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'library/libraries.html', context)

class SaleDocumentsDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Sales Documents")
        elementTag = "saleDocuments"
        elementTagSub = "saleDocumentsPart"
        
        documentsJSON = {"data":[]}
        levels = ["project", "inquiry", "quotation", "order_confirmation", "order_not_confirmation", "purchase_order"]
        
        for level in levels:
            start_dir = os.path.join(os.getcwd(), "media", "sale", level)
            #hedef dosyayı başlangıç klasörü içerisinde alt klasörleri de tarayarak arar
            for root, dirs, files in os.walk(start_dir):
                for file in files:
                    file_path = os.path.join(root, file).replace(os.getcwd(), "")
                    documentsJSON["data"].append({"path" : file_path, "name" : file, "main" : "sale", "level" : level})

        documentsJSON = json.dumps(documentsJSON)
        
        with open(os.path.join(os.getcwd(), "media", "documents.json"), "w") as f:
            f.write(documentsJSON)
            
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'library/sale_documents.html', context)
    
class SaleDocumentsPdfView(LoginRequiredMixin, View):
    def get(self, request, level, name, *args, **kwargs):
        tag = _("PDF")
        
        elementTag = "saleDocuments"
        elementTagSub = "saleDocumentsPdf"
        elementTagId = str(level) + "-pdf"
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        level = level
        name = name
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "version" : version,
                "level" : level,
                "name" : name
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'library/sale_documents_pdf.html', context)