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

from .forms import *
from .tasks import *
from .pdfs.order_pdfs import *

from source.models import Company as SourceCompany
from account.models import ProformaInvoice, CommericalInvoice, SendInvoice

import pandas as pd
import json
import random
import string
from datetime import datetime
import time

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

class FinancialReportDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Reports")
        elementTag = "financialReport"
        elementTagSub = "financialReportPart"
        
        pageLoad(request,0,100,"false")
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        pageLoad(request,100,100,"true")
        
        return render(request, 'report/financial_report/financial_reports.html', context)

class FinancialReportFilterPdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Report Pdf")
        
        elementTag = "financialReportPdf"
        elementTagSub = "financialReportPartPdf"
        
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
        
        return render(request, 'report/financial_report/financial_report_pdf.html', context)       

class FinancialReportExportPdfView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        
        startDate = request.GET.get("start")
        endDate = request.GET.get("end")
        
        financialReportPdfInTask.delay(request.user.id,startDate,endDate,request.user.profile.sourceCompany.id)
        
        return HttpResponse(status=204)


class FinancialReportDownloadPdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        today = datetime.today().date().strftime('%d_%m_%Y')
        response = FileResponse(open('./media/report/financial_report/documents/financial_report_' + today + '.pdf', 'rb'))
        response['Content-Disposition'] = f'attachment; filename="financial_report_{today}.pdf"'
        return response
        
        # today = datetime.today().date().strftime("%d.%m.%Y")
        
        # def send_outlook_email(subject, message, from_email, recipient_list, attachments=None):
        #     email = EmailMessage(
        #         subject,
        #         message,
        #         from_email,
        #         recipient_list,
        #     )
        #     if attachments:
        #         for attachment in attachments:
        #             email.attach(attachment['name'], attachment['content'], attachment['mimetype'])
        #     email.send(fail_silently=False)
        #     #send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                
        # subject = 'Daily Financial Report'
        # message = f'The daily financial report dated {today} is attached.\n\n This is an automated email. \n'
        # from_email = 'ESMS - Michoapp <reporting@esmarinesolutions.com>'
        # recipient_list = ['koray.zorlu@novutechnologies.com']
        
        # today = datetime.today().date().strftime('%d_%m_%Y')
        
        # with open(f'./media/report/financial_report/documents/financial_report_{today}.pdf', 'rb') as f:
        #     attachments = [
        #         {
        #             'name': f'financial_report_{today}.pdf',
        #             'content': f.read(),
        #             'mimetype': 'application/pdf'
        #         }
        #     ]

        # send_outlook_email(subject, message, from_email, recipient_list, attachments)
        
        # return HttpResponse(status=204)
    