from django.conf import settings
from django.contrib.auth.models import User

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, TableStyle, PageBreak, Paragraph
from reportlab.platypus.tables import Table
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab import rl_config
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image
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

def soaCustomerPdf(sourceCompanyId, userId):
    sourceCompany = SourceCompany.objects.filter(id = sourceCompanyId).first()
    user = User.objects.filter(id = userId).first()

    path = os.path.join(os.getcwd(), "media", "docs", str(sourceCompanyId), "account", "send_invoice", "documents")
    fileName = "soa-customer-list.pdf"
    logo = Image.open(os.path.join(os.getcwd(),"media","source","companies",str(sourceCompanyId),str(sourceCompany.documentLogo.name.split('/')[-1])))

    p, w, h = pdf_settings(path,fileName)
    defaultStyle, itemsTableStyleLeft, partsTableStyleLeftZero, partsTableStyleLeft, partsTableStyleLeftNoTitle, partsTableStyleLeftBasic, partsTableStyleCustomer, partsTableStyleSupplier, totalTableStyle = pdf_table_styles()
    totalData = total_customer_soa(sourceCompany)
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.fontSize = 6

    headerHeight = 100
    footerHeight = 110
    contentHeight = h - headerHeight - footerHeight
    #print(f"mm: {mm}, header: {headerHeight}, contentHeight: {contentHeight}")

    pdf_header(p,w,h,headerHeight,logo)
    pdf_footer(p,w,h,footerHeight,sourceCompany)

    def draw_title_table(p, invoiceData, yPosition):
        table = Table(invoiceData,colWidths=[((w-60)/100)*100], rowHeights=14)
        table.setStyle(partsTableStyleCustomer)

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
        table.setStyle(partsTableStyleLeft) if key == 0 else table.setStyle(partsTableStyleLeftBasic)

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

    companies = Company.objects.filter(sourceCompany = sourceCompany, send_invoice_customer__isnull = False).distinct()
    
    channel_layer = get_channel_layer()
    seq = 0
    for company in companies:
        async_to_sync(channel_layer.group_send)(
            'private_' + str(userId),
            {
                "type": "send_percent",
                "message": {"seq":seq,"version":""},
                "location" : "soa_send_invoice_pdf",
                "totalCount" : len(companies),
                "ready" : "false"
            }
        )

        invoices = company.send_invoice_customer.filter(payed = False)
        if invoices:
            invoiceData = [[company.name]]
            yPosition = draw_title_table(p, invoiceData, yPosition)
            yPosition -= 10

        billings = Billing.objects.filter(sourceCompany = sourceCompany, vessel__isnull=False, vessel__company = company, send_invoice_billing__isnull = False).order_by("name").distinct()
        vessels = Vessel.objects.filter(sourceCompany = sourceCompany, company = company, send_invoice_vessel__isnull = False).order_by("name").distinct()

        vesselOnlyInvoices = invoices.filter(billing__isnull=True, vessel__isnull=False)
        bothEmptyInvoices = invoices.filter(billing__isnull=True, vessel__isnull=True)

        for billing in billings:
            if billings.exists():
                billingInvoices = invoices.filter(sourceCompany = sourceCompany, billing = billing)
                currencyList = billingInvoices.values_list('currency__code', flat=True).distinct()
                
                for key, currency in enumerate(currencyList):
                    if key == 0:
                        invoiceData = [[billing.name]]
                        invoiceData.append(["Vessel", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"])
                        totalBalancePrice = 0
                        for invoice in billingInvoices.filter(currency__code = currency):
                            invoiceData.append([invoice.vessel.name, invoice.orderConfirmation.project.projectNo if invoice.orderConfirmation else invoice.offer.offerNo if invoice.offer else "", pdf_sub_line(invoice.sendInvoiceNo, 16), invoice.sendInvoiceDate, invoice.paymentDate, round_price(invoice.totalPrice), round_price(invoice.paidPrice), round_price(invoice.totalPrice - invoice.paidPrice), invoice.currency.code])
                            totalBalancePrice += (invoice.totalPrice - invoice.paidPrice)

                        invoiceData.append(["", "", "", "", "", "","Total", round_price(totalBalancePrice), currency])

                        yPosition = draw_invoices_table(p, invoiceData, yPosition, key)
                    else:
                        invoiceData = []
                        totalBalancePrice = 0
                        for invoice in billingInvoices.filter(currency__code = currency):
                            invoiceData.append([invoice.vessel.name, invoice.orderConfirmation.project.projectNo if invoice.orderConfirmation else invoice.offer.offerNo if invoice.offer else "", pdf_sub_line(invoice.sendInvoiceNo, 16), invoice.sendInvoiceDate, invoice.paymentDate, round_price(invoice.totalPrice), round_price(invoice.paidPrice), round_price(invoice.totalPrice - invoice.paidPrice), invoice.currency.code])
                            totalBalancePrice += (invoice.totalPrice - invoice.paidPrice)

                        invoiceData.append(["", "", "", "", "", "","Total", round_price(totalBalancePrice), currency])

                        yPosition = draw_invoices_table(p, invoiceData, yPosition, key)
                    
                yPosition -= 10

        for vessel in vessels:
            if vessels.exists():
                vesselInvoices = invoices.filter(sourceCompany = sourceCompany, vessel = vessel, billing__isnull = True)
                if vesselInvoices:
                    currencyList = vesselInvoices.values_list('currency__code', flat=True).distinct()
                
                    for key, currency in enumerate(currencyList):
                        if key == 0:
                            invoiceData = [[""]]
                            invoiceData.append(["Vessel", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"])
                            totalBalancePrice = 0
                            for invoice in vesselInvoices.filter(currency__code = currency):
                                invoiceData.append([invoice.vessel.name, invoice.orderConfirmation.project.projectNo if invoice.orderConfirmation else invoice.offer.offerNo if invoice.offer else "", pdf_sub_line(invoice.sendInvoiceNo, 16), invoice.sendInvoiceDate, invoice.paymentDate, round_price(invoice.totalPrice), round_price(invoice.paidPrice), round_price(invoice.totalPrice - invoice.paidPrice), invoice.currency.code])
                                totalBalancePrice += (invoice.totalPrice - invoice.paidPrice)

                            invoiceData.append(["", "", "", "", "", "","Total", round_price(totalBalancePrice), currency])

                            yPosition = draw_invoices_table(p, invoiceData, yPosition, key)
                        else:
                            invoiceData = []
                            totalBalancePrice = 0
                            for invoice in vesselInvoices.filter(currency__code = currency):
                                invoiceData.append([invoice.vessel.name, invoice.orderConfirmation.project.projectNo if invoice.orderConfirmation else invoice.offer.offerNo if invoice.offer else "", pdf_sub_line(invoice.sendInvoiceNo, 16), invoice.sendInvoiceDate, invoice.paymentDate, round_price(invoice.totalPrice), round_price(invoice.paidPrice), round_price(invoice.totalPrice - invoice.paidPrice), invoice.currency.code])
                                totalBalancePrice += (invoice.totalPrice - invoice.paidPrice)

                            invoiceData.append(["", "", "", "", "", "","Total", round_price(totalBalancePrice), currency])

                            yPosition = draw_invoices_table(p, invoiceData, yPosition, key)
                        
                    yPosition -= 10

        if not billings.exists() and not vessels.exists():
            emptyBillingAndVesselInvoices = invoices.filter(sourceCompany = sourceCompany, vessel__isnull = True, billing__isnull = True)
            if emptyBillingAndVesselInvoices:

                currencyList = emptyBillingAndVesselInvoices.values_list('currency__code', flat=True).distinct()
                
                for key, currency in enumerate(currencyList):
                    if key == 0:
                        invoiceData = [[""]]
                        invoiceData.append(["Vessel", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"])
                        totalBalancePrice = 0
                        for invoice in emptyBillingAndVesselInvoices.filter(currency__code = currency):
                            invoiceData.append(["", invoice.orderConfirmation.project.projectNo if invoice.orderConfirmation else invoice.offer.offerNo if invoice.offer else "", pdf_sub_line(invoice.sendInvoiceNo, 16), invoice.sendInvoiceDate, invoice.paymentDate, round_price(invoice.totalPrice), round_price(invoice.paidPrice), round_price(invoice.totalPrice - invoice.paidPrice), invoice.currency.code])
                            totalBalancePrice += (invoice.totalPrice - invoice.paidPrice)

                        invoiceData.append(["", "", "", "", "", "","Total", round_price(totalBalancePrice), currency])

                        yPosition = draw_invoices_table(p, invoiceData, yPosition, key)
                    else:
                        invoiceData = []
                        totalBalancePrice = 0
                        for invoice in emptyBillingAndVesselInvoices.filter(currency__code = currency):
                            invoiceData.append(["", invoice.orderConfirmation.project.projectNo if invoice.orderConfirmation else invoice.offer.offerNo if invoice.offer else "", pdf_sub_line(invoice.sendInvoiceNo, 16), invoice.sendInvoiceDate, invoice.paymentDate, round_price(invoice.totalPrice), round_price(invoice.paidPrice), round_price(invoice.totalPrice - invoice.paidPrice), invoice.currency.code])
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
    invoiceData.append(["CURRENCY", "AMOUNT", "TOTAL PAYMENT", "BALANCE"])
    invoiceData.append(["USD", totalData[0]["USD"]["total"],totalData[0]["USD"]["paid"],totalData[0]["USD"]["balance"]])
    invoiceData.append(["EUR", totalData[0]["EUR"]["total"],totalData[0]["EUR"]["paid"],totalData[0]["EUR"]["balance"]])
    invoiceData.append(["GBP", totalData[0]["GBP"]["total"],totalData[0]["GBP"]["paid"],totalData[0]["GBP"]["balance"]])
    invoiceData.append(["QAR", totalData[0]["QAR"]["total"],totalData[0]["QAR"]["paid"],totalData[0]["QAR"]["balance"]])
    invoiceData.append(["RUB", totalData[0]["RUB"]["total"],totalData[0]["RUB"]["paid"],totalData[0]["RUB"]["balance"]])
    invoiceData.append(["JPY", totalData[0]["JPY"]["total"],totalData[0]["JPY"]["paid"],totalData[0]["JPY"]["balance"]])
    invoiceData.append(["TRY", totalData[0]["TRY"]["total"],totalData[0]["TRY"]["paid"],totalData[0]["TRY"]["balance"]])
    
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
            "location" : "soa_send_invoice_pdf",
            "totalCount" : companiesCount,
            "ready" : "true"
        }
    )