from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, TableStyle, PageBreak, Frame, PageTemplate
from reportlab.platypus.tables import Table
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont   
from reportlab import rl_config
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import pica
from PIL import Image

from django.template.loader import render_to_string
#from weasyprint import HTML

from django.db.models import Count
from django.db.models import Q

import os
import io
import shutil
from django.utils import timezone
from datetime import datetime
import logging
from itertools import chain

from ..models import SendInvoice, IncomingInvoice, ProformaInvoiceExpense,ProformaInvoiceItem, SendInvoicePart, SendInvoiceExpense,SendInvoiceItem,CommericalInvoice,CommericalInvoiceItem,CommericalInvoiceExpense
from card.models import EnginePart, Vessel, Billing, Company
from sale.models import QuotationPart,Delivery
from source.models import Bank as SourceBank
from source.models import Company as SourceCompany

from ..utils.pdf_utils import *
from ..utils.account_utils import *

def sendInvoicePdff(theRequest, orderConfirmation, offer, sendInvoice, delivery, sourceCompany):
    logger = logging.getLogger("django")
    try:
        if sourceCompany.formalName:
            sourceCompanyFormalName = sourceCompany.formalName
        else:
            sourceCompanyFormalName = ""
        if sourceCompany.address:
            sourceCompanyAddress = sourceCompany.address
        else:
            sourceCompanyAddress = ""
        if sourceCompany.phone1:
            sourceCompanyPhone = sourceCompany.phone1
        else:
            sourceCompanyPhone = ""
        if sourceCompany.fax:
            sourceCompanyFax = sourceCompany.fax
        else:
            sourceCompanyFax = ""
            
        ##### bank list #####
        filterList = ["USD","EUR","TRY"]
        isBanks = SourceBank.objects.select_related("currency").filter(
            (Q(company = sourceCompany, bankName__icontains='İŞ BANKASI') | Q(company = sourceCompany, bankName__icontains='TÜRKİYE İŞ BANKASI')) &
            Q(currency__code__in = filterList)
        )
        halkBanks= SourceBank.objects.select_related("currency").filter(
            (Q(company = sourceCompany, bankName__icontains='HALKBANK') | Q(company = sourceCompany, bankName__icontains='TÜRKİYE HALK BANKASI')) &
            Q(currency__code__in = filterList)
        )
        vakifBanks= SourceBank.objects.select_related("currency").filter(
            (Q(company = sourceCompany, bankName__icontains='VAKIFBANK') | Q(company = sourceCompany, bankName__icontains='TÜRKİYE VAKIFLAR BANKASI')) &
            Q(currency__code__in = filterList)
        )
        
        banksLength = max(len(isBanks),len(halkBanks),len(vakifBanks))
        banksLength = (banksLength * 10) + 10
        ##### bank list-end #####
            
        #quotation içerisindeki part listesi
        #qParts = orderConfirmation.quotation.quotationpart_set.select_related("inquiryPart")
        if sendInvoice.group == "order":
            qParts = QuotationPart.objects.filter(quotation = orderConfirmation.quotation).order_by("sequency")
        parts = SendInvoiceItem.objects.filter(invoice = sendInvoice)
        expenses = SendInvoiceExpense.objects.filter(invoice = sendInvoice)
        items = []
        for part in parts:
            if part.trDescription:
                description = str(part.description) + " - " + str(part.trDescription)
            else:
                description = str(part.description)
            items.append({"name":part.name,
                        "description" : description,
                        "quantity" : part.quantity,
                        "unit" : part.unit,
                        "unitPrice" : part.unitPrice,
                        "totalPrice" : part.totalPrice
                        })
        for expense in expenses:
            items.append({"name":expense.expense.code,
                        "description" : expense.expense.name,
                        "quantity" : expense.quantity,
                        "unit" : expense.unit,
                        "unitPrice" : expense.unitPrice,
                        "totalPrice" : expense.totalPrice
                        })
        partsSubTotal = 0
        partsTotal = 0
        for part in parts:
            partsSubTotal = partsSubTotal + part.totalPrice
            partsTotal = partsTotal + part.totalPrice
        for expense in expenses:
            partsSubTotal = partsSubTotal + expense.totalPrice
            partsTotal = partsTotal + expense.totalPrice
        discountTotal = partsTotal - partsSubTotal
        vatTotal = (partsSubTotal - discountTotal) * (sendInvoice.vat / 100)
        partsTotal = partsTotal + vatTotal
        
        partsTotalsDict = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0,"vatTotal":0,"totalGrand":0,"totalExpense":0}
            
        partsTotalDict = 0
        
        for part in parts:
            partsTotalDict  = partsTotalDict + part.totalPrice
            partsTotalsDict["totalUnitPrice1"] = partsTotalsDict["totalUnitPrice1"] + part.unitPrice
            partsTotalsDict["totalUnitPrice2"] = partsTotalsDict["totalUnitPrice2"] + part.unitPrice
            partsTotalsDict["totalUnitPrice3"] = partsTotalsDict["totalUnitPrice3"] + part.unitPrice
            partsTotalsDict["totalTotalPrice1"] = partsTotalsDict["totalTotalPrice1"] + part.totalPrice
            partsTotalsDict["totalTotalPrice2"] = partsTotalsDict["totalTotalPrice2"] + part.totalPrice
            partsTotalsDict["totalTotalPrice3"] = partsTotalsDict["totalTotalPrice3"] + part.totalPrice
            
        if sendInvoice.group == "order":
            if orderConfirmation.quotation.manuelDiscountAmount > 0:
                partsTotalsDict["totalDiscount"] = orderConfirmation.quotation.manuelDiscountAmount
            else:
                partsTotalsDict["totalDiscount"] = partsTotalsDict["totalTotalPrice3"] * (orderConfirmation.quotation.manuelDiscount/100)
        elif sendInvoice.group == "service":
            if offer.discountAmount > 0:
                partsTotalsDict["totalDiscount"] = offer.discountAmount
            else:
                partsTotalsDict["totalDiscount"] = partsTotalsDict["totalTotalPrice3"] * (offer.discount/100)
            
        for expense in expenses:
            partsTotalsDict["totalExpense"] = partsTotalsDict["totalExpense"] + expense.totalPrice
        
        partsTotalsDict["totalTotalPrice3"] = partsTotalsDict["totalTotalPrice3"] + partsTotalsDict["totalExpense"]
        partsTotalsDict["totalVat"] = (partsTotalsDict["totalTotalPrice3"] - partsTotalsDict["totalDiscount"]) * (sendInvoice.vat/100)
        partsTotalsDict["totalFinal"] = partsTotalsDict["totalTotalPrice3"] - partsTotalsDict["totalDiscount"] + partsTotalsDict["totalVat"]
        
        
        #standart ayar
        buffer = io.BytesIO()
        
        #dosyanın kaydedileceği konum
        folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "account", "send_invoice", "documents")
        
        #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        
        #font ayarları
        rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
        pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
        
        #standart ayar
        p = canvas.Canvas(folderPath + "/" + sendInvoice.sendInvoiceNoSys + ".pdf", pagesize = A4)
        
        #standart ayar
        w, h = A4
        
        ystart = 780
        
        #tablo satır yükseklikleri
        tableRowHeight = 13
        partsTableRowHeight = 13
        
        #tablo stilleri
        tableLeftStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                                ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                                ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                ('BACKGROUND',(0,0), (-1,-1), "#c7d3e1")
                                ])
        tableRightStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                                ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                ])
        tableRightStyleBold = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                                ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                                ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                ])
        
        #?
        p.setLineWidth(0.5)
        
        #logo
        #esmsImg = Image.open(os.path.join(os.getcwd(), "static", "images", "esms-logo2.jpg"))
        esmsImg = Image.open(os.path.join(os.getcwd(),"media","source","companies",str(sourceCompany.id),str(sourceCompany.documentLogo.name.split('/')[-1])))
        signImg = Image.open(os.path.join(os.getcwd(), "static", "images", "account", "sign", "esms-sign.jpg"))
        #vessel yazısı
        # p.setFillColor(HexColor("#000"))
        # p.setFont('Inter-Bold', 7)
        # p.drawString(35, h-170, "TO")
        # p.setFont('Inter', 7)
        # p.drawString(50, h-170, ":" + theRequest.customer.name)
        
        #imo
        # p.setFillColor(HexColor("#000"))
        # p.setFont('Inter-Bold', 7)
        # p.drawString(35, h-170, "TO")
        # p.setFont('Inter', 7)
        # p.drawString(50, h-170, ":" + theRequest.customer.name)
        
        #test yazısı
        # p.setFont('Inter', 16)
        # p.setFillColor(HexColor("#922724"))
        # p.drawCentredString(w/2, h-95, "TEST FATURASIDIR KULLANMAYINIZ")
        p.setFillColor(HexColor("#000"))
        
        #####sol üst tablo#####
        #company
        vessel = sendInvoice.vessel
        if vessel:
            vesselName = str(vessel.get_type_display()) + " " + str(vessel.name) + " - IMO No: " + str(vessel.imo)
        else:
            vesselName = ""
            
        if sendInvoice.billing:
            billingName = sendInvoice.billing.name
            if sendInvoice.billing.address:
                billingAddress = sendInvoice.billing.address
                if sendInvoice.billing.city:
                    billingCity = sendInvoice.billing.city.name
                    billingAddress = billingAddress + " " + billingCity + " /"
                if sendInvoice.billing.country:
                    billingCountry = sendInvoice.billing.country.international_formal_name
                    billingAddress = billingAddress + " " + billingCountry
            else:
                billingAddress = ""
                if sendInvoice.billing.city:
                    billingCity = sendInvoice.billing.city.name
                    billingAddress = billingAddress + " " + billingCity + " /"
                if sendInvoice.billing.country:
                    billingCountry = sendInvoice.billing.country.international_formal_name
                    billingAddress = billingAddress + " " + billingCountry
        else:    
            billingName = ""
            billingAddress = ""
            
        p.setFillColor(HexColor("#000"))
        p.setFont('Inter-Bold', 6)
        p.drawString(35, h-100, "ALICI / BUYER")
        p.setFont('Inter', 6)
        p.drawString(80, h-100, ": " + vesselName)
        p.drawString(35, h-110, billingName)
        
        #####billing address with multiple lines#####
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        newBillingAddress = ""
        for i in range(0, len(billingAddress), 75):
            chunk = billingAddress[i:i+75]
            space_index = chunk.rfind(' ')
            if space_index != -1:
                newBillingAddress += chunk[:space_index] + '\n'
                if space_index + 1 < len(chunk):
                    newBillingAddress += chunk[space_index+1:]
            else:
                newBillingAddress += chunk
        #alt satır komutu
        lines = newBillingAddress.replace("\r\n", "\n")
        lines = lines.split('\n')
        line_height = 10  # İsteğe bağlı, satır yüksekliği
        current_y = h-120

        for line in lines:
            p.drawString(35, current_y, line)
            current_y = current_y - line_height
        #####billing address with multiple lines-end#####
        
        #####billing address with multiple lines#####
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        newCustomerName = ""
        for i in range(0, len(sendInvoice.customer.name), 75):
            chunk = sendInvoice.customer.name[i:i+75]
            if len(chunk) < 75:
                newCustomerName += chunk
            else:
                space_index = chunk.rfind(' ')
                if space_index != -1:
                    newCustomerName += chunk[:space_index] + '\n'
                    if space_index + 1 < len(chunk):
                        newCustomerName += chunk[space_index+1:]
                else:
                    newCustomerName += chunk
        #alt satır komutu
        lines = newCustomerName.replace("\r\n", "\n")
        lines = lines.split('\n')
        line_height = 10  # İsteğe bağlı, satır yüksekliği
        current_y = current_y
        p.drawString(35, current_y, "c/o ")
        for key, line in enumerate(lines):
            if key == 0:
                p.drawString(35, current_y, "c/o " + str(line))
            else:
                p.drawString(35, current_y, line)
            current_y = current_y - line_height
        #####billing address with multiple lines-end#####
        
        p.setFont('Inter', 6)
        data=[("")]
        table = Table(data, colWidths=w/2-35, rowHeights=tableRowHeight*6)
        table.setStyle(TableStyle([
                                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                                ]))
        
        table.wrapOn(p, 30, h-167)
        table.drawOn(p, 30, h-167)
        #####sol üst tablo-end#####
        
        #####sağ üst tablo#####
            
        p.setFillColor(HexColor("#000"))
        p.setFont('Inter-Bold', 6)
        p.drawString(w/2+10, h-100, "TESLİMAT ADRESİ / DELIVERY ADDRESS")
        p.setFont('Inter', 6)
        #p.drawString(w/2+10, h-140, delivery.address)
        
        # Her bir satırı ayrı bir drawText çağrısı ile ekleyelim
        if delivery:
            if delivery.address:
                lines = delivery.address.replace("\r\n", "\n")
                lines = lines.split('\n')
                line_height = 10  # İsteğe bağlı, satır yüksekliği
                current_y = h-110

                for line in lines:
                    p.drawString(w/2+10, current_y, line)
                    current_y = current_y - line_height
            else:
                p.drawString(w/2+10, h-110, "")
        else:
            p.drawString(w/2+10, h-110, "")
        
        p.setFont('Inter', 6)
        data=[("")]
        table = Table(data, colWidths=w/2-35, rowHeights=tableRowHeight*6)
        table.setStyle(TableStyle([
                                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                                ]))
        
        table.wrapOn(p,  w/2+5, h-167)
        table.drawOn(p,  w/2+5, h-167)
        #####sağ üst tablo-end#####
        
        #####sol alt tablo#####
        data=[["PROJE NO / PROJECT NO"],
            ["SİPARİŞ TARİHİ / ORDER DATE"],
            ["TESLİMAT ŞEKLİ / DELİVERY TYPE"],
            ["TESLİMAT NO / DELİVERY NO"]
            ]
        table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight)
        table.setStyle(tableLeftStyle)
        
        table.wrapOn(p, 30, h-229)
        table.drawOn(p, 30, h-229)
        
        if sendInvoice.vessel:
            imo = sendInvoice.vessel.imo
        else:
            imo = ""
        if delivery:
            trackingNo = delivery.trackingNo
        else:
            trackingNo = ""
        
        if sendInvoice.group == "order":
            data=[[theRequest.requestNo],
                [orderConfirmation.orderConfirmationDate.strftime("%d.%m.%Y")],
                [orderConfirmation.quotation.delivery],
                [trackingNo]
                ]
        elif sendInvoice.group == "service":
            data=[[offer.offerNo],
                [offer.offerDate.strftime("%d.%m.%Y")],
                [offer.deliveryMethod],
                [""]
                ]
        else:
            data=["",
                "",
                ""
                ""
                ]
        table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight)
        table.setStyle(tableRightStyle)
        
        table.wrapOn(p, 30+((w/2-35)/2), h-229)
        table.drawOn(p, 30+((w/2-35)/2), h-229)
        #####sol alt tablo-end#####
        
        #####sağ alt tablo#####
        data=[["MAKER"],
            ["TİP / TYPE"],
            ["MÜŞTERİ REF / CUSTOMER REF"],
            ["ÖDEME ŞEKLİ / PAYMENT TERM"]
            ]
        table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight)
        table.setStyle(tableLeftStyle)
        
        table.wrapOn(p, w/2+5, h-229)
        table.drawOn(p, w/2+5, h-229)
        
        if sendInvoice.vessel:
            vessel = sendInvoice.vessel
        else:
            vessel = ""
        
        if sendInvoice.group == "order":
            if theRequest.maker:
                maker = theRequest.maker
            else:
                maker = ""
            if theRequest.makerType:
                makerType = theRequest.makerType
            else:
                makerType = ""
                
            data=[[maker],
                [makerType],
                [theRequest.customerRef],
                [orderConfirmation.quotation.payment]
            ]
        elif sendInvoice.group == "service":
            if offer.equipment:
                maker = offer.equipment.maker
            else:
                maker = ""
            if offer.equipment:
                makerType = offer.equipment.makerType
            else:
                makerType = ""
            
            data=[[maker],
                [makerType],
                [offer.customerRef],
                [offer.paymentType]
            ]
        
        table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight)
        table.setStyle(tableRightStyle)
        
        table.wrapOn(p, (w/2+5)+((w/2-35)/2), h-229)
        table.drawOn(p, (w/2+5)+((w/2-35)/2), h-229)
        #####sağ alt tablo-end#####
        
        #####parça sayısına göre sayfa dilimleme#####
        #standart ayar
        slice = int(42 - ((banksLength - 10) / 10))
        
        pageNum = 1
        pageCount = len(items) // slice
        #standart ayar
        if len(items) % slice != 0:
            pageCount = pageCount + 1
            
        
            
        #standart ayar
        for i in range(0, len(items), slice):
            #standart ayar
            partsList = items[i:i+slice]
            #standart ayar
            p.drawInlineImage(esmsImg, 30, ystart, width=(esmsImg.size[0]/esmsImg.size[1])*40,height=40)
            #p.drawInlineImage(signImg, (w/2)-70, ystart-35, width=140,height=90)
            p.setFont('Inter-Bold', 7)
            #p.drawString(450, h-50, "DATE")
            p.setFont('Inter', 7)
            #p.drawString(480, h-50, ":" + str(inquiry.inquiryDate.strftime("%d.%m.%Y")))
            
            p.setFont('Inter-Bold', 7)
            #p.drawString(450, h-70, "REF NO")
            p.setFont('Inter', 7)
            #p.drawString(480, h-70, ":" + str(inquiry.inquiryNo))
            
            #####sağ üst yazılar#####
            invoiceTableStyleTitle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (0, 0), 'Inter-Bold', 9),
                                    ('FONT', (0, 1), (0, 1), 'Inter', 8),
                                    ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                                    ('VALIGN',(0,0),(-1,-1),'MIDDLE')
                                    ])
            
            data=[["FATURA / INVOICE"],
            [sendInvoice.sendInvoiceNo]
            ]
            table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight+5)
            table.setStyle(invoiceTableStyleTitle)
            
            table.wrapOn(p, (w/2+5)+((w/2-35)/2), h-60)
            table.drawOn(p, (w/2+5)+((w/2-35)/2), h-60)
            
            p.setFont('Inter-Bold', 6)
            p.drawString((w/2+5)+((w/2-35)/2), h-77, "TARİH: ")
            p.setFont('Inter', 6)
            p.drawString((w/2+5)+((w/2-35)/2)+30, h-77, str(sendInvoice.sendInvoiceDate.strftime("%d.%m.%Y")))
            #####sağ üst yazılar-end#####
            
            if i >= slice:
                th = h+150
            else:
                th = h
            
            #####parts tablo#####
            
            partsTableStyleLeft = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                    ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                    ('BACKGROUND',(0,0), (-1,0), "#c7d3e1")
                                    ])
            partsTableStyleLeftWhite = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                    ])
            partsTableStyleDescriptionLeftWhite = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                    ('LINEBELOW', (0,-1), (-1,-1), 0.1, "rgba(0,56,101,0.65)"),
                                    ])
            partsTableStyleRightWhite = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "RIGHT"),
                                    ])
            
            partsTableStyleRight = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                    ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "RIGHT"),
                                    ('BACKGROUND',(0,0), (-1,0), "#c7d3e1")
                                    ])
            
            partsTableStyleCenter = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                    ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                                    ('BACKGROUND',(0,0), (-1,0), "#c7d3e1")
                                    ])
            
            totalLeftTableStyleLeft = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                    ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                    ('BACKGROUND',(0,0), (-1,-1), "#c7d3e1")
                                    ])
            
            totalLeftTableStyleLeftTotal = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                    ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                    ('BACKGROUND',(0,0), (-1,-1), "#c7d3e1")
                                    ])
            
            totalRightTableStyleRight = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "RIGHT")
                                    ])
            
            totalRightTableStyleRightTotal = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "RIGHT")
                                    ])
            
            #sütun(tablo) 1
            data=[["Sıra\nItem"]]
            table = Table(data, colWidths=((w-60)/100)*5, rowHeights=(partsTableRowHeight*2)-5)
            table.setStyle(partsTableStyleLeft)
            
            table.wrapOn(p, 30, th-246-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30, th-246-(len(data)*partsTableRowHeight))
            table1Length = table._colWidths[0]
            
            data=[]
            for j in range(len(partsList)):
                data.append([j+i+1])
            table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
            table.setStyle(partsTableStyleLeftWhite)
            
            table.wrapOn(p, 30, th-259-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30, th-259-(len(data)*partsTableRowHeight))
            table1Length = table._colWidths[0]
            
            #sütun(tablo) 3
            data=[["Açıklama\nDescription"]]
            table = Table(data, colWidths=((w-60)/100)*59, rowHeights=(partsTableRowHeight*2)-5)
            table.setStyle(partsTableStyleCenter)
            
            table.wrapOn(p, 30+table1Length, th-246-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length, th-246-(len(data)*partsTableRowHeight))
            table3Length = table._colWidths[0]
            
            data=[]
            for part in partsList:
                data.append([part["name"]])
            table = Table(data, colWidths=((w-60)/100)*12, rowHeights=partsTableRowHeight)
            table.setStyle(partsTableStyleDescriptionLeftWhite)
            
            table.wrapOn(p, 30+table1Length, th-259-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length, th-259-(len(data)*partsTableRowHeight))
            table3Length = table._colWidths[0]
            
            #sütun(tablo) 4
            data=[]
            for part in partsList:
                data.append([part["description"]])
            table = Table(data, colWidths=((w-60)/100)*47, rowHeights=partsTableRowHeight)
            table.setStyle(partsTableStyleDescriptionLeftWhite)
            
            table.wrapOn(p, 30+table1Length+table3Length, th-259-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table3Length, th-259-(len(data)*partsTableRowHeight))
            table4Length = table._colWidths[0]
            
            #sütun(tablo) 4
            data=[["Adet\nQty"]]
            table = Table(data, colWidths=((w-60)/100)*5, rowHeights=(partsTableRowHeight*2)-5)
            partsTableStyleRight
            table.setStyle(partsTableStyleCenter)
            
            table.wrapOn(p, 30+table1Length+table3Length+table4Length, th-246-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table3Length+table4Length, th-246-(len(data)*partsTableRowHeight))
            table5Length = table._colWidths[0]
            
            data=[]
            for part in partsList:
                data.append([part["quantity"]])
            table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
            partsTableStyleRight
            table.setStyle(partsTableStyleLeftWhite)
            
            table.wrapOn(p, 30+table1Length+table3Length+table4Length, th-259-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table3Length+table4Length, th-259-(len(data)*partsTableRowHeight))
            table5Length = table._colWidths[0]
            
            #sütun(tablo) 5
            data=[["Birim\nUnit"]]
            table = Table(data, colWidths=((w-60)/100)*5, rowHeights=(partsTableRowHeight*2)-5)
            partsTableStyleRight
            table.setStyle(partsTableStyleCenter)
            
            table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length, th-246-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length, th-246-(len(data)*partsTableRowHeight))
            table6Length = table._colWidths[0]
            
            data=[]
            for part in partsList:
                data.append([part["unit"]])
            table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
            partsTableStyleRight
            table.setStyle(partsTableStyleLeftWhite)
            
            table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length, th-259-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length, th-259-(len(data)*partsTableRowHeight))
            table6Length = table._colWidths[0]
            
            #sütun(tablo) 6
            data=[["Birim Fiyatı\nUnit Price"]]
            table = Table(data, colWidths=((w-60)/100)*13, rowHeights=(partsTableRowHeight*2)-5, hAlign="RIGHT")
            table.setStyle(partsTableStyleCenter)
            
            table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length, th-246-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length, th-246-(len(data)*partsTableRowHeight))
            table7Length = table._colWidths[0]
            
            data=[]
            for part in partsList:
                # Para miktarını belirtilen formatta gösterme
                unitPrice3Fixed = "{:,.2f}".format(round(part["unitPrice"],2))
                # Nokta ile virgülü değiştirme
                unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                data.append([str(unitPrice3Fixed) + " " + sendInvoice.currency.code])
            table = Table(data, colWidths=((w-60)/100)*13, rowHeights=partsTableRowHeight, hAlign="RIGHT")
            table.setStyle(partsTableStyleRightWhite)
            
            table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length, th-259-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length, th-259-(len(data)*partsTableRowHeight))
            table7Length = table._colWidths[0]
            
            #sütun(tablo) 7
            data=[["Toplam Fiyat\nTotal Price"]]
            table = Table(data, colWidths=((w-60)/100)*13, rowHeights=(partsTableRowHeight*2)-5)
            table.setStyle(partsTableStyleCenter)
            
            table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length+table7Length, th-246-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length+table7Length, th-246-(len(data)*partsTableRowHeight))
            table8Length = table._colWidths[0]
            
            data=[]
            for part in partsList:
                # Para miktarını belirtilen formatta gösterme
                totalPrice3Fixed = "{:,.2f}".format(round(part["totalPrice"],2))
                # Nokta ile virgülü değiştirme
                totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                data.append([str(totalPrice3Fixed) + " " + sendInvoice.currency.code])
            table = Table(data, colWidths=((w-60)/100)*13, rowHeights=partsTableRowHeight)
            table.setStyle(partsTableStyleRightWhite)
            
            table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length+table7Length, th-259-(len(data)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length+table7Length, th-259-(len(data)*partsTableRowHeight))
            table8Length = table._colWidths[0]
            
            lenData = len(data)
            
            
            #sütun(tablo) total
            """
            if pageNum == pageCount:
                subTotalPrice = 0
                totalPrice = 0
                
                for part in parts:
                    subTotalPrice = subTotalPrice + part.totalPrice
                    totalPrice = totalPrice + part.totalPrice
                for expense in expenses:
                    subTotalPrice = subTotalPrice + expense.totalPrice
                    totalPrice = totalPrice + expense.totalPrice
                
                try:
                    discount = round(1-(totalPrice/subTotalPrice),2)
                except:
                    discount = 0
                    
                discountPrice  = round(subTotalPrice - totalPrice,2)
                
                # Para miktarını belirtilen formatta gösterme
                partsSubTotalFixed = "{:,.2f}".format(round(partsSubTotal,2))
                discountTotalFixed = "{:,.2f}".format(round(discountTotal,2))
                vatTotalFixed = "{:,.2f}".format(round(vatTotal,2))
                partsTotalFixed = "{:,.2f}".format(round(partsTotal,2))
                # Nokta ile virgülü değiştirme
                partsSubTotalFixed = partsSubTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                discountTotalFixed = discountTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                vatTotalFixed = vatTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                partsTotalFixed = partsTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

                vatRate = sendInvoice.vat
                
                if vatRate == 0:
                    vatText = "KDV / VAT"
                else:
                    if vatRate.is_integer():
                        vatText = "KDV " + str(int(vatRate)) + "% / VAT " + str(int(vatRate)) + "%"
                    else:
                        vatText = "KDV " + str(vatRate) + "% / VAT " + str(vatRate) + "%"
                
                dataSubTotal=[["ARA TOPLAM / SUB TOTAL"],
                            ["İSKONTO / DISCOUNT"],
                            [vatText],
                            ["TOPLAM / G.AMOUNT"]
                            ]
                table = Table(dataSubTotal, colWidths=((w-60)/100)*18, rowHeights=partsTableRowHeight)
                table.setStyle(totalLeftTableStyleLeftTotal)
                
                table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length, th-246-((len(data)+5)*partsTableRowHeight))
                table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length, th-246-((len(data)+5)*partsTableRowHeight))
                tableTotalLeftLength = table._colWidths[0]
                
                # Para miktarını belirtilen formatta gösterme
                totalTotalPrice3Fixed = "{:,.2f}".format(round(partsTotalsDict["totalTotalPrice3"],2))
                totalDiscountFixed = "{:,.2f}".format(round(partsTotalsDict["totalDiscount"],2))
                totalVatFixed = "{:,.2f}".format(round(partsTotalsDict["totalVat"],2))
                totalFinalFixed = "{:,.2f}".format(round(partsTotalsDict["totalFinal"],2))
                # Nokta ile virgülü değiştirme
                totalTotalPrice3Fixed = totalTotalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalDiscountFixed = totalDiscountFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalVatFixed = totalVatFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalFinalFixed = totalFinalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                
                dataSubTotal=[[str(totalTotalPrice3Fixed) + " " + orderConfirmation.quotation.currency.code],
                            [str(totalDiscountFixed) + " " + orderConfirmation.quotation.currency.code],
                            [str(totalVatFixed) + " " + orderConfirmation.quotation.currency.code],
                            [str(totalFinalFixed) + " " + orderConfirmation.quotation.currency.code]
                            ]
                table = Table(dataSubTotal, colWidths=((w-60)/100)*13, rowHeights=partsTableRowHeight)
                table.setStyle(totalRightTableStyleRightTotal)
                
                table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+tableTotalLeftLength, th-246-((len(data)+5)*partsTableRowHeight))
                table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+tableTotalLeftLength, th-246-((len(data)+5)*partsTableRowHeight))
                tableTotalLeftLength = table._colWidths[0]
            """
            #####parts tablo-end#####
            
            ######sayfa altı########
            p.setStrokeColor(HexColor("#808080"))
            p.line(30, 70, w-30, 70)
            p.setFont('Inter-Bold', 7)
            p.drawString(30, 60, sourceCompanyFormalName)
            p.drawString(30, 40, "Office")
            p.setFont('Inter', 7)
            p.drawString(60, 40, sourceCompanyAddress)
            #p.drawString(60, 70, "No:126 57/C P.K. 34947 Tuzla İstanbul TR")
            p.setFont('Inter-Bold', 7)
            p.drawString(30, 30, "Tel")
            p.setFont('Inter', 7)
            p.drawString(60, 30, sourceCompanyPhone)
            p.setFont('Inter-Bold', 7)
            p.drawString(30, 20, "Fax")
            p.setFont('Inter', 7)
            p.drawString(60, 20, sourceCompanyFax)
            
            lrImg = Image.open(os.path.join(os.getcwd(), "static", "images", "sale", "lr-logo4.jpg"))
            
            p.drawInlineImage(lrImg, 415, 16, width=150,height=50)
            
            ######sayfa altı-end########
            
            #####sayfa numarası#####
            # if len(parts) > slice:
            #     p.setFont('Inter', 7)
            #     p.drawCentredString(w/2, 10, str(pageNum) + "/" + str(pageCount))
            #     pageNum = pageNum + 1
            #####sayfa numarası-end#####
            
            #####sayfa numarası#####
            # if pageNum == pageCount:
            #     if len(partsList) > 29:
            #         p.setFont('Inter', 7)
            #         p.drawString(30, 75, "SAYFA / PAGE     " + str(pageNum) + " of " + str(pageCount))
            #         pageNum = pageNum + 1
            #     else:
            #         p.setFont('Inter', 7)
            #         p.drawString(30, 197, "SAYFA / PAGE     " + str(pageNum) + " of " + str(pageCount))
            #         pageNum = pageNum + 1
            # else:
            #     p.setFont('Inter', 7)
            #     #th-246-((lenData+2)*partsTableRowHeight)
            #     p.drawString(30, 75, "SAYFA / PAGE     " + str(pageNum) + " of " + str(pageCount) + "     CONTINUED")
            #     pageNum = pageNum + 1
            #####sayfa numarası-end#####
            
            if pageNum == pageCount:
                if len(items) == slice or len(items) % slice > 29:
                    pageCount = pageCount + 1
                    
                if len(partsList) > 29:
                    p.setFont('Inter', 7)
                    p.drawString(30, 75, "SAYFA / PAGE     " + str(pageNum) + " of " + str(pageCount) + "     CONTINUED")
                    pageNum = pageNum + 1
                else:
                    p.setFont('Inter', 7)
                    p.drawString(30, 157+banksLength, "SAYFA / PAGE     " + str(pageNum) + " of " + str(pageCount))
                    pageNum = pageNum + 1
                
                if len(partsList) > 29:
                    p.showPage()
                    
                    p.drawInlineImage(esmsImg, 30, ystart, width=(esmsImg.size[0]/esmsImg.size[1])*40,height=40)
                    #p.drawInlineImage(signImg, (w/2)-70, ystart-35, width=140,height=90)
                    p.setFont('Inter-Bold', 7)
                    #p.drawString(450, h-50, "DATE")
                    p.setFont('Inter', 7)
                    #p.drawString(480, h-50, ":" + str(inquiry.inquiryDate.strftime("%d.%m.%Y")))
                    
                    p.setFont('Inter-Bold', 7)
                    #p.drawString(450, h-70, "REF NO")
                    p.setFont('Inter', 7)
                    #p.drawString(480, h-70, ":" + str(inquiry.inquiryNo))
                    
                    #####sağ üst yazılar#####
                    invoiceTableStyleTitle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                            ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                            ('FONT', (0, 0), (0, 0), 'Inter-Bold', 9),
                                            ('FONT', (0, 1), (0, 1), 'Inter', 8),
                                            ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                                            ('VALIGN',(0,0),(-1,-1),'MIDDLE')
                                            ])
                    
                    data=[["FATURA / INVOICE"],
                    [sendInvoice.sendInvoiceNo]
                    ]
                    table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight+5)
                    table.setStyle(invoiceTableStyleTitle)
                    
                    table.wrapOn(p, (w/2+5)+((w/2-35)/2), h-60)
                    table.drawOn(p, (w/2+5)+((w/2-35)/2), h-60)
                    
                    p.setFont('Inter-Bold', 6)
                    p.drawString((w/2+5)+((w/2-35)/2), h-77, "TARİH: ")
                    p.setFont('Inter', 6)
                    p.drawString((w/2+5)+((w/2-35)/2)+30, h-77, str(sendInvoice.sendInvoiceDate.strftime("%d.%m.%Y")))
                    #####sağ üst yazılar-end#####
                
                    ######sayfa altı########
                    p.setStrokeColor(HexColor("#808080"))
                    p.line(30, 70, w-30, 70)
                    p.setFont('Inter-Bold', 7)
                    p.drawString(30, 60, sourceCompanyFormalName)
                    p.drawString(30, 40, "Office")
                    p.setFont('Inter', 7)
                    p.drawString(60, 40, sourceCompanyAddress)
                    #p.drawString(60, 70, "No:126 57/C P.K. 34947 Tuzla İstanbul TR")
                    p.setFont('Inter-Bold', 7)
                    p.drawString(30, 30, "Tel")
                    p.setFont('Inter', 7)
                    p.drawString(60, 30, sourceCompanyPhone)
                    p.setFont('Inter-Bold', 7)
                    p.drawString(30, 20, "Fax")
                    p.setFont('Inter', 7)
                    p.drawString(60, 20, sourceCompanyFax)
                    
                    lrImg = Image.open(os.path.join(os.getcwd(), "static", "images", "sale", "lr-logo4.jpg"))
                    
                    p.drawInlineImage(lrImg, 415, 16, width=150,height=50)
                    
                    ######sayfa altı-end########
                    
                    #####sayfa numarası#####
                    # if len(parts) > slice:
                    #     p.setFont('Inter', 7)
                    #     p.drawCentredString(w/2, 10, str(pageNum) + "/" + str(pageCount))
                    #     pageNum = pageNum + 1
                    #####sayfa numarası-end#####
                    
                    #####sayfa numarası#####
                    p.setFont('Inter', 7)
                    p.drawString(30, 157+banksLength, "SAYFA / PAGE     " + str(pageNum) + " of " + str(pageCount))
                    pageNum = pageNum + 1
                    #####sayfa numarası-end#####
                    
                    
                    
                ####TOTAL TABLO#####
                
                subTotalPrice = 0
                totalPrice = 0
                
                for part in parts:
                    subTotalPrice = subTotalPrice + part.totalPrice
                    totalPrice = totalPrice + part.totalPrice
                for expense in expenses:
                    subTotalPrice = subTotalPrice + expense.totalPrice
                    totalPrice = totalPrice + expense.totalPrice
                
                try:
                    discount = round(1-(totalPrice/subTotalPrice),2)
                except:
                    discount = 0
                    
                discountPrice  = round(subTotalPrice - totalPrice,2)
                
                # Para miktarını belirtilen formatta gösterme
                partsSubTotalFixed = "{:,.2f}".format(round(partsSubTotal,2))
                discountTotalFixed = "{:,.2f}".format(round(discountTotal,2))
                vatTotalFixed = "{:,.2f}".format(round(vatTotal,2))
                partsTotalFixed = "{:,.2f}".format(round(partsTotal,2))
                # Nokta ile virgülü değiştirme
                partsSubTotalFixed = partsSubTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                discountTotalFixed = discountTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                vatTotalFixed = vatTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                partsTotalFixed = partsTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

                vatRate = sendInvoice.vat
                
                if vatRate == 0:
                    vatText = "KDV / VAT"
                else:
                    if vatRate.is_integer():
                        vatText = "KDV " + str(int(vatRate)) + "% / VAT " + str(int(vatRate)) + "%"
                    else:
                        vatText = "KDV " + str(vatRate) + "% / VAT " + str(vatRate) + "%"
                
                dataSubTotal=[["ARA TOPLAM / SUB TOTAL"],
                                ["İSKONTO / DISCOUNT"],
                                [vatText],
                                ["TOPLAM / G.AMOUNT"]
                                ]
                table = Table(dataSubTotal, colWidths=((w-60)/100)*18 - 5, rowHeights=13)
                table.setStyle(totalLeftTableStyleLeftTotal)
                
                table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+5, 100+banksLength)
                table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+5, 100+banksLength)
                tableTotalLeftLength = table._colWidths[0]
                
                # Para miktarını belirtilen formatta gösterme
                totalTotalPrice3Fixed = "{:,.2f}".format(round(partsTotalsDict["totalTotalPrice3"],2))
                totalDiscountFixed = "{:,.2f}".format(round(partsTotalsDict["totalDiscount"],2))
                totalVatFixed = "{:,.2f}".format(round(partsTotalsDict["totalVat"],2))
                totalFinalFixed = "{:,.2f}".format(round(partsTotalsDict["totalFinal"],2))
                # Nokta ile virgülü değiştirme
                totalTotalPrice3Fixed = totalTotalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalDiscountFixed = totalDiscountFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalVatFixed = totalVatFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalFinalFixed = totalFinalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                dataSubTotal=[[str(totalTotalPrice3Fixed) + " " + sendInvoice.currency.code],
                                [str(totalDiscountFixed) + " " + sendInvoice.currency.code],
                                [str(totalVatFixed) + " " + sendInvoice.currency.code],
                                [str(totalFinalFixed) + " " + sendInvoice.currency.code]
                                ]
                table = Table(dataSubTotal, colWidths=((w-60)/100)*13, rowHeights=13)
                table.setStyle(totalRightTableStyleRightTotal)
                
                table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+tableTotalLeftLength+5, 100+banksLength)
                table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+tableTotalLeftLength+5, 100+banksLength)
                tableTotalLeftLength = table._colWidths[0]
                
                #####total tablo-end#####
            
                #####yalnız tablo#####
                tableLeftStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                                        ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                                        ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                        ('BACKGROUND',(0,0), (-1,-1), "#c7d3e1")
                                        ])
                tableRightStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                                        ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                                        ('FONT', (0, 0), (-1, -1), 'Inter', 5.5),
                                        ])
                data=[["Yalnız / Only"]]
                table = Table(data, colWidths=(w-60)/10, rowHeights=tableRowHeight)
                table.setStyle(tableLeftStyle)
                
                table.wrapOn(p, 30, 139+banksLength)
                table.drawOn(p, 30, 139+banksLength)
                
                data=[[sendInvoice.only]]
                table = Table(data, colWidths=(w-60)-((w-60)/10)-(((w-60)/100)*31) - 5, rowHeights=tableRowHeight)
                table.setStyle(tableRightStyle)
                
                table.wrapOn(p, 30+((w-60)/10), 139+banksLength)
                table.drawOn(p, 30+((w-60)/10), 139+banksLength)
                #####yalnız tablo-end#####
            
                #####önemli yazı#####
                p.setFont('Inter', 7)
                data=[("")]
                table = Table(data, colWidths=(w-60) - (((w-60)/100)*31) - 5, rowHeights=30)
                table.setStyle(TableStyle([
                                            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                                        ]))
                
                table.wrapOn(p, 30, 100+banksLength)
                table.drawOn(p, 30, 100+banksLength)
                
                p.setFont('Inter-Bold', 6)
                p.setFillColor(HexColor("#922724"))
                p.drawCentredString((w/2) - ((((w-60)/100)*31)/2) - (5/2), 120+banksLength, f"Tüm satışlar {sourceCompany.formalName} satış şartları dahilinde yapılmaktadır.")
                p.drawCentredString((w/2) - ((((w-60)/100)*31)/2) - (5/2), 105+banksLength, "Satış şartları kopyası www.esmarinesolutions.com adresinde bulunmaktadır.")
                p.setFillColor(HexColor("#000"))
                
                p.setFont('Inter', 7)
                #####önemli yazı-end#####
            
                #####teslim tablo#####
                data=[["TESLİM EDEN / DELIVERER:"]]
                table = Table(data, colWidths=((w-60)/2)-5, rowHeights=tableRowHeight+5)
                table.setStyle(tableRightStyleBold)
                
                table.wrapOn(p, 30, 75+banksLength)
                table.drawOn(p, 30, 75+banksLength)
                
                data=[["TESLİM ALAN / RECEIVED BY:"]]
                table = Table(data, colWidths=((w-60)-((w-60)/2))-5, rowHeights=tableRowHeight+5)
                table.setStyle(tableRightStyleBold)
                
                table.wrapOn(p, 30+((w-60)/2)+5, 75+banksLength)
                table.drawOn(p, 30+((w-60)/2)+5, 75+banksLength)
                #####teslim tablo-end#####
            
                #####iban yazı#####
                
                p.setFont('Inter', 7)
                
                bankH = 65 + banksLength
                bankW = 30
                bankPosition = 0
                
                if isBanks:
                    bankW = bankW + bankPosition
                    p.drawString(bankW, bankH, "Türkiye İş Bankası (Swift: ISBKTRIS)")
                    bankH = bankH - 10
                    for isBank in isBanks:
                        p.drawString(bankW, bankH, f"IBAN: {isBank.ibanNo} {isBank.currency.code}")
                        bankH = bankH - 10
                    
                    bankPosition = (w/3-10)
                
                if vakifBanks:
                    bankH = 65 + banksLength
                    bankW = 30
                    bankW = bankW + bankPosition
                    p.drawString(bankW, bankH, "Vakıfbank (Swift: TVBATR2A)")
                    bankH = bankH - 10
                    for vakifBank in vakifBanks:
                        p.drawString(bankW, bankH, f"IBAN: {vakifBank.ibanNo} {vakifBank.currency.code}")
                        bankH = bankH - 10
                    
                    if bankPosition == 0:
                        bankPosition = (w/3-10)
                    else:
                        bankPosition = (w/3*2-20)
                
                if halkBanks:
                    bankH = 65 + banksLength
                    bankW = 30
                    bankW = bankW + bankPosition
                    
                    p.drawString(bankW, bankH, "Halkbank (Swift: TRHBTR2A)")
                    bankH = bankH - 10
                    for halkBank in halkBanks:
                        p.drawString(bankW, bankH, f"IBAN: {halkBank.ibanNo} {halkBank.currency.code}")
                        bankH = bankH - 10
                #####iban yazı-end#####
            else: 
                if len(items) == slice or len(items) % slice > 29:
                    pageCount = pageCount + 1
                p.setFont('Inter', 7)
                #th-246-((lenData+2)*partsTableRowHeight)
                p.drawString(30, 75, "SAYFA / PAGE     " + str(pageNum) + " of " + str(pageCount) + "     CONTINUED")
                pageNum = pageNum + 1
            
            
            
            p.showPage()

        p.save()
    except Exception as e:
        logger.exception(e)
 
 