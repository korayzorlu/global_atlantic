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
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.middleware.csrf import get_token

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa
from django.template.loader import get_template 
import json
from itertools import chain
import xmltodict
import requests as rs
from django.utils import timezone
from datetime import datetime, timedelta

from ..forms import *
from ..tasks import *
from ..pdfs.soa_pdfs import *
from ..pdfs.soa_customer_pdfs import *



import random
import string
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Border, Side

class SOASendInvoiceFilterExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Send Invoice Excel")
        
        elementTag = "soaSendInvoiceExcel"
        elementTagSub = "soaSendInvoicePartExcel"
        
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
        
        return render(request, 'account/soa_send_invoice_excel.html', context)       

class SOASendInvoiceExportExcelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "account", "send_invoice", "documents")
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        if request.GET.get("start") == "":
            startDate = "01/01/2024"
        else:
            startDate = datetime.strptime(request.GET.get("start"), "%d/%m/%Y").date()
            
        if request.GET.get("end") == "":
            endDate = datetime.today().date().strftime('%d/%m/%Y')
        else:
            endDate = datetime.strptime(request.GET.get("end"), "%d/%m/%Y").date()
        
        sendInvoiceExcludeTypes = []
        
        if request.GET.get("o") == "false":
            sendInvoiceExcludeTypes.append("order")
            
        if request.GET.get("s") == "false":
            sendInvoiceExcludeTypes.append("service")
        
        customers = request.GET.get("c")
        
        if request.GET.get("p") == "true":
            sendInvoices = SendInvoice.objects.select_related("customer").exclude(group__in=sendInvoiceExcludeTypes).filter(
                sourceCompany = request.user.profile.sourceCompany,
                payed=True,sendInvoiceDate__range=(startDate,endDate)
            ).order_by("sendInvoiceDate").distinct().annotate(num_vessels=Count('vessel')).order_by('customer__name', '-num_vessels', 'vessel')
        elif request.GET.get("np") == "true":
            sendInvoices = SendInvoice.objects.select_related("customer").exclude(group__in=sendInvoiceExcludeTypes).filter(
                sourceCompany = request.user.profile.sourceCompany,
                payed=False,sendInvoiceDate__range=(startDate,endDate)
            ).order_by("sendInvoiceDate").distinct().annotate(num_vessels=Count('vessel')).order_by('customer__name', '-num_vessels', 'vessel')
        else:
            sendInvoices = SendInvoice.objects.select_related("customer").exclude(group__in=sendInvoiceExcludeTypes).filter(
                sourceCompany = request.user.profile.sourceCompany,
                sendInvoiceDate__range=(startDate,endDate)
            ).order_by("sendInvoiceDate").annotate(num_vessels=Count('vessel')).order_by('customer__name', '-num_vessels', 'vessel')
        
        if customers:
            customers = customers.split(",")
            sendInvoices = sendInvoices.filter(
                sourceCompany = request.user.profile.sourceCompany,
                customer__id__in=customers
            ).order_by("customer__name").annotate(num_vessels=Count('vessel')).order_by('customer__name', '-num_vessels', 'vessel')
        
        
        data = {
            "Customer": [],
            "Billing Name": [],
            "Invoice No": [],
            "Project No": [],
            "Vessel": [],
            "IMO": [],
            "Invoice Date": [],
            "Payment Date": [],
            "Amount": [],
            "Total Payment": [],
            "Balance": [],
            "Currency": [],
            "Exchange Rate": [],
            "TRY Gross": [],
        }
        
        channel_layer = get_channel_layer()
        
        seq = 0
        for sendInvoice in sendInvoices:
            async_to_sync(channel_layer.group_send)(
                'private_' + str(request.user.id),
                {
                    "type": "send_percent",
                    "message": seq,
                    "location" : "soa_send_invoice_excel",
                    "totalCount" : len(sendInvoices),
                    "ready" : "false"
                }
            )
            
            if sendInvoice.theRequest:
                project = sendInvoice.theRequest.requestNo
            elif sendInvoice.offer:
                project = sendInvoice.offer.offerNo
            else:
                project  = ""
            
            if sendInvoice.customer:
                customer = sendInvoice.customer.name
            else:
                customer = ""
            
            if sendInvoice.vessel:
                vessel = f"{sendInvoice.vessel.get_type_display()} {sendInvoice.vessel.name}"
                imo = sendInvoice.vessel.imo
            else:
                vessel = ""
                imo = ""
                
            if sendInvoice.billing:
                billing = sendInvoice.billing.name
            else:
                billing = ""
                
            data["Customer"].append(customer)
            data["Billing Name"].append(billing)
            data["Invoice No"].append(sendInvoice.sendInvoiceNo)
            data["Project No"].append(project)
            data["Vessel"].append(vessel)
            data["IMO"].append(imo)
            data["Invoice Date"].append(str(sendInvoice.sendInvoiceDate.strftime("%d.%m.%Y")))
            data["Payment Date"].append(str(sendInvoice.paymentDate.strftime("%d.%m.%Y")))
            data["Amount"].append(round(sendInvoice.totalPrice,2))
            data["Total Payment"].append(round(sendInvoice.paidPrice,2))
            data["Balance"].append(round(sendInvoice.totalPrice - sendInvoice.paidPrice,2))
            data["Currency"].append(sendInvoice.currency.code)
            data["Exchange Rate"].append(sendInvoice.exchangeRate)
            data["TRY Gross"].append(round(sendInvoice.totalPrice * sendInvoice.exchangeRate))
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/soa-customer-list.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='SendInvoice', index=False)
            # dfTo.to_excel(writer, sheet_name='SendInvoice', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='SendInvoice', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)

        #stil düzeltme
        wb = load_workbook(base_path + "/soa-customer-list.xlsx")
        ws = wb.active

        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        previous_customer = None
        row_offset = 1
        for index, sendInvoice in enumerate(sendInvoices):
            # Müşteri değişimini kontrol et
            current_row = index + row_offset
            if sendInvoice.customer != previous_customer:
                if previous_customer is not None:
                    # Boş satır ekle
                    row_offset += 1
                    current_row = index + row_offset
                    ws.insert_rows(current_row)

            previous_customer = sendInvoice.customer

        wb.save(base_path + "/soa-customer-list.xlsx")

        #stil düzeltme-end

        #pdf to excel
        # input_pdf = base_path + "/" + "SI-024-00000029.pdf"
        # output_pdf = base_path + "/" + "convert_pdf_to_xls.csv"

        # tabula.convert_into(input_pdf, output_pdf, output_format="csv")
        
        #pdf to excel-end
        
        if sendInvoices:
            sendInvoicesCount = len(sendInvoices)
        else:
            sendInvoicesCount = 0
        async_to_sync(channel_layer.group_send)(
            'private_' + str(request.user.id),
            {
                "type": "send_percent",
                "message": seq,
                "location" : "soa_send_invoice_excel",
                "totalCount" : sendInvoicesCount,
                "ready" : "true"
            }
        )
        
        return HttpResponse(status=204)

class SOASendInvoiceDownloadExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/account/send_invoice/documents/soa-customer-list.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'
        
        return response





class SOASendInvoiceFilterPdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Send Invoice Pdf")
        
        elementTag = "soaSendInvoicePdf"
        elementTagSub = "soaSendInvoicePartPdf"
        
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
        
        return render(request, 'account/soa_send_invoice_pdf.html', context)       

class SOASendInvoiceExportPdfView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "account", "send_invoice", "documents")
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        if request.GET.get("start") == "":
            startDate = "01/01/2024"
        else:
            startDate = datetime.strptime(request.GET.get("start"), "%d/%m/%Y").date()
            
        if request.GET.get("end") == "":
            endDate = datetime.today().date().strftime('%d/%m/%Y')
        else:
            endDate = datetime.strptime(request.GET.get("end"), "%d/%m/%Y").date()
        
        sendInvoiceExcludeTypes = []
        
        if request.GET.get("o") == "false":
            sendInvoiceExcludeTypes.append("order")
            
        if request.GET.get("s") == "false":
            sendInvoiceExcludeTypes.append("service")
        
        customers = request.GET.get("c")
        
        # if request.GET.get("p") == "true":
        #     sendInvoices = SendInvoice.objects.select_related("customer").exclude(group__in=sendInvoiceExcludeTypes).filter(
        #         sourceCompany = request.user.profile.sourceCompany,
        #         payed=True,sendInvoiceDate__range=(startDate,endDate)
        #     ).order_by("sendInvoiceDate").distinct().annotate(num_vessels=Count('vessel')).order_by('customer__name', '-num_vessels', 'vessel')
        # elif request.GET.get("np") == "true":
        #     sendInvoices = SendInvoice.objects.select_related("customer").exclude(group__in=sendInvoiceExcludeTypes).filter(
        #         sourceCompany = request.user.profile.sourceCompany,
        #         payed=False,sendInvoiceDate__range=(startDate,endDate)
        #     ).order_by("sendInvoiceDate").distinct().annotate(num_vessels=Count('vessel')).order_by('customer__name', '-num_vessels', 'vessel')
        # else:
        #     sendInvoices = SendInvoice.objects.select_related("customer").exclude(group__in=sendInvoiceExcludeTypes).filter(
        #         sourceCompany = request.user.profile.sourceCompany,
        #         sendInvoiceDate__range=(startDate,endDate)
        #     ).order_by("sendInvoiceDate").annotate(num_vessels=Count('vessel')).order_by('customer__name', '-num_vessels', 'vessel')
        
        # if customers:
        #     customers = customers.split(",")
        #     sendInvoices = sendInvoices.filter(
        #         sourceCompany = request.user.profile.sourceCompany,
        #         customer__id__in=customers
        #     ).order_by("customer__name").annotate(num_vessels=Count('vessel')).order_by('customer__name', '-num_vessels', 'vessel')
        
        
        soaCustomerPdf(request.user.profile.sourceCompany.id, request.user.id)
        
        # channel_layer = get_channel_layer()
        
        # seq = 0
        # for sendInvoice in sendInvoices:
        #     async_to_sync(channel_layer.group_send)(
        #         'private_' + str(request.user.id),
        #         {
        #             "type": "send_percent",
        #             "message": {"seq":seq,"version":""},
        #             "location" : "soa_send_invoice_pdf",
        #             "totalCount" : len(sendInvoices),
        #             "ready" : "false"
        #         }
        #     )
            
        #     if sendInvoice.theRequest:
        #         project = sendInvoice.theRequest.requestNo
        #     elif sendInvoice.offer:
        #         project = sendInvoice.offer.offerNo
        #     else:
        #         project  = ""
            
        #     if sendInvoice.customer:
        #         customer = sendInvoice.customer.name
        #     else:
        #         customer = ""
            
        #     if sendInvoice.vessel:
        #         vessel = sendInvoice.vessel.name
        #         imo = sendInvoice.vessel.imo
        #     else:
        #         vessel = ""
        #         imo = ""
                
        #     if sendInvoice.billing:
        #         billing = sendInvoice.billing.name
        #     else:
        #         billing = ""
                
            
        #     seq = seq + 1

        
        # if sendInvoices:
        #     sendInvoicesCount = len(sendInvoices)
        # else:
        #     sendInvoicesCount = 0

        # characters = string.ascii_letters + string.digits
        # version = ''.join(random.choice(characters) for _ in range(10))

        # async_to_sync(channel_layer.group_send)(
        #     'private_' + str(request.user.id),
        #     {
        #         "type": "send_percent",
        #         "message": {"seq":seq,"version":version},
        #         "location" : "soa_send_invoice_pdf",
        #         "totalCount" : sendInvoicesCount,
        #         "ready" : "true"
        #     }
        # )
        
        return HttpResponse(status=204)

class SOASendInvoiceDownloadPdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = FileResponse(open(f"./media/docs/{str(request.user.profile.sourceCompany.id)}/account/send_invoice/documents/soa-customer-list.pdf", 'rb'))
        return response
