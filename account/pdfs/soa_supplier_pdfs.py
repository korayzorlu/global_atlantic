from django.conf import settings
from django.contrib.auth.models import User

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, TableStyle, PageBreak
from reportlab.platypus.tables import Table
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab import rl_config

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.db.models import Count

import os
import io
import shutil
from django.utils import timezone
from datetime import datetime
from decimal import Decimal

import logging
import random
import string

from ..models import SendInvoice, IncomingInvoice, ProformaInvoiceExpense,ProformaInvoiceItem, SendInvoicePart, SendInvoiceExpense,SendInvoiceItem,CommericalInvoice,CommericalInvoiceItem,CommericalInvoiceExpense
from card.models import EnginePart, Vessel, Billing, Company
from sale.models import QuotationPart
from source.models import Company as SourceCompany

from ..utils.pdf_utils import *
from ..utils.account_utils import *

from PIL import Image

def soaSupplierPdf(sourceCompanyId, userId):
    sourceCompany = SourceCompany.objects.filter(id = sourceCompanyId).first()
    user = User.objects.filter(id = userId).first()

    path = os.path.join(os.getcwd(), "media", "docs", str(sourceCompanyId), "account", "incoming_invoice", "documents")
    fileName = "soa-supplier-list.pdf"
    logo = Image.open(os.path.join(os.getcwd(),"media","source","companies",str(sourceCompanyId),str(sourceCompany.documentLogo.name.split('/')[-1])))

    p, w, h = pdf_settings(path,fileName)
    defaultStyle, itemsTableStyleLeft, partsTableStyleLeftZero, partsTableStyleLeft, partsTableStyleLeftNoTitle, partsTableStyleLeftBasic, partsTableStyleCustomer, partsTableStyleSupplier, totalTableStyle = pdf_table_styles()
    totalData = total_supplier_soa(sourceCompany)

    headerHeight = 100
    footerHeight = 110
    contentHeight = h - headerHeight - footerHeight
    #print(f"mm: {mm}, header: {headerHeight}, contentHeight: {contentHeight}")

    pdf_header(p,w,h,headerHeight,logo)
    pdf_footer(p,w,h,footerHeight,sourceCompany)

    def draw_title_table(p, invoiceData, yPosition):
        table = Table(invoiceData,colWidths=[((w-60)/100)*100], rowHeights=14)
        table.setStyle(partsTableStyleSupplier)

        tableHeight = sum(table._rowHeights)
        if yPosition - tableHeight < footerHeight:
            p.showPage()
            pdf_header(p,w,h,headerHeight,logo)
            pdf_footer(p,w,h,footerHeight,sourceCompany)
            yPosition = h - headerHeight

        table.wrapOn(p, w, contentHeight)
        table.drawOn(p, 30, yPosition - tableHeight)

        return yPosition - tableHeight

    def draw_invoices_table(p, invoiceData, yPosition, key=None):
        table = Table(invoiceData,colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
        table.setStyle(partsTableStyleLeftNoTitle) if key == 0 else table.setStyle(partsTableStyleLeftBasic)

        table.wrapOn(p, 30, -99999999)
        table.drawOn(p, 30, -99999999)
        
        tableHeight = sum(table._rowHeights)
        if yPosition - tableHeight < footerHeight:
            p.showPage()
            pdf_header(p,w,h,headerHeight,logo)
            pdf_footer(p,w,h,footerHeight,sourceCompany)
            yPosition = h - headerHeight

        table.wrapOn(p, w, contentHeight)
        table.drawOn(p, 30, yPosition - tableHeight)

        return yPosition - tableHeight

    def draw_total_table(p, invoiceData, yPosition):
        table = Table(invoiceData,colWidths=[((w-60)/100)*12,((w-60)/100)*12,((w-60)/100)*12,((w-60)/100)*12], rowHeights=12)
        table.setStyle(totalTableStyle)

        tableHeight = sum(table._rowHeights)
        if yPosition - tableHeight < footerHeight:
            p.showPage()
            pdf_header(p,w,h,headerHeight,logo)
            pdf_footer(p,w,h,footerHeight,sourceCompany)
            yPosition = h - headerHeight

        table.wrapOn(p, w, contentHeight)
        table.drawOn(p, 30, yPosition - tableHeight)

        return yPosition - tableHeight

    yPosition = h - headerHeight

    companies = Company.objects.filter(sourceCompany = sourceCompany, incoming_invoice_seller__isnull = False).distinct()
    
    channel_layer = get_channel_layer()
    seq = 0
    for company in companies:
        async_to_sync(channel_layer.group_send)(
            'private_' + str(userId),
            {
                "type": "send_percent",
                "message": {"seq":seq,"version":""},
                "location" : "soa_incoming_invoice_pdf",
                "totalCount" : len(companies),
                "ready" : "false"
            }
        )

        invoices = company.incoming_invoice_seller.filter(payed = False)
        if invoices:
            invoiceData = [[company.name]]
            yPosition = draw_title_table(p, invoiceData, yPosition)
            #yPosition -= 10
        
        currencyList = invoices.order_by('currency__code').values_list('currency__code', flat=True).distinct()
        #currencyList = Currency.objects.filter(incoming_invoice_currency__isnul = False).distinct()
        
        if invoices:
            for key, currency in enumerate(currencyList):
                if key == 0:
                    invoiceData = [["Purchase Order No", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"]]
                    totalBalancePrice = 0
                    for invoice in invoices.filter(currency__code = currency):
                        purchaseOrder = invoice.purchaseOrder.purchaseOrderNo if invoice.purchaseOrder else (invoice.purchasingPurchaseOrder.purchaseOrderNo if invoice.purchasingPurchaseOrder else "")
                        project = invoice.project.projectNo if invoice.project else (invoice.purchasingProject.projectNo if invoice.purchasingProject else "")

                        invoiceData.append([purchaseOrder, project, pdf_sub_line(invoice.incomingInvoiceNo, 16), invoice.incomingInvoiceDate, invoice.paymentDate, round_price(invoice.totalPrice), round_price(invoice.paidPrice), round_price(invoice.totalPrice - invoice.paidPrice), invoice.currency.code])
                        totalBalancePrice += (invoice.totalPrice - invoice.paidPrice)

                    invoiceData.append(["", "", "", "", "", "","Total", round_price(totalBalancePrice), currency])

                    yPosition = draw_invoices_table(p, invoiceData, yPosition, key)
                else:
                    invoiceData = []
                    totalBalancePrice = 0
                    for invoice in invoices.filter(currency__code = currency):
                        purchaseOrder = invoice.purchaseOrder.purchaseOrderNo if invoice.purchaseOrder else (invoice.purchasingPurchaseOrder.purchaseOrderNo if invoice.purchasingPurchaseOrder else "")
                        project = invoice.project.projectNo if invoice.project else (invoice.purchasingProject.projectNo if invoice.purchasingProject else "")

                        invoiceData.append([purchaseOrder, project, pdf_sub_line(invoice.incomingInvoiceNo, 16), invoice.incomingInvoiceDate, invoice.paymentDate, round_price(invoice.totalPrice), round_price(invoice.paidPrice), round_price(invoice.totalPrice - invoice.paidPrice), invoice.currency.code])
                        totalBalancePrice += (invoice.totalPrice - invoice.paidPrice)

                    invoiceData.append(["", "", "", "", "", "","Total", round_price(totalBalancePrice), currency])

                    yPosition = draw_invoices_table(p, invoiceData, yPosition, key)
                
            yPosition -= 10

        if yPosition < footerHeight:  # Sayfa dolduğunda yeni sayfaya geç
            p.showPage()
            pdf_header(p,w,h,headerHeight,logo)
            pdf_footer(p,w,h,footerHeight,sourceCompany)
            yPosition = h - headerHeight

        seq = seq + 1
        
    #pdf_footer(p,w,h,footerHeight,sourceCompany)

    remainingSpace = yPosition - footerHeight  # Toplam için gerekli boş alan

    if remainingSpace < 30:  # Eğer yer yoksa yeni sayfa ekleyelim
        p.showPage()
        pdf_header(p,w,h,headerHeight,logo)
        pdf_footer(p,w,h,footerHeight,sourceCompany)
        yPosition = h - headerHeight

    
    
    #####total table#####
    invoiceData = [["TOTAL"]]
    invoiceData.append(["CURRENCY", "BALANCE"])
    invoiceData.append(["USD", totalData[0]["USD"]["balance"]])
    invoiceData.append(["EUR", totalData[0]["EUR"]["balance"]])
    invoiceData.append(["GBP", totalData[0]["GBP"]["balance"]])
    invoiceData.append(["QAR", totalData[0]["QAR"]["balance"]])
    invoiceData.append(["RUB", totalData[0]["RUB"]["balance"]])
    invoiceData.append(["JPY", totalData[0]["JPY"]["balance"]])
    invoiceData.append(["TRY", totalData[0]["TRY"]["balance"]])
    
    yPosition = draw_total_table(p, invoiceData, yPosition)
    yPosition -= 10
    #####total table-end#####
    
    p.showPage()


    p.save()




    if companies:
        companiesCount = len(companies)
    else:
        companiesCount = 0

    characters = string.ascii_letters + string.digits
    version = ''.join(random.choice(characters) for _ in range(10))

    async_to_sync(channel_layer.group_send)(
        'private_' + str(userId),
        {
            "type": "send_percent",
            "message": {"seq":seq,"version":version},
            "location" : "soa_incoming_invoice_pdf",
            "totalCount" : companiesCount,
            "ready" : "true"
        }
    )
