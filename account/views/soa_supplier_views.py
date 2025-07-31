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
from ..pdfs.soa_supplier_pdfs import *


import random
import string
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Border, Side

class SOAIncomingInvoiceFilterExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Incoming Invoice Excel")
        
        elementTag = "soaIncomingInvoiceExcel"
        elementTagSub = "soaIncomingInvoicePartExcel"
        
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
        
        return render(request, 'account/soa_incoming_invoice_excel.html', context)       

class SOAIncomingInvoiceExportExcelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "account", "incoming_invoice", "documents")
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
        
        incomingInvoiceExcludeTypes = []
        
        if request.GET.get("o") == "false":
            incomingInvoiceExcludeTypes.append("order")
            
        if request.GET.get("pu") == "false":
            incomingInvoiceExcludeTypes.append("purchasing")
        
        suppliers = request.GET.get("c")
        
        if request.GET.get("p") == "true":
            incomingInvoices = IncomingInvoice.objects.select_related("seller").exclude(group__in=incomingInvoiceExcludeTypes).filter(
                sourceCompany = request.user.profile.sourceCompany,
                payed=True,incomingInvoiceDate__range=(startDate,endDate)
            ).order_by("incomingInvoiceDate").distinct().annotate(num_projects=Count('project')).order_by('seller__name', '-num_projects', 'project')
        elif request.GET.get("np") == "true":
            incomingInvoices = IncomingInvoice.objects.select_related("seller").exclude(group__in=incomingInvoiceExcludeTypes).filter(
                sourceCompany = request.user.profile.sourceCompany,
                payed=False,incomingInvoiceDate__range=(startDate,endDate)
            ).order_by("incomingInvoiceDate").distinct().annotate(num_projects=Count('project')).order_by('seller__name', '-num_projects', 'project')
        else:
            incomingInvoices = IncomingInvoice.objects.select_related("seller").exclude(group__in=incomingInvoiceExcludeTypes).filter(
                sourceCompany = request.user.profile.sourceCompany,
                incomingInvoiceDate__range=(startDate,endDate)
            ).order_by("incomingInvoiceDate").annotate(num_projects=Count('project')).order_by('seller__name', '-num_projects', 'project')
        
        if suppliers:
            suppliers = suppliers.split(",")
            incomingInvoices = incomingInvoices.filter(
                sourceCompany = request.user.profile.sourceCompany,
                seller__id__in=suppliers
            ).order_by("seller__name").annotate(num_projects=Count('project')).order_by('seller__name', '-num_projects', 'project')
        
        
        data = {
            "Supplier": [],
            "PO": [],
            "Invoice No": [],
            "Project No": [],
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
        for incomingInvoice in incomingInvoices:
            async_to_sync(channel_layer.group_send)(
                'private_' + str(request.user.id),
                {
                    "type": "send_percent",
                    "message": seq,
                    "location" : "soa_incoming_invoice_excel",
                    "totalCount" : len(incomingInvoices),
                    "ready" : "false"
                }
            )
            
            if incomingInvoice.project:
                project = incomingInvoice.project.projectNo
            elif incomingInvoice.purchasingProject:
                project = incomingInvoice.purchasingProject.projectNo
            else:
                project  = ""
            
            if incomingInvoice.seller:
                supplier = incomingInvoice.seller.name
            else:
                supplier = ""
                
            if incomingInvoice.purchaseOrder:
                purchaseOrder = incomingInvoice.purchaseOrder.purchaseOrderNo
            elif incomingInvoice.purchasingPurchaseOrder:
                purchaseOrder = incomingInvoice.purchasingPurchaseOrder.purchaseOrderNo
            else:
                purchaseOrder = ""
                
            data["Supplier"].append(supplier)
            data["PO"].append(purchaseOrder)
            data["Invoice No"].append(incomingInvoice.incomingInvoiceNo)
            data["Project No"].append(project)
            data["Invoice Date"].append(str(incomingInvoice.incomingInvoiceDate.strftime("%d.%m.%Y")))
            data["Payment Date"].append(str(incomingInvoice.paymentDate.strftime("%d.%m.%Y")))
            data["Amount"].append(round(incomingInvoice.totalPrice,2))
            data["Total Payment"].append(round(incomingInvoice.paidPrice,2))
            data["Balance"].append(round(incomingInvoice.totalPrice - incomingInvoice.paidPrice,2))
            data["Currency"].append(incomingInvoice.currency.code)
            data["Exchange Rate"].append(incomingInvoice.exchangeRate)
            data["TRY Gross"].append(round(incomingInvoice.totalPrice * incomingInvoice.exchangeRate))
            seq = seq + 1

        # Verileri pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)

        # DataFrame'i Excel dosyasına dönüştür
        excel_dosyasi_adi = base_path + "/soa-supplier-list.xlsx"
        with pd.ExcelWriter(excel_dosyasi_adi, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='IncomingInvoice', index=False)
            # dfTo.to_excel(writer, sheet_name='IncomingInvoice', index=False)
            # emptyLines = 2  # Tablolar arasındaki boş satır sayısı
            # nextTableStartLine = len(dfTo.index) + emptyLines + 1
            # df.to_excel(writer, sheet_name='IncomingInvoice', startrow=nextTableStartLine, index=False)
        
        #df.to_excel(excel_dosyasi_adi, index=False)

        #stil düzeltme
        wb = load_workbook(base_path + "/soa-supplier-list.xlsx")
        ws = wb.active

        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        previous_supplier = None
        row_offset = 1
        for index, incomingInvoice in enumerate(incomingInvoices):
            print(incomingInvoice.seller)
            # Müşteri değişimini kontrol et
            current_row = index + row_offset
            if incomingInvoice.seller != previous_supplier:
                if previous_supplier is not None:
                    # Boş satır ekle
                    row_offset += 1
                    current_row = index + row_offset
                    ws.insert_rows(current_row)

            previous_supplier = incomingInvoice.seller

        wb.save(base_path + "/soa-supplier-list.xlsx")

        #stil düzeltme-end

        #pdf to excel
        # input_pdf = base_path + "/" + "SI-024-00000029.pdf"
        # output_pdf = base_path + "/" + "convert_pdf_to_xls.csv"

        # tabula.convert_into(input_pdf, output_pdf, output_format="csv")
        
        #pdf to excel-end
        
        if incomingInvoices:
            incomingInvoicesCount = len(incomingInvoices)
        else:
            incomingInvoicesCount = 0
        async_to_sync(channel_layer.group_send)(
            'private_' + str(request.user.id),
            {
                "type": "send_percent",
                "message": seq,
                "location" : "soa_incoming_invoice_excel",
                "totalCount" : incomingInvoicesCount,
                "ready" : "true"
            }
        )
        
        return HttpResponse(status=204)

class SOAIncomingInvoiceDownloadExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = FileResponse(open('./media/docs/' + str(request.user.profile.sourceCompany.id) + '/account/incoming_invoice/documents/soa-supplier-list.xlsx', 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename="all-quotations.xlsx"'
        
        return response
    




class SOAIncomingInvoiceFilterPdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Incoming Invoice Pdf")
        
        elementTag = "soaIncomingInvoicePdf"
        elementTagSub = "soaIncomingInvoicePartPdf"
        
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
        
        return render(request, 'account/soa_incoming_invoice_pdf.html', context)       

class SOAIncomingInvoiceExportPdfView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        base_path = os.path.join(os.getcwd(), "media", "docs", str(request.user.profile.sourceCompany.id), "account", "incoming_invoice", "documents")
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
        
        incomingInvoiceExcludeTypes = []
        
        if request.GET.get("o") == "false":
            incomingInvoiceExcludeTypes.append("order")
            
        if request.GET.get("s") == "false":
            incomingInvoiceExcludeTypes.append("purchasing")
        
        suppliers = request.GET.get("c")
        
        # if request.GET.get("p") == "true":
        #     incomingInvoices = IncomingInvoice.objects.select_related("seller").exclude(group__in=incomingInvoiceExcludeTypes).filter(
        #         sourceCompany = request.user.profile.sourceCompany,
        #         payed=True,incomingInvoiceDate__range=(startDate,endDate)
        #     ).order_by("incomingInvoiceDate").distinct().order_by('seller__name', 'incomingInvoiceDate')
        # elif request.GET.get("np") == "true":
        #     incomingInvoices = IncomingInvoice.objects.select_related("seller").exclude(group__in=incomingInvoiceExcludeTypes).filter(
        #         sourceCompany = request.user.profile.sourceCompany,
        #         payed=False,incomingInvoiceDate__range=(startDate,endDate)
        #     ).order_by("incomingInvoiceDate").distinct().order_by('seller__name', 'incomingInvoiceDate')
        # else:
        #     incomingInvoices = IncomingInvoice.objects.select_related("seller").exclude(group__in=incomingInvoiceExcludeTypes).filter(
        #         sourceCompany = request.user.profile.sourceCompany,
        #         incomingInvoiceDate__range=(startDate,endDate)
        #     ).order_by("incomingInvoiceDate").order_by('seller__name', 'incomingInvoiceDate')
        
        # if suppliers:
        #     suppliers = suppliers.split(",")
        #     incomingInvoices = incomingInvoices.filter(
        #         sourceCompany = request.user.profile.sourceCompany,
        #         seller__id__in=suppliers
        #     ).order_by('seller__name', 'incomingInvoiceDate')
        
        
        soaSupplierPdf(request.user.profile.sourceCompany.id, request.user.id)
        
        # channel_layer = get_channel_layer()
        
        # seq = 0
        # for incomingInvoice in incomingInvoices:
        #     async_to_sync(channel_layer.group_send)(
        #         'private_' + str(request.user.id),
        #         {
        #             "type": "send_percent",
        #             "message": {"seq":seq,"version":""},
        #             "location" : "soa_incoming_invoice_pdf",
        #             "totalCount" : len(incomingInvoices),
        #             "ready" : "false"
        #         }
        #     )
            
        #     if incomingInvoice.theRequest:
        #         project = incomingInvoice.theRequest.requestNo
        #     elif incomingInvoice.purchasingProject:
        #         project = incomingInvoice.purchasingProject.projectNo
        #     else:
        #         project  = ""
            
        #     if incomingInvoice.seller:
        #         supplier = incomingInvoice.seller.name
        #     else:
        #         supplier = ""
            
        #     seq = seq + 1

        
        # if incomingInvoices:
        #     incomingInvoicesCount = len(incomingInvoices)
        # else:
        #     incomingInvoicesCount = 0

        # characters = string.ascii_letters + string.digits
        # version = ''.join(random.choice(characters) for _ in range(10))

        # async_to_sync(channel_layer.group_send)(
        #     'private_' + str(request.user.id),
        #     {
        #         "type": "send_percent",
        #         "message": {"seq":seq,"version":version},
        #         "location" : "soa_incoming_invoice_pdf",
        #         "totalCount" : incomingInvoicesCount,
        #         "ready" : "true"
        #     }
        # )
        
        return HttpResponse(status=204)

class SOAIncomingInvoiceDownloadPdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = FileResponse(open(f"./media/docs/{str(request.user.profile.sourceCompany.id)}/account/incoming_invoice/documents/soa-supplier-list.pdf", 'rb'))
        return response
