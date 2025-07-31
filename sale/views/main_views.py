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

 
class EmailSendView(LoginRequiredMixin, View):
    def get(self, request, id, type, *args, **kwargs):
        tag = _("Quotation PDF")
        
        elementTag = "email"
        elementTagSub = "emailSend"
        elementTagId = "table"
        
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

        return render(request, 'sale/email_send.html', context)
    
    def post(self, request, id, type, *args, **kwargs):
        sendEmail(id)
            
        return HttpResponse(status=204)