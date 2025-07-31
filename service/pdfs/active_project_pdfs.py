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
import logging

from ..models import Offer, OfferServiceCard, OfferExpense, OfferPart
from card.models import EnginePart

#####SETUP#####
def pageSettings(p, w, h, title):
    #başlık
    p.setFont('Inter', 18)
    p.setFillColor(HexColor("#9d2235"))
    p.drawCentredString(w/2, h-100, title)   

def pageTemplate(p, w, h, ystart,sourceCompany,sourceCompanyFormalName,sourceCompanyAddress,sourceCompanyPhone,sourceCompanyFax):
    #logo
    #esmsImg = Image.open(os.path.join(os.getcwd(), "static", "images", "esms-logo2.jpg"))
    esmsImg = Image.open(os.path.join(os.getcwd(),"media","source","companies",str(sourceCompany.id),str(sourceCompany.documentLogo.name.split('/')[-1])))
    
    p.drawInlineImage(esmsImg, 30, ystart-10, width=(esmsImg.size[0]/esmsImg.size[1])*40,height=40)
    
    ######sayfa altı########
    p.setStrokeColor(HexColor("#808080"))
    p.line(30, 100, w-30, 100)
    p.setFont('Inter-Bold', 7)
    p.drawString(30, 90, sourceCompanyFormalName)
    p.drawString(30, 70, "Office")
    p.setFont('Inter', 7)
    p.drawString(60, 70, sourceCompanyAddress)
    #p.drawString(60, 70, "No:126 57/C P.K. 34947 Tuzla İstanbul TR")
    p.setFont('Inter-Bold', 7)
    p.drawString(30, 60, "Tel")
    p.setFont('Inter', 7)
    p.drawString(60, 60, sourceCompanyPhone)
    p.setFont('Inter-Bold', 7)
    p.drawString(30, 50, "Fax")
    p.setFont('Inter', 7)
    p.drawString(60, 50, sourceCompanyFax)
    
    lrImg = Image.open(os.path.join(os.getcwd(), "static", "images", "sale", "lr-logo4.jpg"))
    
    p.drawInlineImage(lrImg, 415, 46, width=150,height=50)
    
    p.line(30, 40, w-30, 40)
    p.setFont('Inter-Bold', 7)
    #p.drawString(30, 30, str(offer.user.first_name) + " " + str(offer.user.last_name) + " / " + str(offer.user.profile.positionType))
    p.setFont('Inter-Bold', 7)
    p.drawString(310, 30, "Document Date: " + str(datetime.today().date().strftime("%d.%m.%Y")))
    ######sayfa altı-end########

def tableStyle(style):
    styles = {
        "tableLeftStyle" : TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                                        ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                                        ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                        ('TEXTCOLOR',(0,0), (-1,-1), colors.white),
                                        ('BACKGROUND',(0,0), (-1,-1), "#9d2235")
                               ]),
        "tableRightStyle" : TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                                        ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                                        ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                               ]),
        "partsTableStyleLeft" : TableStyle([('INNERGRID', (0,1), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
                                        ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
                                        ('BOX', (0,0), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
                                        ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                        ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 6),
                                        ('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
                                        ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                        ('ALIGN', (5, 0), (-1, -1), "RIGHT"),
                                        ('TEXTCOLOR',(0,1), (-1,1), colors.white),
                                        #('BACKGROUND',(0,0), (-1,0), "#009999"),
                                        ('BACKGROUND',(0,0), (-1,0), "rgba(0,56,101,0.40)"),
                                        ('BACKGROUND',(6,-1), (-1,-1), "rgba(0,56,101,0.40)"),
                                        ('INNERGRID', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('BOX', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('BACKGROUND',(0,1), (-1,1), "#003865"),
                                        ('VALIGN', (0, 0), (-1, -1), "TOP")
                                ]),
        "partsTableStyleLeftWOP" : TableStyle([('INNERGRID', (0,1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        #('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
                                        ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                        ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 6),
                                        #('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
                                        ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                        ('ALIGN', (5, 0), (-1, -1), "RIGHT"),
                                        ('TEXTCOLOR',(0,1), (-1,1), colors.white),
                                        #('BACKGROUND',(0,0), (-1,0), "#009999"),
                                        ('BACKGROUND',(0,0), (-1,0), "rgba(0,56,101,0.40)"),
                                        #('BACKGROUND',(6,-1), (-1,-1), "rgba(0,56,101,0.40)"),
                                        #('INNERGRID', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        #('BOX', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('BACKGROUND',(0,1), (-1,1), "#003865"),
                                        ('VALIGN', (0, 0), (-1, -1), "TOP")
                                ]),
        "partsTableStyleRight" : TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('FONT', (0, 0), (-1, -1), 'Inter', 7),
                                        ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 7),
                                        ('ALIGN', (0, 0), (-1, -1), "RIGHT"),
                                        ('TEXTCOLOR',(0,0), (-1,0), colors.white),
                                        ('BACKGROUND',(0,0), (-1,0), "#003865")
                                ]),
        "partsTableStyleCenter" : TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('FONT', (0, 0), (-1, -1), 'Inter', 7),
                                        ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 7),
                                        ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                                        ('TEXTCOLOR',(0,0), (-1,0), colors.white),
                                        ('BACKGROUND',(0,0), (-1,0), "#003865")
                                ]),
        "totalLeftTableStyleLeft" : TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                        ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                        ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                        ('TEXTCOLOR',(0,0), (-1,-1), colors.white),
                                        ('BACKGROUND',(0,0), (-1,-1), "#003865")
                                ]),
        "totalRightTableStyleRight" : TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "RIGHT")
                                ])
    }

    return styles.get(style, "Invalid Choice")

def subLine(p, text, line_height):
    text = text
    #alt satır komutu
    lines = text.replace("\r\n", "\n")
    lines = lines.split('\n')
    line_height = line_height  # İsteğe bağlı, satır yüksekliği
    current_y = current_y

    for line in lines:
        p.drawString(35, current_y, line)
        current_y = current_y - line_height

def totalTable(p, w, h, th, tableTotalRowHeight, tableSpace, partsTotalsDict, currency):
    dataSubTotal=[["SUB TOTAL"],
                          ["DISCOUNT"],
                          ["NET TOTAL"]
                          ]
    tableTotal = Table(dataSubTotal, colWidths=[((w-60)/100)*12, ((w-60)/100)*12], rowHeights=13)
    tableTotal.setStyle(tableStyle("totalLeftTableStyleLeft"))
    
    tableTotal.wrapOn(p, 30, -99999999)
    tableTotal.drawOn(p, 30, -99999999)
    if th == h+250:
        tableTotal.wrapOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4), th-215-tableTotalRowHeight-sum(tableTotal._rowHeights)-tableSpace)
        tableTotal.drawOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4), th-215-tableTotalRowHeight-sum(tableTotal._rowHeights)-tableSpace)
    else:
        tableTotal.wrapOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4), th-215-tableTotalRowHeight-sum(tableTotal._rowHeights)-tableSpace)
        tableTotal.drawOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4), th-215-tableTotalRowHeight-sum(tableTotal._rowHeights)-tableSpace)
    tableTotalLeftLength = tableTotal._colWidths[0]
    
    # Para miktarını belirtilen formatta gösterme
    totalTotalPrice3Fixed = "{:,.2f}".format(round(partsTotalsDict["totalTotalPrice3"],2))
    totalDiscountFixed = "{:,.2f}".format(round(partsTotalsDict["totalDiscount"],2))
    totalFinalFixed = "{:,.2f}".format(round(partsTotalsDict["totalFinal"],2))
    # Nokta ile virgülü değiştirme
    totalTotalPrice3Fixed = totalTotalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
    totalDiscountFixed = totalDiscountFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
    totalFinalFixed = totalFinalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
    
    dataSubTotal=[[str(totalTotalPrice3Fixed) + " " + str(currency)],
                    [str(totalDiscountFixed) + " " + str(currency)],
                    [str(totalFinalFixed) + " " + str(currency)]
                    ]
    
    tableTotal = Table(dataSubTotal, colWidths=[((w-60)/100)*12, ((w-60)/100)*12], rowHeights=13)
    tableTotal.setStyle(tableStyle("totalRightTableStyleRight"))
    
    tableTotal.wrapOn(p, 30, -99999999)
    tableTotal.drawOn(p, 30, -99999999)
    if th == h+250:
        tableTotal.wrapOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4)+(((w-60)/100)*12), th-215-tableTotalRowHeight-sum(tableTotal._rowHeights)-tableSpace)
        tableTotal.drawOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4)+(((w-60)/100)*12), th-215-tableTotalRowHeight-sum(tableTotal._rowHeights)-tableSpace)
    else:
        tableTotal.wrapOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4)+(((w-60)/100)*12), th-215-tableTotalRowHeight-sum(tableTotal._rowHeights)-tableSpace)
        tableTotal.drawOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4)+(((w-60)/100)*12), th-215-tableTotalRowHeight-sum(tableTotal._rowHeights)-tableSpace)
    tableTotalLeftLength = tableTotal._colWidths[0] 
#####SETUP-END#####

#####PDF#####
def activeProjectPdf(offer, sourceCompany):
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
            
        title = "PROJECT SUMMARY"
        #quotation içerisindeki part listesi
        #parts = orderConfirmation.quotation.quotationpart_set.select_related("inquiryPart")
        serviceCards = OfferServiceCard.objects.filter(offer = offer, extra = False).order_by("id")
        serviceCardsExtra = OfferServiceCard.objects.filter(offer = offer, extra = True).order_by("id")
        expenses = OfferExpense.objects.filter(offer = offer).order_by("id")
        parts = OfferPart.objects.filter(offer = offer).order_by("id")
        
        items = []
        serviceCardsList = []
        for serviceCard in serviceCards:
            items.append({"id" : serviceCard.id,
                        "name":serviceCard.serviceCard.code,
                        "description" : serviceCard.serviceCard.name,
                        "remark" : serviceCard.remark,
                        "quantity" : serviceCard.quantity,
                        "unit" : serviceCard.serviceCard.unit,
                        "unitPrice" : serviceCard.unitPrice3,
                        "totalPrice" : serviceCard.totalPrice,
                        "currency" : offer.currency.code,
                        "type" : "service_card",
                        "extra" : False
                        })
        for serviceCardExtra in serviceCardsExtra:
            items.append({"id" : serviceCardExtra.id,
                        "name":serviceCardExtra.serviceCard.code,
                        "description" : serviceCardExtra.serviceCard.name,
                        "remark" : serviceCardExtra.remark,
                        "quantity" : serviceCardExtra.quantity,
                        "unit" : serviceCardExtra.serviceCard.unit,
                        "unitPrice" : serviceCardExtra.unitPrice3,
                        "totalPrice" : serviceCardExtra.totalPrice,
                        "currency" : offer.currency.code,
                        "type" : "service_card_extra",
                        "extra" : True
                        })
        for expense in expenses:
            items.append({"id" : expense.id,
                        "name":expense.expense.code,
                        "description" : expense.expense.name,
                        "remark" : "",
                        "quantity" : expense.quantity,
                        "unit" : expense.expense.unit,
                        "unitPrice" : expense.unitPrice,
                        "totalPrice" : expense.totalPrice,
                        "currency" : offer.currency.code,
                        "type" : "expense",
                        "extra" : False
                        })
        for part in parts:
            items.append({"id" : part.id,
                        "name":part.part.partNo,
                        "description" : part.part.description,
                        "remark" : part.remark,
                        "quantity" : part.quantity,
                        "unit" : part.part.unit,
                        "unitPrice" : part.unitPrice,
                        "totalPrice" : part.totalPrice,
                        "currency" : offer.currency.code,
                        "type" : "part",
                        "extra" : False
                        })

        partsTotalsDict = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
            
        partsTotalDict = 0
        
        for item in items:
            partsTotalDict  = partsTotalDict + item["unitPrice"]
            partsTotalsDict["totalUnitPrice1"] = partsTotalsDict["totalUnitPrice1"] + item["unitPrice"]
            partsTotalsDict["totalUnitPrice2"] = partsTotalsDict["totalUnitPrice2"] + item["unitPrice"]
            partsTotalsDict["totalUnitPrice3"] = partsTotalsDict["totalUnitPrice3"] + item["unitPrice"]
            partsTotalsDict["totalTotalPrice1"] = partsTotalsDict["totalTotalPrice1"] + item["totalPrice"]
            partsTotalsDict["totalTotalPrice2"] = partsTotalsDict["totalTotalPrice2"] + item["totalPrice"]
            partsTotalsDict["totalTotalPrice3"] = partsTotalsDict["totalTotalPrice3"] + item["totalPrice"]
        
        if offer.discountAmount > 0:
            partsTotalsDict["totalDiscount"] = offer.discountAmount
        else:
            partsTotalsDict["totalDiscount"] = partsTotalsDict["totalTotalPrice3"] * (offer.discount/100)
        partsTotalsDict["totalFinal"] = partsTotalsDict["totalTotalPrice3"] - partsTotalsDict["totalDiscount"]
        
        #page settings (main folder name, sub folder name, file name)
        #pageSettings("service", "active_project", offer.offerNo)
        
        #standart ayar
        buffer = io.BytesIO()
        
        #dosyanın kaydedileceği konum
        folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "service", "active_project", "documents")
        
        #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
            
        #font ayarları
        rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
        pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
        
        #standart ayar
        p = canvas.Canvas(folderPath + "/" + offer.offerNo + ".pdf", pagesize = A4)
        
        #standart ayar
        w, h = A4
        print(f"widht: {w}")
        ystart = 780
        
        #####satır yükseklii kontrol#####
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        descriptionLengths = []
        for item in items:
            descriptionLengths.append(len(item["description"]))
        #print((max(descriptionLengths)/70)*20)
        #####satır yükseklii kontrol-end#####
        
        #tablo satır yükseklikleri
        tableRowHeight = 12
        partsTableRowHeight = (max(descriptionLengths)/70)*20
        
        #?
        p.setLineWidth(0.5)
        
        #sayfa ayarı
        pageSettings(p, w, h, title)
        
        #company
        p.setFillColor(HexColor("#000"))
        p.setFont('Inter-Bold', 6)
        p.drawString(35, h-130, "TO:")
        p.setFont('Inter', 6)
        #####customer with multiple lines#####
        #alt satır komutu
        lines = offer.customer.name.replace("\r\n", "\n")
        lines = lines.split('\n')
        line_height = 8  # İsteğe bağlı, satır yüksekliği
        current_y = h-130

        for line in lines:
            p.drawString(50, current_y, line)
            current_y = current_y - line_height
        #####customer with multiple lines-end#####
        
        #####address with multiple lines#####
        #alt satır komutu
        if offer.customer:
            customerName = offer.customer.name
            if offer.customer.address:
                if offer.customer.country:
                    customerCountry = offer.customer.country.international_formal_name
                else:
                    customerCountry = ""
                if offer.customer.city:
                    customerCity = offer.customer.city.name
                else:
                    customerCity = ""
                customerAddress = offer.customer.address + " " + customerCity + "/" + customerCountry
            else:
                if offer.customer.country:
                    customerCountry = offer.customer.country.international_formal_name
                else:
                    customerCountry = ""
                if offer.customer.city:
                    customerCity = offer.customer.city.name
                else:
                    customerCity = ""
                customerAddress = customerCity + "/" + customerCountry
        else:    
            customerName = ""
            customerAddress = ""
            
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        customerAddress = customerAddress.replace("\r\n", "\n")
        customerAddress = customerAddress.replace("\n", " ")
        newCustomerAddress = ""
        for i in range(0, len(customerAddress), 100):
            chunk = customerAddress[i:i+100]
            if len(chunk) < 100:
                newCustomerAddress += chunk
            else:
                space_index = chunk.rfind(' ')
                if space_index != -1:
                    newCustomerAddress += chunk[:space_index] + '\n'
                    if space_index + 1 < len(chunk):
                        newCustomerAddress += chunk[space_index+1:]
                else:
                    newCustomerAddress += chunk
        #alt satır komutu
        lines = newCustomerAddress.replace("\r\n", "\n")
        lines = lines.split('\n')
        line_height = 10  # İsteğe bağlı, satır yüksekliği
        #current_y = h-130

        for line in lines:
            p.drawString(35, current_y, line)
            current_y = current_y - line_height
        #####address with multiple lines-end#####
        
        #####person with multiple lines#####
        if offer.person:
            if offer.person.name:
                person = offer.person.name
                #alt satır komutu
                lines = person.replace("\r\n", "\n")
                lines = lines.split('\n')
                line_height = 8  # İsteğe bağlı, satır yüksekliği
                current_y = current_y

                for line in lines:
                    p.drawString(35, current_y, line)
                    current_y = current_y - line_height
        #####person with multiple lines-end#####
        
        #####title with multiple lines#####
        if offer.person:
            if offer.person.title:
                title = offer.person.title
                #alt satır komutu
                lines = title.replace("\r\n", "\n")
                lines = lines.split('\n')
                line_height = 8  # İsteğe bağlı, satır yüksekliği
                current_y = current_y

                for line in lines:
                    p.drawString(35, current_y, line)
                    current_y = current_y - line_height
        #####title with multiple lines-end#####
        
        #####email with multiple lines#####
        if offer.person:
            if offer.person.email:
                email = offer.person.email
                #alt satır komutu
                lines = email.replace("\r\n", "\n")
                lines = lines.split('\n')
                line_height = 8  # İsteğe bağlı, satır yüksekliği
                current_y = current_y

                for line in lines:
                    p.drawString(35, current_y, line)
                    current_y = current_y - line_height
        #####email with multiple lines-end#####
        
        #####sağ üst tablo#####
        data=[["OUR REF"],
            ["YOUR REF"],
            ["VALIDITY"],
            ["MAKER"],
            ["TYPE"],
            ["SERIAL"],
            ["CYL"]
            ]
        table = Table(data, colWidths=(w/2-35)/3, rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableLeftStyle"))
        
        table.wrapOn(p, w/2+5, h-210)
        table.drawOn(p, w/2+5, h-210)
            
        if offer.equipment:
            maker = offer.equipment.maker.name
            if offer.equipment.makerType:
                makerType = offer.equipment.makerType.type
            else:
                makerType = ""
            serial = offer.equipment.serialNo
            cyl = offer.equipment.cyl
        else:
            maker = ""
            makerType = ""
            serial = ""
            cyl = ""
        
        
        data=[[offer.offerNo],
            [offer.customerRef],
            [offer.period],
            [maker],
            [makerType],
            [serial],
            [cyl]
            ]
        table = Table(data, colWidths=((w/2-35)/3)*2, rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableRightStyle"))
        
        table.wrapOn(p, (w/2+5)+(((w/2-35)/3)), h-210)
        table.drawOn(p, (w/2+5)+(((w/2-35)/3)), h-210)
        #####sağ üst tablo-end#####
        
        #####sol üst tablo sol#####
        data=[["VESSEL / PLANT"],
            ["LOA"],
            ["BEAM"]
            ]
        table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableLeftStyle"))
        
        table.wrapOn(p, 30, h-210)
        table.drawOn(p, 30, h-210)
        
        if offer.vessel:
            vessel = offer.vessel.name
            loa = offer.vessel.loa
            beam = offer.vessel.beam
            imo = offer.vessel.imo
            draught = offer.vessel.draught
            building = offer.vessel.building
        else:
            vessel = ""
            loa = ""
            beam = ""
            imo = ""
            draught = ""
            building = ""
        
        
        data=[[vessel],
            [loa],
            [beam]
            ]
        table = Table(data, colWidths=((w/2-35)/4), rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableRightStyle"))
        
        table.wrapOn(p, 30+(((w/2-35)/4)), h-210)
        table.drawOn(p, 30+(((w/2-35)/4)), h-210)
        #####sol üst tablo sol-end#####
        
        #####sol üst tablo sağ#####
        data=[["IMO"],
            ["DRAUGHT"],
            ["B.YEAR"]
            ]
        table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableLeftStyle"))
        
        table.wrapOn(p, 30+(((w/2-35)/4)*2), h-210)
        table.drawOn(p, 30+(((w/2-35)/4)*2), h-210)
        
        if offer.vessel:
            vessel = offer.vessel.name
            loa = offer.vessel.loa
            beam = offer.vessel.beam
            imo = offer.vessel.imo
            draught = offer.vessel.draught
            building = offer.vessel.building
        else:
            vessel = ""
            loa = ""
            beam = ""
            imo = ""
            draught = ""
            building = ""
        
        
        data=[[imo],
            [draught],
            [building]
            ]
        table = Table(data, colWidths=((w/2-35)/4), rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableRightStyle"))
        
        table.wrapOn(p, 30+(((w/2-35)/4)*3), h-210)
        table.drawOn(p, 30+(((w/2-35)/4)*3), h-210)
        #####sol üst tablo sağ-end#####
        
        #####parça sayısına göre sayfa dilimleme#####
        #standart ayar
        slice = 22
        pageNum = 1
        pageCount = len(items) // slice
        #standart ayar
        if len(items) % slice != 0:
            pageCount = pageCount + 1
        #standart ayar
        serviceCardsTotal = 0
        serviceCardsSequency = 0
        serviceCardsExtraTotal = 0
        serviceCardsExtraSequency = 0
        expenseTotal = 0
        expenseSequency = 0
        partTotal = 0
        partSequency = 0
        
        for i in range(0, len(items), slice):
            tableTotalRowHeight = 0
            tableSpace = 0
            #standart ayar
            partsList = items[i:i+slice]
            #standart ayar
            pageTemplate(p, w, h, ystart,sourceCompany,sourceCompanyFormalName,sourceCompanyAddress,sourceCompanyPhone,sourceCompanyFax)
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
            p.drawString(450, h-50, "DATE")
            p.setFont('Inter', 7)
            p.drawString(480, h-50, ":" + str(offer.offerDate.strftime("%d.%m.%Y")))
            #####sağ üst yazılar-end#####
            
            if i >= slice:
                th = h+100
            else:
                th = h
            
            #####parts tablo#####
            
            ##########service card talo##########
            data=[["Actions In Offer"],
                ["Line", "Item", "Description", "Qty", "Unit", "Unit Price", "Total Price"]
                ]
            rowLengths = []
            serviceCardList = []
            for j in range(len(partsList)):
                if partsList[j]["type"] == "service_card":
                    serviceCardList.append(partsList[j])
                    #partsList[j]["description"] = partsList[j]["description"].replace("\r\n", " ")
                    #####bdescription with multiple lines#####
                    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
                    newDescription = "" 
                    for k in range(0, len(partsList[j]["description"]), 80):
                        chunk = partsList[j]["description"][k:k+80]
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newDescription += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newDescription += chunk[space_index+1:]
                        else:
                            newDescription += chunk
                    #alt satır komutu
                    #newDescription = newDescription.replace("\r\n", " ")
                    lines = newDescription.replace("\r\n", "\n")
                    lines = lines.split('\n')
                    #####bdescription with multiple lines-end#####
                    
                    if partsList[j]["remark"]:
                        partRemark = " - " + str(partsList[j]["remark"])
                    else:
                        partRemark = ""
                    
                    # Para miktarını belirtilen formatta gösterme
                    unitPrice3Fixed = "{:,.2f}".format(round(partsList[j]["unitPrice"],2))
                    totalPrice3Fixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                    # Nokta ile virgülü değiştirme
                    unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    
                    rowLengths.append(partsList[j])
                    
                    serviceCardsSequency = serviceCardsSequency + 1
                    data.append([serviceCardsSequency, partsList[j]["name"], partsList[j]["description"] + str(partRemark), partsList[j]["quantity"], partsList[j]["unit"], str(unitPrice3Fixed) + " " + str(partsList[j]["currency"]), str(totalPrice3Fixed) + " " + str(partsList[j]["currency"])])
                    serviceCardsTotal = serviceCardsTotal + partsList[j]["totalPrice"]
            
            # Para miktarını belirtilen formatta gösterme
            serviceCardsTotalFixed = "{:,.2f}".format(round(serviceCardsTotal,2))
            # Nokta ile virgülü değiştirme
            serviceCardsTotalFixed = serviceCardsTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            data.append(["", "", "", "", "", "", str(serviceCardsTotalFixed) + " " + str(offer.currency.code)])
            table1 = Table(data, colWidths=[((w-60)/100)*5 , ((w-60)/100)*11, ((w-60)/100)*52 , ((w-60)/100)*4 , ((w-60)/100)*4 , ((w-60)/100)*12 , ((w-60)/100)*12])
            table1.setStyle(tableStyle("partsTableStyleLeft"))

            
            table1.wrapOn(p, 30, -99999999)
            table1.drawOn(p, 30, -99999999)
            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
            table1TotalRowHeight = sum(table1._rowHeights)
            if len(serviceCardList) > 0:
                tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                table1.wrapOn(p, 30, th-215-tableTotalRowHeight)
                table1.drawOn(p, 30, th-215-tableTotalRowHeight)
                tableSpace = tableSpace + 10
            ##########service card talo-end##########
            
            ##########service card extra talo##########
            data=[["Actions In Extra"],
                ["Line", "Item", "Description", "Qty", "Unit", "Unit Price", "Total Price"]
                ]
            rowLengths = []
            serviceCardExtraList = []
            for j in range(len(partsList)):
                if partsList[j]["type"] == "service_card_extra":
                    serviceCardExtraList.append(partsList[j])
                    #partsList[j]["description"] = partsList[j]["description"].replace("\r\n", " ")
                    #####bdescription with multiple lines#####
                    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
                    newDescription = "" 
                    for k in range(0, len(partsList[j]["description"]), 80):
                        chunk = partsList[j]["description"][k:k+80]
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newDescription += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newDescription += chunk[space_index+1:]
                        else:
                            newDescription += chunk
                            print(newDescription)
                    #alt satır komutu
                    #newDescription = newDescription.replace("\r\n", " ")
                    lines = newDescription.replace("\r\n", "\n")
                    lines = lines.split('\n')
                    #####bdescription with multiple lines-end#####
                    
                    if partsList[j]["remark"]:
                        partRemark = " - " + str(partsList[j]["remark"])
                    else:
                        partRemark = ""
                    
                    # Para miktarını belirtilen formatta gösterme
                    unitPrice3Fixed = "{:,.2f}".format(round(partsList[j]["unitPrice"],2))
                    totalPrice3Fixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                    # Nokta ile virgülü değiştirme
                    unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    
                    rowLengths.append(len(lines))
                    serviceCardsExtraSequency = serviceCardsExtraSequency + 1
                    data.append([serviceCardsExtraSequency, partsList[j]["name"], partsList[j]["description"] + str(partRemark), partsList[j]["quantity"], partsList[j]["unit"], str(unitPrice3Fixed) + " " + str(partsList[j]["currency"]), str(totalPrice3Fixed) + " " + str(partsList[j]["currency"])])
                    serviceCardsExtraTotal = serviceCardsExtraTotal + partsList[j]["totalPrice"]
            
            # Para miktarını belirtilen formatta gösterme
            serviceCardsExtraTotalFixed = "{:,.2f}".format(round(serviceCardsExtraTotal,2))
            # Nokta ile virgülü değiştirme
            serviceCardsExtraTotalFixed = serviceCardsExtraTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            data.append(["", "", "", "", "", "", str(serviceCardsExtraTotalFixed) + " " + str(offer.currency.code)])      
            table2 = Table(data, colWidths=[((w-60)/100)*5 , ((w-60)/100)*11, ((w-60)/100)*52 , ((w-60)/100)*4 , ((w-60)/100)*4 , ((w-60)/100)*12 , ((w-60)/100)*12])
            table2.setStyle(tableStyle("partsTableStyleLeft"))

            
            table2.wrapOn(p, 30, -99999999)
            table2.drawOn(p, 30, -99999999)
            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
            table2TotalRowHeight = sum(table2._rowHeights)
            if len(serviceCardExtraList) > 0:
                tableTotalRowHeight = tableTotalRowHeight + sum(table2._rowHeights)
                table2.wrapOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                table2.drawOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                tableSpace = tableSpace + 10
                print("space: " + str(tableSpace))
            ##########service card extra talo-end##########
            
            ##########expense talo##########
            data=[["Expenses"],
                ["Line", "Item", "Description", "Qty", "Unit", "Unit Price", "Total Price"]
                ]
            rowLengths = []
            expenseList = []
            for j in range(len(partsList)):
                if partsList[j]["type"] == "expense":
                    expenseList.append(partsList[j])
                    #partsList[j]["description"] = partsList[j]["description"].replace("\r\n", " ")
                    #####bdescription with multiple lines#####
                    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
                    newDescription = "" 
                    for k in range(0, len(partsList[j]["description"]), 80):
                        chunk = partsList[j]["description"][k:k+80]
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newDescription += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newDescription += chunk[space_index+1:]
                        else:
                            newDescription += chunk
                            print(newDescription)
                    #alt satır komutu
                    #newDescription = newDescription.replace("\r\n", " ")
                    lines = newDescription.replace("\r\n", "\n")
                    lines = lines.split('\n')
                    #####bdescription with multiple lines-end#####
                    
                    # Para miktarını belirtilen formatta gösterme
                    unitPrice3Fixed = "{:,.2f}".format(round(partsList[j]["unitPrice"],2))
                    totalPrice3Fixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                    # Nokta ile virgülü değiştirme
                    unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    
                    rowLengths.append(len(lines))
                    expenseSequency = expenseSequency + 1
                    data.append([expenseSequency, partsList[j]["name"], partsList[j]["description"], partsList[j]["quantity"], partsList[j]["unit"], str(unitPrice3Fixed) + " " + str(partsList[j]["currency"]), str(totalPrice3Fixed) + " " + str(partsList[j]["currency"])])
                    expenseTotal = expenseTotal + partsList[j]["totalPrice"]
            
            # Para miktarını belirtilen formatta gösterme
            expenseTotalFixed = "{:,.2f}".format(round(expenseTotal,2))
            # Nokta ile virgülü değiştirme
            expenseTotalFixed = expenseTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            data.append(["", "", "", "", "", "", str(expenseTotalFixed) + " " + str(offer.currency.code)])      
            table3 = Table(data, colWidths=[((w-60)/100)*5 , ((w-60)/100)*11, ((w-60)/100)*52 , ((w-60)/100)*4 , ((w-60)/100)*4 , ((w-60)/100)*12 , ((w-60)/100)*12])
            table3.setStyle(tableStyle("partsTableStyleLeft"))

            
            table3.wrapOn(p, 30, -99999999)
            table3.drawOn(p, 30, -99999999)
            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
            table3TotalRowHeight = sum(table3._rowHeights)
            if len(expenseList) > 0:
                tableTotalRowHeight = tableTotalRowHeight + sum(table3._rowHeights)
                table3.wrapOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                table3.drawOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                print("space: " + str(tableSpace))
                tableSpace = tableSpace + 10
            ##########expensetalo-end##########
            
            ##########part talo##########
            data=[["Materials"],
                ["Line", "Item", "Description", "Qty", "Unit", "Unit Price", "Total Price"]
                ]
            rowLengths = []
            partList = []
            for j in range(len(partsList)):
                if partsList[j]["type"] == "part":
                    partList.append(partsList[j])
                    #partsList[j]["description"] = partsList[j]["description"].replace("\r\n", " ")
                    #####bdescription with multiple lines#####
                    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
                    newDescription = "" 
                    for k in range(0, len(partsList[j]["description"]), 80):
                        chunk = partsList[j]["description"][k:k+80]
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newDescription += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newDescription += chunk[space_index+1:]
                        else:
                            newDescription += chunk
                            print(newDescription)
                    #alt satır komutu
                    #newDescription = newDescription.replace("\r\n", " ")
                    lines = newDescription.replace("\r\n", "\n")
                    lines = lines.split('\n')
                    #####bdescription with multiple lines-end#####
                    
                    if partsList[j]["remark"]:
                        partRemark = " - " + str(partsList[j]["remark"])
                    else:
                        partRemark = ""
                    
                    # Para miktarını belirtilen formatta gösterme
                    unitPrice3Fixed = "{:,.2f}".format(round(partsList[j]["unitPrice"],2))
                    totalPrice3Fixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                    # Nokta ile virgülü değiştirme
                    unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    
                    rowLengths.append(len(lines))
                    partSequency = partSequency + 1
                    data.append([partSequency, partsList[j]["name"], str(partsList[j]["description"]) + str(partRemark), partsList[j]["quantity"], partsList[j]["unit"], str(unitPrice3Fixed) + " " + str(partsList[j]["currency"]), str(totalPrice3Fixed) + " " + str(partsList[j]["currency"])])
                    partTotal = partTotal + partsList[j]["totalPrice"]
            
            # Para miktarını belirtilen formatta gösterme
            partTotalFixed = "{:,.2f}".format(round(partTotal,2))
            # Nokta ile virgülü değiştirme
            partTotalFixed = partTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            data.append(["", "", "", "", "", "", str(partTotalFixed) + " " + str(offer.currency.code)])      
            table = Table(data, colWidths=[((w-60)/100)*5 , ((w-60)/100)*11, ((w-60)/100)*52 , ((w-60)/100)*4 , ((w-60)/100)*4 , ((w-60)/100)*12 , ((w-60)/100)*12])
            table.setStyle(tableStyle("partsTableStyleLeft"))

            
            table.wrapOn(p, 30, -99999999)
            table.drawOn(p, 30, -99999999)
            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
            #tableTotalRowHeight = sum(table1._rowHeights)+sum(table2._rowHeights)+sum(table3._rowHeights)+sum(table._rowHeights)
            if len(partList) > 0:
                tableTotalRowHeight = tableTotalRowHeight + sum(table._rowHeights)
                table.wrapOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                table.drawOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                tableSpace = tableSpace + 10
                
            ##########part tablo-end##########
            
            if pageNum == pageCount:
                #total tablo
                totalTable(p, w, h, th, tableTotalRowHeight, tableSpace, partsTotalsDict, offer.currency.code)

            p.setFont('Inter', 7)
            #####önemli yazı-end#####
            
            #####sayfa numarası#####
            if len(items) > slice:
                p.setFont('Inter', 7)
                p.drawCentredString(w/2, 10, str(pageNum) + "/" + str(pageCount))
                pageNum = pageNum + 1
            #####sayfa numarası-end#####
            
            p.showPage()
        
        p.save()
    except Exception as e:
        logger.exception(e)
def activeProjectPdfWithoutPrice(offer, sourceCompany):
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
            
        title = "PROJECT SUMMARY"
        #quotation içerisindeki part listesi
        #parts = orderConfirmation.quotation.quotationpart_set.select_related("inquiryPart")
        serviceCards = OfferServiceCard.objects.filter(offer = offer, extra = False).order_by("id")
        serviceCardsExtra = OfferServiceCard.objects.filter(offer = offer, extra = True).order_by("id")
        expenses = OfferExpense.objects.filter(offer = offer).order_by("id")
        parts = OfferPart.objects.filter(offer = offer).order_by("id")
        
        items = []
        serviceCardsList = []
        for serviceCard in serviceCards:
            items.append({"id" : serviceCard.id,
                        "name":serviceCard.serviceCard.code,
                        "description" : serviceCard.serviceCard.name,
                        "remark" : "",
                        "quantity" : serviceCard.quantity,
                        "unit" : serviceCard.serviceCard.unit,
                        "unitPrice" : serviceCard.unitPrice3,
                        "totalPrice" : serviceCard.totalPrice,
                        "currency" : offer.currency.code,
                        "type" : "service_card",
                        "extra" : False
                        })
        for serviceCardExtra in serviceCardsExtra:
            items.append({"id" : serviceCardExtra.id,
                        "name":serviceCardExtra.serviceCard.code,
                        "description" : serviceCardExtra.serviceCard.name,
                        "remark" : "",
                        "quantity" : serviceCardExtra.quantity,
                        "unit" : serviceCardExtra.serviceCard.unit,
                        "unitPrice" : serviceCardExtra.unitPrice3,
                        "totalPrice" : serviceCardExtra.totalPrice,
                        "currency" : offer.currency.code,
                        "type" : "service_card_extra",
                        "extra" : True
                        })
        for expense in expenses:
            items.append({"id" : expense.id,
                        "name":expense.expense.code,
                        "description" : expense.expense.name,
                        "remark" : "",
                        "quantity" : expense.quantity,
                        "unit" : expense.expense.unit,
                        "unitPrice" : expense.unitPrice,
                        "totalPrice" : expense.totalPrice,
                        "currency" : offer.currency.code,
                        "type" : "expense",
                        "extra" : False
                        })
        for part in parts:
            items.append({"id" : part.id,
                        "name":part.part.partNo,
                        "description" : part.part.description,
                        "remark" : "",
                        "quantity" : part.quantity,
                        "unit" : part.part.unit,
                        "unitPrice" : part.unitPrice,
                        "totalPrice" : part.totalPrice,
                        "currency" : offer.currency.code,
                        "type" : "part",
                        "extra" : False
                        })

        partsTotalsDict = {"totalUnitPrice1":0,"totalUnitPrice2":0,"totalUnitPrice3":0,"totalTotalPrice1":0,"totalTotalPrice2":0,"totalTotalPrice3":0,"totalProfit":0,"totalDiscount":0,"totalFinal":0}
            
        partsTotalDict = 0
        
        for item in items:
            partsTotalDict  = partsTotalDict + item["unitPrice"]
            partsTotalsDict["totalUnitPrice1"] = partsTotalsDict["totalUnitPrice1"] + item["unitPrice"]
            partsTotalsDict["totalUnitPrice2"] = partsTotalsDict["totalUnitPrice2"] + item["unitPrice"]
            partsTotalsDict["totalUnitPrice3"] = partsTotalsDict["totalUnitPrice3"] + item["unitPrice"]
            partsTotalsDict["totalTotalPrice1"] = partsTotalsDict["totalTotalPrice1"] + item["totalPrice"]
            partsTotalsDict["totalTotalPrice2"] = partsTotalsDict["totalTotalPrice2"] + item["totalPrice"]
            partsTotalsDict["totalTotalPrice3"] = partsTotalsDict["totalTotalPrice3"] + item["totalPrice"]
        
        if offer.discountAmount > 0:
            partsTotalsDict["totalDiscount"] = offer.discountAmount
        else:
            partsTotalsDict["totalDiscount"] = partsTotalsDict["totalTotalPrice3"] * (offer.discount/100)
        partsTotalsDict["totalFinal"] = partsTotalsDict["totalTotalPrice3"] - partsTotalsDict["totalDiscount"]
        
        #page settings (main folder name, sub folder name, file name)
        #pageSettings("service", "active_project", offer.offerNo)
        
        #standart ayar
        buffer = io.BytesIO()
        
        #dosyanın kaydedileceği konum
        folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "service", "active_project", "documents")
        
        #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
            
        #font ayarları
        rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
        pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
        
        #standart ayar
        p = canvas.Canvas(folderPath + "/" + offer.offerNo + "-without-price.pdf", pagesize = A4)
        
        #standart ayar
        w, h = A4
        
        ystart = 780
        
        #####satır yükseklii kontrol#####
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        descriptionLengths = []
        for item in items:
            descriptionLengths.append(len(item["description"]))
        #print((max(descriptionLengths)/70)*20)
        #####satır yükseklii kontrol-end#####
        
        #tablo satır yükseklikleri
        tableRowHeight = 12
        partsTableRowHeight = (max(descriptionLengths)/70)*20
        
        #?
        p.setLineWidth(0.5)
        
        #sayfa ayarı
        pageSettings(p, w, h, title)
        
        #company
        p.setFillColor(HexColor("#000"))
        p.setFont('Inter-Bold', 6)
        p.drawString(35, h-130, "TO:")
        p.setFont('Inter', 6)
        #####customer with multiple lines#####
        #alt satır komutu
        lines = offer.customer.name.replace("\r\n", "\n")
        lines = lines.split('\n')
        line_height = 8  # İsteğe bağlı, satır yüksekliği
        current_y = h-130

        for line in lines:
            p.drawString(50, current_y, line)
            current_y = current_y - line_height
        #####customer with multiple lines-end#####
        
        #####address with multiple lines#####
        #alt satır komutu
        if offer.customer:
            customerName = offer.customer.name
            if offer.customer.address:
                customerAddress = offer.customer.address
                if offer.customer.city:
                    customerCity = offer.customer.city.name
                    customerAddress = customerAddress + " " + customerCity + " /"
                if offer.customer.country:
                    customerCountry = offer.customer.country.international_formal_name
                    customerAddress = customerAddress + " " + customerCountry
            else:
                customerAddress = ""
                if offer.customer.city:
                    customerCity = offer.customer.city.name
                    customerAddress = customerAddress + " " + customerCity + " /"
                if offer.customer.country:
                    customerCountry = offer.customer.country.international_formal_name
                    customerAddress = customerAddress + " " + customerCountry
        else:    
            customerName = ""
            customerAddress = ""
            
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        customerAddress = customerAddress.replace("\r\n", "\n")
        customerAddress = customerAddress.replace("\n", " ")
        newCustomerAddress = ""
        for i in range(0, len(customerAddress), 90):
            chunk = customerAddress[i:i+90]
            if len(chunk) < 90:
                newCustomerAddress += chunk
            else:
                space_index = chunk.rfind(' ')
                if space_index != -1:
                    newCustomerAddress += chunk[:space_index] + '\n'
                    if space_index + 1 < len(chunk):
                        newCustomerAddress += chunk[space_index+1:]
                else:
                    newCustomerAddress += chunk
        #alt satır komutu
        lines = newCustomerAddress.replace("\r\n", "\n")
        lines = lines.split('\n')
        line_height = 10  # İsteğe bağlı, satır yüksekliği
        #current_y = h-130

        for line in lines:
            p.drawString(35, current_y, line)
            current_y = current_y - line_height
        #####address with multiple lines-end#####
        
        #####person with multiple lines#####
        if offer.person:
            if offer.person.name:
                person = offer.person.name
                #alt satır komutu
                lines = person.replace("\r\n", "\n")
                lines = lines.split('\n')
                line_height = 8  # İsteğe bağlı, satır yüksekliği
                current_y = current_y

                for line in lines:
                    p.drawString(35, current_y, line)
                    current_y = current_y - line_height
        #####person with multiple lines-end#####
        
        #####title with multiple lines#####
        if offer.person:
            if offer.person.title:
                title = offer.person.title
                #alt satır komutu
                lines = title.replace("\r\n", "\n")
                lines = lines.split('\n')
                line_height = 8  # İsteğe bağlı, satır yüksekliği
                current_y = current_y

                for line in lines:
                    p.drawString(35, current_y, line)
                    current_y = current_y - line_height
        #####title with multiple lines-end#####
        
        #####email with multiple lines#####
        if offer.person:
            if offer.person.email:
                email = offer.person.email
                #alt satır komutu
                lines = email.replace("\r\n", "\n")
                lines = lines.split('\n')
                line_height = 8  # İsteğe bağlı, satır yüksekliği
                current_y = current_y

                for line in lines:
                    p.drawString(35, current_y, line)
                    current_y = current_y - line_height
        #####email with multiple lines-end#####
        
        #####sağ üst tablo#####
        data=[["OUR REF"],
            ["YOUR REF"],
            ["VALIDITY"],
            ["MAKER"],
            ["TYPE"],
            ["SERIAL"],
            ["CYL"]
            ]
        table = Table(data, colWidths=(w/2-35)/3, rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableLeftStyle"))
        
        table.wrapOn(p, w/2+5, h-210)
        table.drawOn(p, w/2+5, h-210)
            
        if offer.equipment:
            maker = offer.equipment.maker.name
            if offer.equipment.makerType:
                makerType = offer.equipment.makerType.type
            else:
                makerType = ""
            serial = offer.equipment.serialNo
            cyl = offer.equipment.cyl
        else:
            maker = ""
            makerType = ""
            serial = ""
            cyl = ""
        
        
        data=[[offer.offerNo],
            [offer.customerRef],
            [offer.period],
            [maker],
            [makerType],
            [serial],
            [cyl]
            ]
        table = Table(data, colWidths=((w/2-35)/3)*2, rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableRightStyle"))
        
        table.wrapOn(p, (w/2+5)+(((w/2-35)/3)), h-210)
        table.drawOn(p, (w/2+5)+(((w/2-35)/3)), h-210)
        #####sağ üst tablo-end#####
        
        #####sol üst tablo sol#####
        data=[["VESSEL / PLANT"],
            ["LOA"],
            ["BEAM"]
            ]
        table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableLeftStyle"))
        
        table.wrapOn(p, 30, h-210)
        table.drawOn(p, 30, h-210)
        
        if offer.vessel:
            vessel = offer.vessel.name
            loa = offer.vessel.loa
            beam = offer.vessel.beam
            imo = offer.vessel.imo
            draught = offer.vessel.draught
            building = offer.vessel.building
        else:
            vessel = ""
            loa = ""
            beam = ""
            imo = ""
            draught = ""
            building = ""
        
        
        data=[[vessel],
            [loa],
            [beam]
            ]
        table = Table(data, colWidths=((w/2-35)/4), rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableRightStyle"))
        
        table.wrapOn(p, 30+(((w/2-35)/4)), h-210)
        table.drawOn(p, 30+(((w/2-35)/4)), h-210)
        #####sol üst tablo sol-end#####
        
        #####sol üst tablo sağ#####
        data=[["IMO"],
            ["DRAUGHT"],
            ["B.YEAR"]
            ]
        table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableLeftStyle"))
        
        table.wrapOn(p, 30+(((w/2-35)/4)*2), h-210)
        table.drawOn(p, 30+(((w/2-35)/4)*2), h-210)
        
        if offer.vessel:
            vessel = offer.vessel.name
            loa = offer.vessel.loa
            beam = offer.vessel.beam
            imo = offer.vessel.imo
            draught = offer.vessel.draught
            building = offer.vessel.building
        else:
            vessel = ""
            loa = ""
            beam = ""
            imo = ""
            draught = ""
            building = ""
        
        
        data=[[imo],
            [draught],
            [building]
            ]
        table = Table(data, colWidths=((w/2-35)/4), rowHeights=tableRowHeight)
        table.setStyle(tableStyle("tableRightStyle"))
        
        table.wrapOn(p, 30+(((w/2-35)/4)*3), h-210)
        table.drawOn(p, 30+(((w/2-35)/4)*3), h-210)
        #####sol üst tablo sağ-end#####
        
        #####parça sayısına göre sayfa dilimleme#####
        #standart ayar
        slice = 26
        pageNum = 1
        pageCount = len(items) // slice
        #standart ayar
        if len(items) % slice != 0:
            pageCount = pageCount + 1
        #standart ayar
        serviceCardsTotal = 0
        serviceCardsSequency = 0
        serviceCardsExtraTotal = 0
        serviceCardsExtraSequency = 0
        expenseTotal = 0
        expenseSequency = 0
        partTotal = 0
        partSequency = 0
        
        for i in range(0, len(items), slice):
            tableTotalRowHeight = 0
            tableSpace = 0
            #standart ayar
            partsList = items[i:i+slice]
            #standart ayar
            pageTemplate(p, w, h, ystart,sourceCompany,sourceCompanyFormalName,sourceCompanyAddress,sourceCompanyPhone,sourceCompanyFax)
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
            p.drawString(450, h-50, "DATE")
            p.setFont('Inter', 7)
            p.drawString(480, h-50, ":" + str(offer.offerDate.strftime("%d.%m.%Y")))
            #####sağ üst yazılar-end#####
            
            if i >= slice:
                th = h+100
            else:
                th = h
            
            #####parts tablo#####
            
            ##########service card talo##########
            data=[["Actions In Offer"],
                ["Line", "Item", "Description", "Qty", "Unit"]
                ]
            rowLengths = []
            serviceCardList = []
            for j in range(len(partsList)):
                if partsList[j]["type"] == "service_card":
                    serviceCardList.append(partsList[j])
                    #partsList[j]["description"] = partsList[j]["description"].replace("\r\n", " ")
                    #####bdescription with multiple lines#####
                    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
                    newDescription = "" 
                    for k in range(0, len(partsList[j]["description"]), 80):
                        chunk = partsList[j]["description"][k:k+80]
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newDescription += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newDescription += chunk[space_index+1:]
                        else:
                            newDescription += chunk
                    #alt satır komutu
                    #newDescription = newDescription.replace("\r\n", " ")
                    lines = newDescription.replace("\r\n", "\n")
                    lines = lines.split('\n')
                    #####bdescription with multiple lines-end#####
                    
                    # Para miktarını belirtilen formatta gösterme
                    unitPrice3Fixed = "{:,.2f}".format(round(partsList[j]["unitPrice"],2))
                    totalPrice3Fixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                    # Nokta ile virgülü değiştirme
                    unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    
                    rowLengths.append(partsList[j])
                    
                    serviceCardsSequency = serviceCardsSequency + 1
                    data.append([serviceCardsSequency, partsList[j]["name"], partsList[j]["description"], partsList[j]["quantity"], partsList[j]["unit"]])
                    serviceCardsTotal = serviceCardsTotal + partsList[j]["totalPrice"]
            
            # Para miktarını belirtilen formatta gösterme
            serviceCardsTotalFixed = "{:,.2f}".format(round(serviceCardsTotal,2))
            # Nokta ile virgülü değiştirme
            serviceCardsTotalFixed = serviceCardsTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            #data.append(["", "", "", "", "", "", str(serviceCardsTotalFixed) + " " + str(offer.currency.code)])
            table1 = Table(data, colWidths=[((w-60)/100)*5 , ((w-60)/100)*11, ((w-60)/100)*76 , ((w-60)/100)*4 , ((w-60)/100)*4])
            table1.setStyle(tableStyle("partsTableStyleLeftWOP"))

            
            table1.wrapOn(p, 30, -99999999)
            table1.drawOn(p, 30, -99999999)
            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
            table1TotalRowHeight = sum(table1._rowHeights)
            if len(serviceCardList) > 0:
                tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                table1.wrapOn(p, 30, th-215-tableTotalRowHeight)
                table1.drawOn(p, 30, th-215-tableTotalRowHeight)
                tableSpace = tableSpace + 10
            ##########service card talo-end##########
            
            ##########service card extra talo##########
            data=[["Actions In Extra"],
                ["Line", "Item", "Description", "Qty", "Unit"]
                ]
            rowLengths = []
            serviceCardExtraList = []
            for j in range(len(partsList)):
                if partsList[j]["type"] == "service_card_extra":
                    serviceCardExtraList.append(partsList[j])
                    #partsList[j]["description"] = partsList[j]["description"].replace("\r\n", " ")
                    #####bdescription with multiple lines#####
                    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
                    newDescription = "" 
                    for k in range(0, len(partsList[j]["description"]), 80):
                        chunk = partsList[j]["description"][k:k+80]
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newDescription += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newDescription += chunk[space_index+1:]
                        else:
                            newDescription += chunk
                            print(newDescription)
                    #alt satır komutu
                    #newDescription = newDescription.replace("\r\n", " ")
                    lines = newDescription.replace("\r\n", "\n")
                    lines = lines.split('\n')
                    #####bdescription with multiple lines-end#####
                    
                    # Para miktarını belirtilen formatta gösterme
                    unitPrice3Fixed = "{:,.2f}".format(round(partsList[j]["unitPrice"],2))
                    totalPrice3Fixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                    # Nokta ile virgülü değiştirme
                    unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    
                    rowLengths.append(len(lines))
                    serviceCardsExtraSequency = serviceCardsExtraSequency + 1
                    data.append([serviceCardsExtraSequency, partsList[j]["name"], partsList[j]["description"], partsList[j]["quantity"], partsList[j]["unit"]])
                    serviceCardsExtraTotal = serviceCardsExtraTotal + partsList[j]["totalPrice"]
            
            # Para miktarını belirtilen formatta gösterme
            serviceCardsExtraTotalFixed = "{:,.2f}".format(round(serviceCardsExtraTotal,2))
            # Nokta ile virgülü değiştirme
            serviceCardsExtraTotalFixed = serviceCardsExtraTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            table2 = Table(data, colWidths=[((w-60)/100)*5 , ((w-60)/100)*11, ((w-60)/100)*76 , ((w-60)/100)*4 , ((w-60)/100)*4])
            table2.setStyle(tableStyle("partsTableStyleLeftWOP"))

            
            table2.wrapOn(p, 30, -99999999)
            table2.drawOn(p, 30, -99999999)
            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
            table2TotalRowHeight = sum(table2._rowHeights)
            if len(serviceCardExtraList) > 0:
                tableTotalRowHeight = tableTotalRowHeight + sum(table2._rowHeights)
                table2.wrapOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                table2.drawOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                tableSpace = tableSpace + 10
                print("space: " + str(tableSpace))
            ##########service card extra talo-end##########
            
            ##########expense talo##########
            data=[["Expenses"],
                ["Line", "Item", "Description", "Qty", "Unit"]
                ]
            rowLengths = []
            expenseList = []
            for j in range(len(partsList)):
                if partsList[j]["type"] == "expense":
                    expenseList.append(partsList[j])
                    #partsList[j]["description"] = partsList[j]["description"].replace("\r\n", " ")
                    #####bdescription with multiple lines#####
                    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
                    newDescription = "" 
                    for k in range(0, len(partsList[j]["description"]), 80):
                        chunk = partsList[j]["description"][k:k+80]
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newDescription += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newDescription += chunk[space_index+1:]
                        else:
                            newDescription += chunk
                            print(newDescription)
                    #alt satır komutu
                    #newDescription = newDescription.replace("\r\n", " ")
                    lines = newDescription.replace("\r\n", "\n")
                    lines = lines.split('\n')
                    #####bdescription with multiple lines-end#####
                    
                    # Para miktarını belirtilen formatta gösterme
                    unitPrice3Fixed = "{:,.2f}".format(round(partsList[j]["unitPrice"],2))
                    totalPrice3Fixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                    # Nokta ile virgülü değiştirme
                    unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    
                    rowLengths.append(len(lines))
                    expenseSequency = expenseSequency + 1
                    data.append([expenseSequency, partsList[j]["name"], partsList[j]["description"], partsList[j]["quantity"], partsList[j]["unit"]])
                    expenseTotal = expenseTotal + partsList[j]["totalPrice"]
            
            # Para miktarını belirtilen formatta gösterme
            expenseTotalFixed = "{:,.2f}".format(round(expenseTotal,2))
            # Nokta ile virgülü değiştirme
            expenseTotalFixed = expenseTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')     
            table3 = Table(data, colWidths=[((w-60)/100)*5 , ((w-60)/100)*11, ((w-60)/100)*76 , ((w-60)/100)*4 , ((w-60)/100)*4])
            table3.setStyle(tableStyle("partsTableStyleLeftWOP"))

            
            table3.wrapOn(p, 30, -99999999)
            table3.drawOn(p, 30, -99999999)
            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
            table3TotalRowHeight = sum(table3._rowHeights)
            if len(expenseList) > 0:
                tableTotalRowHeight = tableTotalRowHeight + sum(table3._rowHeights)
                table3.wrapOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                table3.drawOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                print("space: " + str(tableSpace))
                tableSpace = tableSpace + 10
            ##########expensetalo-end##########
            
            ##########part talo##########
            data=[["Materials"],
                ["Line", "Item", "Description", "Qty", "Unit"]
                ]
            rowLengths = []
            partList = []
            for j in range(len(partsList)):
                if partsList[j]["type"] == "part":
                    partList.append(partsList[j])
                    #partsList[j]["description"] = partsList[j]["description"].replace("\r\n", " ")
                    #####bdescription with multiple lines#####
                    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
                    newDescription = "" 
                    for k in range(0, len(partsList[j]["description"]), 80):
                        chunk = partsList[j]["description"][k:k+80]
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newDescription += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newDescription += chunk[space_index+1:]
                        else:
                            newDescription += chunk
                            print(newDescription)
                    #alt satır komutu
                    #newDescription = newDescription.replace("\r\n", " ")
                    lines = newDescription.replace("\r\n", "\n")
                    lines = lines.split('\n')
                    #####bdescription with multiple lines-end#####
                    
                    if partsList[j]["remark"]:
                        partRemark = " - " + str(partsList[j]["remark"])
                    else:
                        partRemark = ""
                    
                    # Para miktarını belirtilen formatta gösterme
                    unitPrice3Fixed = "{:,.2f}".format(round(partsList[j]["unitPrice"],2))
                    totalPrice3Fixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                    # Nokta ile virgülü değiştirme
                    unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                    
                    rowLengths.append(len(lines))
                    partSequency = partSequency + 1
                    data.append([partSequency, partsList[j]["name"], str(partsList[j]["description"]) + str(partRemark), partsList[j]["quantity"], partsList[j]["unit"]])
                    partTotal = partTotal + partsList[j]["totalPrice"]
            
            # Para miktarını belirtilen formatta gösterme
            partTotalFixed = "{:,.2f}".format(round(partTotal,2))
            # Nokta ile virgülü değiştirme
            partTotalFixed = partTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')     
            table = Table(data, colWidths=[((w-60)/100)*5 , ((w-60)/100)*11, ((w-60)/100)*76 , ((w-60)/100)*4 , ((w-60)/100)*4])
            table.setStyle(tableStyle("partsTableStyleLeftWOP"))

            
            table.wrapOn(p, 30, -99999999)
            table.drawOn(p, 30, -99999999)
            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
            #tableTotalRowHeight = sum(table1._rowHeights)+sum(table2._rowHeights)+sum(table3._rowHeights)+sum(table._rowHeights)
            if len(partList) > 0:
                tableTotalRowHeight = tableTotalRowHeight + sum(table._rowHeights)
                table.wrapOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                table.drawOn(p, 30, th-215-tableTotalRowHeight-tableSpace)
                tableSpace = tableSpace + 10
                
            ##########part tablo-end##########

            p.setFont('Inter', 7)
            #####önemli yazı-end#####
            
            #####sayfa numarası#####
            if len(items) > slice:
                p.setFont('Inter', 7)
                p.drawCentredString(w/2, 10, str(pageNum) + "/" + str(pageCount))
                pageNum = pageNum + 1
            #####sayfa numarası-end#####
            
            p.showPage()
        
        p.save()
    except Exception as e:
        logger.exception(e)
  