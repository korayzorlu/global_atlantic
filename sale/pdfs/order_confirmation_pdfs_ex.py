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

from ..models import Request, InquiryPart, QuotationPart, PurchaseOrderPart,QuotationExtra
from card.models import EnginePart


def orderConfirmationPdff(theRequest, orderConfirmation):
    #quotation içerisindeki part listesi
    #parts = orderConfirmation.quotation.quotationpart_set.select_related("inquiryPart")
    parts = QuotationPart.objects.filter(quotation = orderConfirmation.quotation).order_by("sequency")
    
    partsSubTotal = 0
    partsTotal = 0
    for part in parts:
        partsSubTotal = partsSubTotal + part.totalPrice2
        partsTotal = partsTotal + part.totalPrice3
    discountTotal = partsTotal - partsSubTotal
    vatTotal = (partsSubTotal - discountTotal) * (orderConfirmation.vat / 100)
    partsTotal = partsTotal + vatTotal
    
    partsTotalsDict = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
        
    partsTotalDict = 0
    
    for part in parts:
        partsTotalDict  = partsTotalDict + part.totalPrice3
        partsTotalsDict["totalUnitPrice1"] = partsTotalsDict["totalUnitPrice1"] + part.unitPrice1
        partsTotalsDict["totalUnitPrice2"] = partsTotalsDict["totalUnitPrice2"] + part.unitPrice2
        partsTotalsDict["totalUnitPrice3"] = partsTotalsDict["totalUnitPrice3"] + part.unitPrice3
        partsTotalsDict["totalTotalPrice1"] = partsTotalsDict["totalTotalPrice1"] + part.totalPrice1
        partsTotalsDict["totalTotalPrice2"] = partsTotalsDict["totalTotalPrice2"] + part.totalPrice2
        partsTotalsDict["totalTotalPrice3"] = partsTotalsDict["totalTotalPrice3"] + part.totalPrice3
    
    if orderConfirmation.quotation.manuelDiscountAmount > 0:
        partsTotalsDict["totalDiscount"] = orderConfirmation.quotation.manuelDiscountAmount
    else:
        partsTotalsDict["totalDiscount"] = partsTotalsDict["totalTotalPrice3"] * (orderConfirmation.quotation.manuelDiscount/100)
    partsTotalsDict["totalVat"] = (partsTotalsDict["totalTotalPrice3"] - partsTotalsDict["totalDiscount"]) * (orderConfirmation.vat/100)
    partsTotalsDict["totalFinal"] = partsTotalsDict["totalTotalPrice3"] - partsTotalsDict["totalDiscount"] + partsTotalsDict["totalVat"]
    
    #standart ayar
    buffer = io.BytesIO()
    
    #dosyanın kaydedileceği konum
    folderPath = os.path.join(os.getcwd(), "media", "sale", "order_confirmation", "documents")
    
    #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    
    #font ayarları
    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
    pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
    
    #standart ayar
    p = canvas.Canvas(folderPath + "/" + orderConfirmation.orderConfirmationNo + ".pdf", pagesize = A4)
    
    #standart ayar
    w, h = A4
    
    ystart = 780
    
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
    p.setFont('Inter', 18)
    p.setFillColor(HexColor("#9d2235"))
    p.drawCentredString(w/2, h-120, "ORDER CONFIRMATION")
    
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
    
    #company
    p.setFillColor(HexColor("#000"))
    p.setFont('Inter-Bold', 7)
    p.drawString(35, h-170, "COMPANY")
    p.setFont('Inter', 7)
    p.drawString(80, h-170, ":" + theRequest.customer.name)
    
    #####sol üst tablo#####
    p.setFont('Inter', 7)
    data=[("")]
    table = Table(data, colWidths=w/2-35, rowHeights=tableRowHeight*6)
    table.setStyle(TableStyle([
                                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                            ]))
    
    table.wrapOn(p, 30, h-245)
    table.drawOn(p, 30, h-245)
    #####sol üst tablo-end#####
    
    #####sağ üst tablo#####
    data=[["ORDER DATE"],
        ["ORDER REF"],
        ["OUR REF"],
        ["CURRENCY"],
        ["DELIVERY TERMS"],
        ["PAYMENT TERMS"]
        ]
    table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
    table.wrapOn(p, w/2+5, h-245)
    table.drawOn(p, w/2+5, h-245)
    
    data=[[orderConfirmation.orderConfirmationDate],
        [theRequest.customerRef],
        [orderConfirmation.quotation.quotationNo],
        [orderConfirmation.quotation.currency.code],
        [orderConfirmation.quotation.delivery],
        [orderConfirmation.quotation.payment]
        ]
    table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight)
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, (w/2+5)+((w/2-35)/2), h-245)
    table.drawOn(p, (w/2+5)+((w/2-35)/2), h-245)
    #####sağ üst tablo-end#####
    
    #####sol alt tablo#####
    data=[["MAKER"],
          ["TYPE"]
          ]
    table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
    table.wrapOn(p, 30, h-280)
    table.drawOn(p, 30, h-280)
    
    if theRequest.vessel:
        imo = theRequest.vessel.imo
    else:
        imo = ""
    
    data=[[theRequest.maker],
          [theRequest.makerType],
          ]
    table = Table(data, colWidths=((w/2-35)/4)*3, rowHeights=tableRowHeight)
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, 30+((w/2-35)/4), h-280)
    table.drawOn(p, 30+((w/2-35)/4), h-280)
    #####sol alt tablo-end#####
    
    #####sağ alt tablo#####
    data=[["SERIAL"],
          ["CYL"]
          ]
    table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
    table.wrapOn(p, w/2+5, h-280)
    table.drawOn(p, w/2+5, h-280)
    
    if theRequest.vessel:
        vessel = theRequest.vessel
    else:
        vessel = ""
        
    data=[[""],
          [""]
          ]
    table = Table(data, colWidths=((w/2-35)/4)*3, rowHeights=tableRowHeight)
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, (w/2+5)+((w/2-35)/4), h-280)
    table.drawOn(p, (w/2+5)+((w/2-35)/4), h-280)
    #####sağ alt tablo-end#####
    
    #####parça sayısına göre sayfa dilimleme#####
    #standart ayar
    slice = 20
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
        
        #####sağ üst yazılar#####
        p.setFont('Inter-Bold', 7)
        p.drawString(420, h-50, "DOCUMENT NO")
        p.setFont('Inter', 7)
        p.drawString(480, h-50, ":" + str(orderConfirmation.orderConfirmationNo))
        p.setFont('Inter-Bold', 7)
        p.drawString(420, h-70, "PROJECT NO")
        p.setFont('Inter', 7)
        p.drawString(480, h-70, ":" + str(theRequest.requestNo))
        #####sağ üst yazılar-end#####
        
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
            if partsList[j].alternative:
                sequency = str(partsList[j].sequency) + "-A"
            else:
                sequency = str(partsList[j].sequency)
            data.append([sequency])
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleLeft)
        
        table.wrapOn(p, 30, th-285-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30, th-285-(len(data)*partsTableRowHeight))
        table1Length = table._colWidths[0]
        
        #sütun(tablo) 2
        data=[["Item"]]
        for part in partsList:
            data.append([part.inquiryPart.requestPart.part.partNo])
        table = Table(data, colWidths=((w-60)/100)*13, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleLeft)
        
        table.wrapOn(p, 30+table1Length, th-285-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length, th-285-(len(data)*partsTableRowHeight))
        table2Length = table._colWidths[0]
        
        #sütun(tablo) 3
        data=[["Description of Goods & Services"]]
        for part in partsList:
            data.append([part.inquiryPart.requestPart.part.description])
        table = Table(data, colWidths=((w-60)/100)*42, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleLeft)
        
        table.wrapOn(p, 30+table1Length+table2Length, th-285-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length, th-285-(len(data)*partsTableRowHeight))
        table3Length = table._colWidths[0]
        
        #sütun(tablo) 4
        data=[["Qty"]]
        for part in partsList:
            data.append([part.quantity])
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
        partsTableStyleRight
        table.setStyle(partsTableStyleRight)
        
        table.wrapOn(p, 30+table1Length+table2Length+table3Length, th-285-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length+table3Length, th-285-(len(data)*partsTableRowHeight))
        table4Length = table._colWidths[0]
        
        #sütun(tablo) 5
        data=[["Unit"]]
        for part in partsList:
            data.append([part.inquiryPart.requestPart.part.unit])
        table = Table(data, colWidths=((w-60)/100)*5, rowHeights=partsTableRowHeight)
        partsTableStyleRight
        table.setStyle(partsTableStyleRight)
        
        table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length, th-285-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length, th-285-(len(data)*partsTableRowHeight))
        table5Length = table._colWidths[0]
        
        #sütun(tablo) 6
        data=[["Unit Price"]]
        for part in partsList:
            data.append([str(round(part.unitPrice3,2)) + " " + orderConfirmation.quotation.currency.code])
        table = Table(data, colWidths=((w-60)/100)*15, rowHeights=partsTableRowHeight, hAlign="RIGHT")
        table.setStyle(partsTableStyleRight)
        
        table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length, th-285-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length, th-285-(len(data)*partsTableRowHeight))
        table6Length = table._colWidths[0]
        
        #sütun(tablo) 7
        data=[["Total Price"]]
        for part in partsList:
            data.append([str(round(part.totalPrice3,2)) + " " + orderConfirmation.quotation.currency.code])
        table = Table(data, colWidths=((w-60)/100)*15, rowHeights=partsTableRowHeight)
        table.setStyle(partsTableStyleRight)
        
        table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+table6Length, th-285-(len(data)*partsTableRowHeight))
        table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+table6Length, th-285-(len(data)*partsTableRowHeight))
        table7Length = table._colWidths[0]
        
        #sütun(tablo) total
        
        if pageNum == pageCount:
            subTotalPrice = 0
            totalPrice = 0
            
            for part in parts:
                subTotalPrice = subTotalPrice + part.totalPrice2
                totalPrice = totalPrice + part.totalPrice3
            
            try:
                discount = round(1-(totalPrice/subTotalPrice),2)
            except:
                discount = 0
                
            discountPrice  = round(subTotalPrice - totalPrice,2)
            
            dataNote=[[str(orderConfirmation.note)]]
            table = Table(dataNote, colWidths=((w-60)/100)*70, rowHeights=partsTableRowHeight*4)
            table.setStyle(tableRightStyle)
            
            table.wrapOn(p, 30, th-285-((len(data)+4)*partsTableRowHeight))
            table.drawOn(p, 30, th-285-((len(data)+4)*partsTableRowHeight))
            
            vatRate = orderConfirmation.vat
            
            if vatRate == 0:
                vatText = "KDV / VAT"
            else:
                if vatRate.is_integer():
                    vatText = "KDV " + str(int(vatRate)) + "% / VAT " + str(int(vatRate)) + "%"
                else:
                    vatText = "KDV " + str(vatRate) + "% / VAT " + str(vatRate) + "%"
            
            dataSubTotal=[["SUB TOTAL"],
                          ["DISCOUNT"],
                          [vatText],
                          ["NET TOTAL"]
                          ]
            table = Table(dataSubTotal, colWidths=((w-60)/100)*15, rowHeights=partsTableRowHeight)
            table.setStyle(totalLeftTableStyleLeft)
            
            table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length, th-285-((len(data)+4)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length, th-285-((len(data)+4)*partsTableRowHeight))
            tableTotalLeftLength = table._colWidths[0]
            
            dataSubTotal=[[str(round(partsTotalsDict["totalTotalPrice3"],2)) + " " + str(orderConfirmation.quotation.currency.code)],
                  [str(round(partsTotalsDict["totalDiscount"],2)) + " " + str(orderConfirmation.quotation.currency.code)],
                  [str(round(partsTotalsDict["totalVat"],2)) + " " + str(orderConfirmation.quotation.currency.code)],
                  [str(round(partsTotalsDict["totalFinal"],2)) + " " + str(orderConfirmation.quotation.currency.code)]]
            table = Table(dataSubTotal, colWidths=((w-60)/100)*15, rowHeights=partsTableRowHeight)
            table.setStyle(totalRightTableStyleRight)
            
            table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+tableTotalLeftLength, th-285-((len(data)+4)*partsTableRowHeight))
            table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+tableTotalLeftLength, th-285-((len(data)+4)*partsTableRowHeight))
            tableTotalLeftLength = table._colWidths[0]
        
        #####parts tablo-end#####
        
        #####önemli yazı#####
        p.setFont('Inter', 7)
        data=[("")]
        table = Table(data, colWidths=w-60, rowHeights=50)
        table.setStyle(TableStyle([
                                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                                ]))
        
        table.wrapOn(p, 30, 110)
        table.drawOn(p, 30, 110)
        
        p.setFont('Inter-Bold', 6)
        p.setFillColor(HexColor("#922724"))
        p.drawCentredString(w/2, 145, "According to SOLAS CHAPTER II-1 Part A-1 Regulation 3-5 , we hereby declare that the offered parts don't contain any asbestos material.")
        p.drawCentredString(w/2, 135, "Asbestos-Free certificates, if available, can be provided based on request.")
        p.setFillColor(HexColor("#000"))
        p.drawCentredString(w/2, 125, "This document contains confidental information belonging to ESMS and must not be disclosed to 3rd parties without permission.")
        
        p.drawCentredString(w/2, 115, "Cancellation of any confirmed order will result in additional fees (amount of the fees will be changed upon supplier desicion and total amount of order)")
        
        p.setFont('Inter', 7)
        #####önemli yazı-end#####
        
        ######sayfa altı########
        p.setStrokeColor(HexColor("#808080"))
        p.line(30, 100, w-30, 100)
        p.setFont('Inter-Bold', 7)
        p.drawString(30, 90, "ESMS DENİZCİLİK ENERJİ TAAHHÜT MÜHENDİSLİK SANAYİ VE TİC. A.Ş.")
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
        
        p.drawInlineImage(lrImg, 415, 46, width=150,height=50)
        
        p.line(30, 40, w-30, 40)
        p.setFont('Inter-Bold', 7)
        p.drawString(30, 30, str(orderConfirmation.quotation.inquiry.project.user.first_name) + " " + str(orderConfirmation.quotation.inquiry.project.user.last_name) + " / " + str(orderConfirmation.quotation.inquiry.project.user.profile.positionType))
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
