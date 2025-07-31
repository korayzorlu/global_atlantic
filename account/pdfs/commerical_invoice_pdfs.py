from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, TableStyle, PageBreak
from reportlab.platypus.tables import Table
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont   
from reportlab import rl_config
from PIL import Image

from django.db.models import Count
from django.db.models import Q
from source.models import Bank as SourceBank

import os
import io
import shutil
from django.utils import timezone
from datetime import datetime

from ..models import SendInvoice, IncomingInvoice, ProformaInvoiceExpense,ProformaInvoiceItem, SendInvoicePart, SendInvoiceExpense,SendInvoiceItem,CommericalInvoice,CommericalInvoiceItem,CommericalInvoiceExpense
from card.models import EnginePart, Vessel, Billing, Company
from sale.models import QuotationPart

def commericalInvoicePdf(theRequest, orderConfirmation, commericalInvoice, sourceCompany):
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
        
    parts = CommericalInvoiceItem.objects.filter(invoice = commericalInvoice).order_by("quotationPart__sequency")
    expenses = CommericalInvoiceExpense.objects.filter(invoice = commericalInvoice)
    items = []
    for part in parts:
        print(f"desc: {part.trDescription}")
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
    vatTotal = (partsSubTotal - discountTotal) * (commericalInvoice.vat / 100)
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

    if orderConfirmation.quotation.manuelDiscountAmount > 0:
        partsTotalsDict["totalDiscount"] = orderConfirmation.quotation.manuelDiscountAmount
    else:
        partsTotalsDict["totalDiscount"] = partsTotalsDict["totalTotalPrice3"] * (orderConfirmation.quotation.manuelDiscount/100)
        
    for expense in expenses:
        partsTotalsDict["totalExpense"] = partsTotalsDict["totalExpense"] + expense.totalPrice
    
    partsTotalsDict["totalTotalPrice3"] = partsTotalsDict["totalTotalPrice3"] + partsTotalsDict["totalExpense"]
    partsTotalsDict["totalVat"] = (partsTotalsDict["totalTotalPrice3"] - partsTotalsDict["totalDiscount"]) * (commericalInvoice.vat/100)
    partsTotalsDict["totalFinal"] = partsTotalsDict["totalTotalPrice3"] - partsTotalsDict["totalDiscount"] + partsTotalsDict["totalVat"]
    
    
    #standart ayar
    buffer = io.BytesIO()
    
    #dosyanın kaydedileceği konum
    folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "account", "commerical_invoice", "documents")
    
    #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    
    #font ayarları
    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
    pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
    
    #standart ayar
    p = canvas.Canvas(folderPath + "/" + commericalInvoice.commericalInvoiceNo + ".pdf", pagesize = A4)
    
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
    
    #signImg = Image.open(os.path.join(os.getcwd(), "static", "images", "account", "sign", "esms-sign.jpg"))
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
    vessel = commericalInvoice.vessel
    if vessel:
        vesselName = str(vessel.get_type_display()) + " " + str(vessel.name) + " - IMO No: " + str(vessel.imo)
        vesselName2 = str(vessel.get_type_display()) + " " + str(vessel.name)
    else:
        vesselName = ""
        vesselName2 = ""
        
    if commericalInvoice.billing:
        billingName = commericalInvoice.billing.name
        if commericalInvoice.billing.address:
            billingAddress = commericalInvoice.billing.address
            if commericalInvoice.billing.city:
                billingCity = commericalInvoice.billing.city.name
                billingAddress = billingAddress + " " + billingCity + " /"
            if commericalInvoice.billing.country:
                billingCountry = commericalInvoice.billing.country.international_formal_name
                billingAddress = billingAddress + " " + billingCountry
        else:
            billingAddress = ""
            if commericalInvoice.billing.city:
                billingCity = commericalInvoice.billing.city.name
                billingAddress = billingAddress + " " + billingCity + " /"
            if commericalInvoice.billing.country:
                billingCountry = commericalInvoice.billing.country.international_formal_name
                billingAddress = billingAddress + " " + billingCountry
    else:    
        billingName = ""
        billingAddress = ""
        
    p.setFillColor(HexColor("#000"))
    p.setFont('Inter-Bold', 6)
    p.drawString(35, h-100, "VESSEL / PLANT")
    p.setFont('Inter', 6)
    p.drawString(85, h-100, ": " + vesselName)
    p.drawString(35, h-110, billingName)
    
    #####billing address with multiple lines#####
    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
    newBillingAddress = ""
    for i in range(0, len(billingAddress), 50):
        chunk = billingAddress[i:i+50]
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
    p.drawString(w/2+10, h-100, "DELIVERY ADDRESS")
    p.setFont('Inter', 6)
    p.drawString(w/2+10, h-110, "SHIP SPARE IN TRANSIT TO THE MASTER OF " + str(vesselName2))
    p.setFont('Inter', 6)
    #p.drawString(w/2+10, h-140, delivery.address)
    
    # Her bir satırı ayrı bir drawText çağrısı ile ekleyelim
    if commericalInvoice.deliveryNote:
        deliveryNote = commericalInvoice.deliveryNote.replace("\r\n", "\n")
        deliveryNote = deliveryNote.replace("\n", " ")
    else:
        deliveryNote = ""
    newDeliveryNote = ""
    for k in range(0, len(deliveryNote), 80):
        chunk = deliveryNote[k:k+80]
        if len(chunk) < 80:
            newDeliveryNote += chunk
        else:
            space_index = chunk.rfind(" ")
            if space_index != -1:
                newDeliveryNote += chunk[:space_index] + '\n'
                if space_index + 1 < len(chunk):
                    newDeliveryNote += chunk[space_index+1:]
            else:
                newDeliveryNote += chunk
                
    lines = newDeliveryNote.replace("\r\n", "\n")
    lines = lines.split('\n')
    line_height = 10  # İsteğe bağlı, satır yüksekliği
    current_y = h-120

    for line in lines:
        p.drawString(w/2+10, current_y, line)
        current_y = current_y - line_height
    
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
    data=[["ORDER DATE"],
          ["ORDER REF"],
          ["OUR REF"]
          ]
    table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
    table.wrapOn(p, 30, h-215)
    table.drawOn(p, 30, h-215)
    
    if commericalInvoice.vessel:
        imo = commericalInvoice.vessel.imo
    else:
        imo = ""
    
    trackingNo = ""
    
    data=[[orderConfirmation.orderConfirmationDate.strftime("%d.%m.%Y")],
        [theRequest.customerRef],
        [orderConfirmation.quotation.quotationNo]
        ]
    
    table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight)
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, 30+((w/2-35)/2), h-215)
    table.drawOn(p, 30+((w/2-35)/2), h-215)
    #####sol alt tablo-end#####
    
    #####sağ alt tablo#####
    data=[["CURRENCY"],
          ["DELIVERY TERMS"],
          ["PAYMENT TERMS"]
          ]
    table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
    table.wrapOn(p, w/2+5, h-215)
    table.drawOn(p, w/2+5, h-215)
    
    if commericalInvoice.vessel:
        vessel = commericalInvoice.vessel
    else:
        vessel = ""
    
    if theRequest.maker:
        maker = theRequest.maker
    else:
        maker = ""
    if theRequest.makerType:
        makerType = theRequest.makerType
    else:
        makerType = ""
        
    data=[[commericalInvoice.currency.code],
        [orderConfirmation.quotation.delivery],
        [orderConfirmation.quotation.payment]
    ]
    
    table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight)
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, (w/2+5)+((w/2-35)/2), h-215)
    table.drawOn(p, (w/2+5)+((w/2-35)/2), h-215)
    #####sağ alt tablo-end#####
    
    #####parça sayısına göre sayfa dilimleme#####
    #standart ayar
    slice = 38
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
        
        data=[["COMMERCIAL INVOICE & DELIVERY NOTE"],
        [commericalInvoice.commericalInvoiceNo]
        ]
        table = Table(data, rowHeights=tableRowHeight+5)
        table_width, table_height = table.wrap(0, 0)
        table.setStyle(invoiceTableStyleTitle)
        
        table.wrapOn(p, (w/2+5)+((w/2-35)-table_width), h-60)
        table.drawOn(p, (w/2+5)+((w/2-35)-table_width), h-60)
        
        p.setFont('Inter-Bold', 6)
        p.drawString((w/2+5)+((w/2-35)/2)-20, h-72, "DATE: ")
        p.setFont('Inter', 6)
        p.drawString((w/2+5)+((w/2-35)/2)+20, h-72, str(commericalInvoice.commericalInvoiceDate.strftime("%d.%m.%Y")))
        
        p.setFont('Inter-Bold', 6)
        p.drawString((w/2+5)+((w/2-35)/2)-20, h-82, "PROJECT: ")
        p.setFont('Inter', 6)
        p.drawString((w/2+5)+((w/2-35)/2)+20, h-82, str(commericalInvoice.project.projectNo))
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
        data=[["Item"]]
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=(partsTableRowHeight*2)-5)
        table.setStyle(partsTableStyleLeft)
        
        table.wrapOn(p, 30, th-231-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30, th-231-(len(data)*partsTableRowHeight))
        table1Length = table._colWidths[0]
        
        data=[]
        for j in range(len(partsList)):
            data.append([j+i+1])
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleLeftWhite)
        
        table.wrapOn(p, 30, th-244-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30, th-244-(len(data)*partsTableRowHeight))
        table1Length = table._colWidths[0]
        
        #sütun(tablo) 3
        data=[["Description"]]
        table = Table(data, colWidths=((w-60)/100)*63, rowHeights=(partsTableRowHeight*2)-5)
        table.setStyle(partsTableStyleCenter)
        
        table.wrapOn(p, 30+table1Length, th-231-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length, th-231-(len(data)*partsTableRowHeight))
        table3Length = table._colWidths[0]
        
        data=[]
        for part in partsList:
            data.append([part["name"]])
        table = Table(data, colWidths=((w-60)/100)*12, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleDescriptionLeftWhite)
        
        table.wrapOn(p, 30+table1Length, th-244-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length, th-244-(len(data)*partsTableRowHeight))
        table3Length = table._colWidths[0]
        
        #sütun(tablo) 4
        data=[]
        for part in partsList:
            data.append([part["description"]])
        table = Table(data, colWidths=((w-60)/100)*51, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleDescriptionLeftWhite)
        
        table.wrapOn(p, 30+table1Length+table3Length, th-244-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table3Length, th-244-(len(data)*partsTableRowHeight))
        table4Length = table._colWidths[0]
        
        #sütun(tablo) 4
        data=[["Qty"]]
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=(partsTableRowHeight*2)-5)
        partsTableStyleRight
        table.setStyle(partsTableStyleCenter)
        
        table.wrapOn(p, 30+table1Length+table3Length+table4Length, th-231-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table3Length+table4Length, th-231-(len(data)*partsTableRowHeight))
        table5Length = table._colWidths[0]
        
        data=[]
        for part in partsList:
            data.append([part["quantity"]])
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
        partsTableStyleRight
        table.setStyle(partsTableStyleLeftWhite)
        
        table.wrapOn(p, 30+table1Length+table3Length+table4Length, th-244-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table3Length+table4Length, th-244-(len(data)*partsTableRowHeight))
        table5Length = table._colWidths[0]
        
        #sütun(tablo) 5
        data=[["Unit"]]
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=(partsTableRowHeight*2)-5)
        partsTableStyleRight
        table.setStyle(partsTableStyleCenter)
        
        table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length, th-231-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length, th-231-(len(data)*partsTableRowHeight))
        table6Length = table._colWidths[0]
        
        data=[]
        for part in partsList:
            data.append([part["unit"]])
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
        partsTableStyleRight
        table.setStyle(partsTableStyleLeftWhite)
        
        table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length, th-244-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length, th-244-(len(data)*partsTableRowHeight))
        table6Length = table._colWidths[0]
        
        #sütun(tablo) 6
        data=[["Unit Price"]]
        table = Table(data, colWidths=((w-60)/100)*11, rowHeights=(partsTableRowHeight*2)-5, hAlign="RIGHT")
        table.setStyle(partsTableStyleCenter)
        
        table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length, th-231-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length, th-231-(len(data)*partsTableRowHeight))
        table7Length = table._colWidths[0]
        
        data=[]
        for part in partsList:
            # Para miktarını belirtilen formatta gösterme
            unitPrice3Fixed = "{:,.2f}".format(round(part["unitPrice"],2))
            # Nokta ile virgülü değiştirme
            unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            data.append([str(unitPrice3Fixed) + " " + commericalInvoice.currency.code])
        table = Table(data, colWidths=((w-60)/100)*11, rowHeights=partsTableRowHeight, hAlign="RIGHT")
        table.setStyle(partsTableStyleRightWhite)
        
        table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length, th-244-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length, th-244-(len(data)*partsTableRowHeight))
        table7Length = table._colWidths[0]
        
        #sütun(tablo) 7
        data=[["Total Price"]]
        table = Table(data, colWidths=((w-60)/100)*11, rowHeights=(partsTableRowHeight*2)-5)
        table.setStyle(partsTableStyleCenter)
        
        table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length+table7Length, th-231-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length+table7Length, th-231-(len(data)*partsTableRowHeight))
        table8Length = table._colWidths[0]
        
        data=[]
        for part in partsList:
            # Para miktarını belirtilen formatta gösterme
            totalPrice3Fixed = "{:,.2f}".format(round(part["totalPrice"],2))
            # Nokta ile virgülü değiştirme
            totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            data.append([str(totalPrice3Fixed) + " " + commericalInvoice.currency.code])
        table = Table(data, colWidths=((w-60)/100)*11, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleRightWhite)
        
        table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length+table7Length, th-244-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+table6Length+table7Length, th-244-(len(data)*partsTableRowHeight))
        table8Length = table._colWidths[0]
        
        lenData = len(data)
  
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
        
        if pageNum == pageCount:
            if len(items) == slice or len(items) % slice > 29:
                pageCount = pageCount + 1
                
            if len(partsList) > 29:
                p.setFont('Inter', 7)
                p.drawString(30, 75, "PAGE     " + str(pageNum) + " of " + str(pageCount) + "     CONTINUED")
                pageNum = pageNum + 1
            else:
                p.setFont('Inter', 7)
                p.drawString(30, 197, "PAGE     " + str(pageNum) + " of " + str(pageCount))
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
                
                data=[["COMMERICAL INVOICE & DELIVERY NOTE"],
                [commericalInvoice.commericalInvoiceNo]
                ]
                table = Table(data, rowHeights=tableRowHeight+5)
                table_width, table_height = table.wrap(0, 0)
                table.setStyle(invoiceTableStyleTitle)

                table.wrapOn(p, (w/2+5)+((w/2-35)-table_width), h-60)
                table.drawOn(p, (w/2+5)+((w/2-35)-table_width), h-60)
                
                p.setFont('Inter-Bold', 6)
                p.drawString((w/2+5)+((w/2-35)/2), h-77, "DATE: ")
                p.setFont('Inter', 6)
                p.drawString((w/2+5)+((w/2-35)/2)+30, h-77, str(commericalInvoice.commericalInvoiceDate.strftime("%d.%m.%Y")))
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
                p.drawString(30, 197, "PAGE     " + str(pageNum) + " of " + str(pageCount))
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

            vatRate = commericalInvoice.vat
            
            if vatRate == 0:
                vatText = "VAT"
            else:
                if vatRate.is_integer():
                    vatText = "VAT " + str(int(vatRate)) + "%"
                else:
                    vatText = "VAT " + str(vatRate) + "%"
            
            dataSubTotal=[["SUB TOTAL"],
                            ["DISCOUNT"],
                            [vatText],
                            ["G.AMOUNT"]
                            ]
            table = Table(dataSubTotal, colWidths=((w-60)/100)*18 - 5, rowHeights=13)
            table.setStyle(totalLeftTableStyleLeftTotal)
            
            table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+5, 140)
            table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+5, 140)
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
            
            dataSubTotal=[[str(totalTotalPrice3Fixed) + " " + commericalInvoice.currency.code],
                            [str(totalDiscountFixed) + " " + commericalInvoice.currency.code],
                            [str(totalVatFixed) + " " + commericalInvoice.currency.code],
                            [str(totalFinalFixed) + " " + commericalInvoice.currency.code]
                            ]
            table = Table(dataSubTotal, colWidths=((w-60)/100)*13, rowHeights=13)
            table.setStyle(totalRightTableStyleRightTotal)
            
            table.wrapOn(p, 30+table1Length+table3Length+table4Length+table5Length+tableTotalLeftLength+5, 140)
            table.drawOn(p, 30+table1Length+table3Length+table4Length+table5Length+tableTotalLeftLength+5, 140)
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
            data=[["Only"]]
            table = Table(data, colWidths=(w-60)/10, rowHeights=tableRowHeight)
            table.setStyle(tableLeftStyle)
            
            table.wrapOn(p, 30, 179)
            table.drawOn(p, 30, 179)
            
            data=[[commericalInvoice.only]]
            table = Table(data, colWidths=(w-60)-((w-60)/10)-(((w-60)/100)*31) - 5, rowHeights=tableRowHeight)
            table.setStyle(tableRightStyle)
            
            table.wrapOn(p, 30+((w-60)/10), 179)
            table.drawOn(p, 30+((w-60)/10), 179)
            #####yalnız tablo-end#####
        
            #####önemli yazı#####
            p.setFont('Inter', 7)
            data=[("")]
            table = Table(data, colWidths=(w-60) - (((w-60)/100)*31) - 5, rowHeights=30)
            table.setStyle(TableStyle([
                                        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                                    ]))
            
            table.wrapOn(p, 30, 140)
            table.drawOn(p, 30, 140)
            
            p.setFont('Inter-Bold', 6)
            p.setFillColor(HexColor("#922724"))
            p.drawCentredString((w/2) - ((((w-60)/100)*31)/2) - (5/2), 160, "Any use by us of any engines manufacturer's product codes is for description purposes only.")
            p.drawCentredString((w/2) - ((((w-60)/100)*31)/2) - (5/2), 153, "Such use does not mean that the parts sodescribed originate from the engine manufacturer.")
            p.drawCentredString((w/2) - ((((w-60)/100)*31)/2) - (5/2), 145, "Should confirmation on of origin be required, this will ve provided separately.")
            p.setFillColor(HexColor("#000"))
            
            p.setFont('Inter', 7)
            #####önemli yazı-end#####
        
            #####teslim tablo#####
            data=[["DELIVERER:"]]
            table = Table(data, colWidths=((w-60)/2)-5, rowHeights=tableRowHeight+5)
            table.setStyle(tableRightStyleBold)
            
            table.wrapOn(p, 30, 115)
            table.drawOn(p, 30, 115)
            
            data=[["RECEIVED BY:"]]
            table = Table(data, colWidths=((w-60)-((w-60)/2))-5, rowHeights=tableRowHeight+5)
            table.setStyle(tableRightStyleBold)
            
            table.wrapOn(p, 30+((w-60)/2)+5, 115)
            table.drawOn(p, 30+((w-60)/2)+5, 115)
            #####teslim tablo-end#####
        
            #####iban yazı#####
            isBanks = SourceBank.objects.select_related("currency").filter(
                Q(company = sourceCompany, bankName__icontains='İŞ BANKASI') | Q(company = sourceCompany, bankName__icontains='TÜRKİYE İŞ BANKASI')
            )
            halkBanks= SourceBank.objects.select_related("currency").filter(
                Q(company = sourceCompany, bankName__icontains='HALKBANK') | Q(company = sourceCompany, bankName__icontains='TÜRKİYE HALK BANKASI')
            )
            vakifBanks= SourceBank.objects.select_related("currency").filter(
                Q(company = sourceCompany, bankName__icontains='VAKIFBANK') | Q(company = sourceCompany, bankName__icontains='TÜRKİYE VAKIFLAR BANKASI')
            )
            
            p.setFont('Inter', 7)
            
            bankH = 105
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
                bankH = 105
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
                bankH = 105
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
            p.drawString(30, 75, "PAGE     " + str(pageNum) + " of " + str(pageCount) + "     CONTINUED")
            pageNum = pageNum + 1
        
        
        
        p.showPage()

    p.save()
 