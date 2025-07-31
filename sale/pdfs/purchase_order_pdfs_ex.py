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

import os
import io
import shutil
from datetime import datetime
import math

from ..models import PurchaseOrder,PurchaseOrderPart
from card.models import EnginePart
from source.models import Company as SourceCompany

 
def purchaseOrderPdfEx(theRequest, purchaseOrder, sourceCompanyId):
    #quotation içerisindeki part listesi
    #parts = purchaseOrder.purchaseorderpart_set.select_related("inquiryPart")
    
    sourceCompany = SourceCompany.objects.filter(id = sourceCompanyId).first()
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
        
    parts = PurchaseOrderPart.objects.filter(purchaseOrder = purchaseOrder).order_by("sequency")
    
    partsSubTotal = 0
    partsTotal = 0
    for part in parts:
        partsSubTotal = partsSubTotal + part.totalPrice
    discountTotal = partsSubTotal * (purchaseOrder.discount/100)
    partsTotal = float(partsSubTotal) - float(discountTotal)
    
    partsTotalsDict = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
    partsTotalDict = 0
    
    for part in parts:
        partsTotalDict  = partsTotalDict + part.totalPrice
        partsTotalsDict["totalUnitPrice1"] = partsTotalsDict["totalUnitPrice1"] + part.unitPrice
        partsTotalsDict["totalUnitPrice2"] = partsTotalsDict["totalUnitPrice2"] + part.unitPrice
        partsTotalsDict["totalUnitPrice3"] = partsTotalsDict["totalUnitPrice3"] + part.unitPrice
        partsTotalsDict["totalTotalPrice1"] = partsTotalsDict["totalTotalPrice1"] + part.totalPrice
        partsTotalsDict["totalTotalPrice2"] = partsTotalsDict["totalTotalPrice2"] + part.totalPrice
        partsTotalsDict["totalTotalPrice3"] = partsTotalsDict["totalTotalPrice3"] + part.totalPrice
    
    if purchaseOrder.discountAmount > 0:
        partsTotalsDict["totalDiscount"] = purchaseOrder.discountAmount
    else:
        partsTotalsDict["totalDiscount"] = partsTotalsDict["totalTotalPrice3"] * (purchaseOrder.discount/100)
    partsTotalsDict["totalFinal"] = partsTotalsDict["totalTotalPrice3"] - partsTotalsDict["totalDiscount"]
    
    
    #standart ayar
    buffer = io.BytesIO()
    
    #dosyanın kaydedileceği konum
    folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "sale", "purchase_order", "documents")
    
    #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    
    #font ayarları
    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
    pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
    
    #standart ayar
    p = canvas.Canvas(folderPath + "/" + purchaseOrder.purchaseOrderNo + ".pdf", pagesize = landscape(A4))
    
     #standart ayar
    h, w = A4
    
    ystart = 550
    
    #tablo satır yükseklikleri
    tableRowHeight = 15
    partsTableRowHeight = 13
    
    #tablo stilleri
    tableLeftStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                               ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 7),
                               ('BACKGROUND',(0,0), (-1,-1), "#c7d3e1")
                               ])
    tableRightStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                               ('FONT', (0, 0), (-1, -1), 'Inter', 7),
                               ])
    
    #?
    p.setLineWidth(0.5)
    
    #logo
    esmsImg = Image.open(os.path.join(os.getcwd(), "static", "images", "esms-logo2.jpg"))
    
    #başlık
    p.setFont('Inter', 16)
    p.setFillColor(HexColor("#922724"))
    p.drawCentredString(w/2, h-95, "PURCHASE ORDER")
    
    p.setFillColor(HexColor("#000"))
    
   #####sol üst tablo#####
    p.setFont('Inter-Bold', 7)
    p.drawString(35, h-125, "TO")
    p.setFont('Inter', 7)
    p.drawString(50, h-125, ":" + purchaseOrder.inquiry.supplier.name)
    
    p.setFont('Inter', 7)
    data=[("")]
    table = Table(data, colWidths=w/2-35, rowHeights=tableRowHeight*4)
    table.setStyle(TableStyle([
                                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                            ]))
    
    table.wrapOn(p, 30, h-170)
    table.drawOn(p, 30, h-170)
    #####sol üst tablo-end#####
    
    #####sağ üst tablo#####
    data=[["YOUR REF"],
          ["OUR REF"],
          ["PROJECT NO"],
          ["PURCHASE ORDER NO"]
          ]
    table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
    table.wrapOn(p, w/2+5, h-170)
    table.drawOn(p, w/2+5, h-170)
    
    data=[[purchaseOrder.inquiry.supplierRef],
          [purchaseOrder.orderConfirmation.quotation.quotationNo],
          [theRequest.requestNo],
          [purchaseOrder.purchaseOrderNo]
          ]
    table = Table(data, colWidths=((w/2-35)/4)*3, rowHeights=tableRowHeight)
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, (w/2+5)+((w/2-35)/4), h-170)
    table.drawOn(p, (w/2+5)+((w/2-35)/4), h-170)
    #####sağ üst tablo-end#####
    
    p.setFont('Inter', 7)
    p.drawString(30, h-180, "We thank you for your inquiry and are pleased to offer subject to unsold and subject to our standard sales & purchase conditions ( available on request) for;")
    
    #####sol alt tablo#####
    data=[["MAKER"],
          ["TYPE"]
          ]
    table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
    table.wrapOn(p, 30, h-215)
    table.drawOn(p, 30, h-215)
    
    if theRequest.vessel:
        imo = theRequest.vessel.imo
    else:
        imo = ""
    
    data=[[theRequest.maker],
          [theRequest.makerType],
          ]
    table = Table(data, colWidths=((w/2-35)/4)*3, rowHeights=tableRowHeight)
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, 30+((w/2-35)/4), h-215)
    table.drawOn(p, 30+((w/2-35)/4), h-215)
    #####sol alt tablo-end#####
    
    #####sağ alt tablo#####
    data=[["DELIVERY"],
          ["PAYMENT"]
          ]
    table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
    table.wrapOn(p, w/2+5, h-215)
    table.drawOn(p, w/2+5, h-215)
    
    if theRequest.vessel:
        vessel = theRequest.vessel
    else:
        vessel = ""
        
    data=[[purchaseOrder.delivery],
          [purchaseOrder.payment]
          ]
    table = Table(data, colWidths=((w/2-35)/4)*3, rowHeights=tableRowHeight)
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, (w/2+5)+((w/2-35)/4), h-215)
    table.drawOn(p, (w/2+5)+((w/2-35)/4), h-215)
    #####sağ alt tablo-end#####
    
    #####parça sayısına göre sayfa dilimleme#####
    #standart ayar
    slice = 10
    pageNum = 1
    pageCount = len(parts) // slice
    #standart ayar
    if len(parts) % slice != 0:
        pageCount = pageCount + 1
    #standart ayar
    for i in range(0, len(parts), slice):
        #standart ayar
        partsList = parts[i:i+slice]
        #standart ayar
        p.drawInlineImage(esmsImg, 30, ystart-10, width=102,height=40)
        p.setFont('Inter-Bold', 7)
        #p.drawString(450, h-50, "DATE")
        p.setFont('Inter', 7)
        #p.drawString(480, h-50, ":" + str(inquiry.inquiryDate.strftime("%d.%m.%Y")))
        
        p.setFont('Inter-Bold', 7)
        #p.drawString(450, h-70, "REF NO")
        p.setFont('Inter', 7)
        #p.drawString(480, h-70, ":" + str(inquiry.inquiryNo))
        
        p.setFont('Inter-Bold', 7)
        p.drawString(700, ystart-10, "DATE")
        p.setFont('Inter', 7)
        p.drawString(730, ystart-10, ":" + str(purchaseOrder.purchaseOrderDate.strftime("%d.%m.%Y")))
        
        if i >= slice:
            th = h+100
        else:
            th = h
        
        #####parts tablo#####
        
        partsTableStyleLeft = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 7),
                                ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 7),
                                ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                ('BACKGROUND',(0,0), (-1,0), "#c7d3e1")
                                ])
        
        partsTableStyleRight = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 7),
                                ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 7),
                                ('ALIGN', (0, 0), (-1, -1), "RIGHT"),
                                ('BACKGROUND',(0,0), (-1,0), "#c7d3e1")
                                ])
        
        partsTableStyleCenter = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 7),
                                ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 7),
                                ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                                ('BACKGROUND',(0,0), (-1,0), "#c7d3e1")
                                ])
        
        totalLeftTableStyleLeft = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 7),
                                ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 7),
                                ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                ('BACKGROUND',(0,0), (-1,-1), "#c7d3e1")
                                ])
        
        totalRightTableStyleRight = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 7),
                                ('ALIGN', (0, 0), (-1, -1), "RIGHT")
                                ])
        
        #sütun(tablo) 1
        data=[["Line"]]
        for j in range(len(partsList)):
            data.append([j+i+1])
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleLeft)
        
        table.wrapOn(p, 30, th-220-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30, th-220-(len(data)*partsTableRowHeight))
        table1Length = table._colWidths[0]
        
        #sütun(tablo) 2
        data=[["Item"]]
        for part in partsList:
            data.append([part.inquiryPart.requestPart.part.partNo])
        table = Table(data, colWidths=((w-60)/100)*10, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleLeft)
        
        table.wrapOn(p, 30+table1Length, th-220-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length, th-220-(len(data)*partsTableRowHeight))
        table2Length = table._colWidths[0]
        
        #sütun(tablo) 3
        data=[["Description of Goods & Services"]]
        for part in partsList:
            data.append([part.inquiryPart.requestPart.part.description])
        table = Table(data, colWidths=((w-60)/100)*45, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleLeft)
        
        table.wrapOn(p, 30+table1Length+table2Length, th-220-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length, th-220-(len(data)*partsTableRowHeight))
        table3Length = table._colWidths[0]
        
        #sütun(tablo) 4
        data=[["Qty"]]
        for part in partsList:
            data.append([part.quantity])
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
        partsTableStyleRight
        table.setStyle(partsTableStyleRight)
        
        table.wrapOn(p, 30+table1Length+table2Length+table3Length, th-220-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length+table3Length, th-220-(len(data)*partsTableRowHeight))
        table4Length = table._colWidths[0]
        
        #sütun(tablo) 5
        data=[["Unit Price"]]
        for part in partsList:
            data.append([str(round(part.unitPrice,2)) + " " + purchaseOrder.inquiry.currency.code])
        table = Table(data, colWidths=((w-60)/100)*10, rowHeights=partsTableRowHeight, hAlign="RIGHT")
        table.setStyle(partsTableStyleRight)
        
        table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length, th-220-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length, th-220-(len(data)*partsTableRowHeight))
        table5Length = table._colWidths[0]
        
        #sütun(tablo) 6
        data=[["Total Price"]]
        for part in partsList:
            data.append([str(round(part.totalPrice,2)) + " " + purchaseOrder.inquiry.currency.code])
        table = Table(data, colWidths=((w-60)/100)*10, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleRight)
        
        table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length, th-220-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length, th-220-(len(data)*partsTableRowHeight))
        table6Length = table._colWidths[0]

        #sütun(tablo) 7
        data=[["Avail."]]
        for part in partsList:
            if part.availability == 0:
                data.append(["Ex Stock"])
            elif part.availability > 1:
                data.append([str(part.availability) + " days"])
            elif part.availability == 1:
                data.append([str(part.availability) + " day"])
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleRight)
        
        table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+table6Length, th-220-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+table6Length, th-220-(len(data)*partsTableRowHeight))
        table7Length = table._colWidths[0]

        #sütun(tablo) 8
        data=[["Notes"]]
        for part in partsList:
            data.append([""])
        table = Table(data, colWidths=((w-60)/100)*10, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleLeft)
        
        table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+table6Length+table7Length, th-220-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+table6Length+table7Length, th-220-(len(data)*partsTableRowHeight))
        table8Length = table._colWidths[0]
        
        #sütun(tablo) total
        
        if pageNum == pageCount:
            subTotalPrice = 0
            totalPrice = 0
            
            for part in parts:
                subTotalPrice = subTotalPrice + part.totalPrice
                totalPrice = totalPrice + part.totalPrice
            
            
            
            dataSubTotal=[["SUB TOTAL"],
                          ["DISCOUNT"],
                          ["NET TOTAL"]
                          ]
            table = Table(dataSubTotal, colWidths=((w-60)/100)*10, rowHeights=partsTableRowHeight)
            table.setStyle(totalLeftTableStyleLeft)
            
            table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length, th-220-((len(data)+3)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length, th-220-((len(data)+3)*partsTableRowHeight))
            tableTotalLeftLength = table._colWidths[0]
            
            dataSubTotal=[[str(round(partsTotalsDict["totalTotalPrice3"],2)) + " " + purchaseOrder.inquiry.currency.code],
                          [str(round(partsTotalsDict["totalDiscount"],2)) + " " + purchaseOrder.inquiry.currency.code],
                          [str(round(partsTotalsDict["totalFinal"],2)) + " " + purchaseOrder.inquiry.currency.code]
                          ]
            table = Table(dataSubTotal, colWidths=((w-60)/100)*10, rowHeights=partsTableRowHeight)
            table.setStyle(totalRightTableStyleRight)
            
            table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+tableTotalLeftLength, th-220-((len(data)+3)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+tableTotalLeftLength, th-220-((len(data)+3)*partsTableRowHeight))
            tableTotalLeftLength = table._colWidths[0]
            
            
            
            dataNote=[[""]]
            table = Table(dataNote, colWidths=((w-60)/100)*49, rowHeights=partsTableRowHeight*4)
            table.setStyle(tableRightStyle)
            
            table.wrapOn(p, 30, th-285-((len(data)+4)*partsTableRowHeight))
            table.drawOn(p, 30, th-285-((len(data)+4)*partsTableRowHeight))
        
            #to yazısı
            p.setFillColor(HexColor("#000"))
            p.setFont('Inter-Bold', 6)
            p.drawString(35, th-245-((len(data)+4)*partsTableRowHeight), "INVOICE TO: ")
            p.setFont('Inter', 6)
            p.drawString(80, th-245-((len(data)+4)*partsTableRowHeight), sourceCompanyFormalName)
            p.drawString(80, th-240-((len(data)+5)*partsTableRowHeight), "Aydıntepe Mah. Sahil Bulvarı Cad. Denizciler Ticaret Merkezi No:126 57/C P.K. 34947 Tuzla İstanbul TR")
            p.drawString(80, th-235-((len(data)+6)*partsTableRowHeight), "TÜRKİYE")
            p.drawString(80, th-230-((len(data)+7)*partsTableRowHeight), "TUZLA VD. 3801139954")
        
        
            dataNote=[[""]]
            table = Table(dataNote, colWidths=((w-60)/100)*49, rowHeights=partsTableRowHeight*4)
            table.setStyle(tableRightStyle)
            
            table.wrapOn(p, (w/2)+2, th-285-((len(data)+4)*partsTableRowHeight))
            table.drawOn(p, (w/2)+2, th-285-((len(data)+4)*partsTableRowHeight))

            #to yazısı
            p.setFillColor(HexColor("#000"))
            p.setFont('Inter-Bold', 7)
            p.drawString((w/2)+4, th-245-((len(data)+4)*partsTableRowHeight), "")
            p.setFont('Inter', 7)
            p.drawString((w/2)+34, th-245-((len(data)+4)*partsTableRowHeight), "")
        
        #####parts tablo-end#####
        
        p.setFont('Inter', 7)
        data=[("")]
        table = Table(data, colWidths=w-60, rowHeights=50)
        table.setStyle(TableStyle([
                                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                                ]))
        
        table.wrapOn(p, 30, 110)
        table.drawOn(p, 30, 110)
        
        p.setFont('Inter-Bold', 7)
        p.setFillColor(HexColor("#922724"))
        p.drawCentredString(w/2, 145, "According to SOLAS CHAPTER II-1 Part A-1 Regulation 3-5 , we hereby declare that the offered parts don't contain any asbestos material. Asbestos-Free certificates, if available, can be provided based on request.")
        
        p.setFillColor(HexColor("#000"))
        p.drawCentredString(w/2, 135, "This document contains confidental information belonging to ESMS and must not be disclosed to 3rd parties without permission.")
        
        p.drawCentredString(w/2, 125, "Cancellation of any confirmed order will result in additional fees (amount of the fees will be changed upon supplier desicion and total amount of order)")
        
        p.setFont('Inter', 7)
            
        ######sayfa altı########
        p.setStrokeColor(HexColor("#808080"))
        p.line(30, 100, w-30, 100)
        p.setFont('Inter-Bold', 7)
        p.drawString(30, 90, sourceCompanyFormalName)
        p.drawString(30, 70, "Office")
        p.setFont('Inter', 7)
        p.drawString(60, 70, "Aydıntepe Mah. Sahil Bulvarı Cad. Denizciler Ticaret Merkezi No:126 57/C P.K. 34947 Tuzla İstanbul TR")
        #p.drawString(60, 70, "No:126 57/C P.K. 34947 Tuzla İstanbul TR")
        p.setFont('Inter-Bold', 7)
        p.drawString(30, 60, "Tel")
        p.setFont('Inter', 7)
        p.drawString(60, 60, "+90 (216) 330 82 46")
        p.setFont('Inter-Bold', 7)
        p.drawString(30, 50, "Fax")
        p.setFont('Inter', 7)
        p.drawString(60, 50, "+90 (216) 330 74 06")
        
        lrImg = Image.open(os.path.join(os.getcwd(), "static", "images", "sale", "lr-logo4.jpg"))
        
        p.drawInlineImage(lrImg, w-180, 46, width=150,height=50)
        
        p.line(30, 40, 810, 40)
        p.setFont('Inter-Bold', 7)
        p.drawString(30, 30, str(purchaseOrder.inquiry.project.user.first_name) + " " + str(purchaseOrder.inquiry.project.user.last_name) + " / " + str(purchaseOrder.inquiry.project.user.profile.positionType))
        p.setFont('Inter-Bold', 7)
        p.drawString(310, 30, "Document Date: " + str(datetime.today().date().strftime("%d.%m.%Y")))
        ######sayfa altı-end########
        
        #####sayfa numarası#####
        if len(parts) > slice:
            p.setFont('Inter', 7)
            p.drawCentredString(w/2, 10, str(pageNum) + "/" + str(pageCount))
            pageNum = pageNum + 1
        #####sayfa numarası-end#####
        
        p.showPage()

    p.save()
