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

def offerPdf(offer, sourceCompany):
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
        
    #quotation içerisindeki part listesi
    #parts = orderConfirmation.quotation.quotationpart_set.select_related("inquiryPart")
    serviceCards = OfferServiceCard.objects.filter(offer = offer).order_by("id")
    expenses = OfferExpense.objects.filter(offer = offer).order_by("id")
    parts = OfferPart.objects.filter(offer = offer).order_by("id")
    
    items = []
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
                    "note" : serviceCard.note
                    })
    for expense in expenses:
        items.append({"id" : expense.id,
                    "name":expense.expense.code,
                    "description" : expense.expense.description,
                    "quantity" : expense.quantity,
                    "unit" : expense.expense.unit,
                    "unitPrice" : expense.unitPrice,
                    "totalPrice" : expense.totalPrice,
                    "currency" : offer.currency.code,
                    "note" : ""
                    })
    for part in parts:
        items.append({"id" : part.id,
                    "name":part.part.partNo,
                    "description" : part.part.description,
                    "quantity" : part.quantity,
                    "unit" : part.part.unit,
                    "unitPrice" : part.unitPrice,
                    "totalPrice" : part.totalPrice,
                    "currency" : offer.currency.code,
                    "note" : ""
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
    
    #standart ayar
    buffer = io.BytesIO()
    
    #dosyanın kaydedileceği konum
    folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "service", "offer", "documents")
    
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
    #partsTableRowHeight = (max(descriptionLengths)/70)*20
    
    #tablo stilleri
    tableLeftStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                               ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                               ('TEXTCOLOR',(0,0), (-1,-1), colors.white),
                               ('BACKGROUND',(0,0), (-1,-1), "#9d2235")
                               ])
    tableRightStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                               ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                               ])
    
    #?
    p.setLineWidth(0.5)
    
    #logo
    #esmsImg = Image.open(os.path.join(os.getcwd(), "static", "images", "esms-logo2.jpg"))
    esmsImg = Image.open(os.path.join(os.getcwd(),"media","source","companies",str(sourceCompany.id),str(sourceCompany.documentLogo.name.split('/')[-1])))
    
    #başlık
    p.setFont('Inter', 18)
    p.setFillColor(HexColor("#9d2235"))
    p.drawCentredString(w/2, h-100, "QUOTATION")
    
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
        person = offer.person.name
    else: 
        person = ""
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
        else:
            title = ""
    else: 
        title = ""
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
        else:
            email = ""
    else: 
        email = ""
    #alt satır komutu
    lines = email.replace("\r\n", "\n")
    lines = lines.split('\n')
    line_height = 8  # İsteğe bağlı, satır yüksekliği
    current_y = current_y

    for line in lines:
        p.drawString(35, current_y, line)
        current_y = current_y - line_height
    #####email with multiple lines-end#####
    
    
    
    #####sol üst tablo#####
    # p.setFont('Inter', 7)
    # data=[("")]
    # table = Table(data, colWidths=w/2-35, rowHeights=tableRowHeight*6)
    # table.setStyle(TableStyle([
    #                             ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    #                         ]))
    
    # table.wrapOn(p, 30, h-200)
    # table.drawOn(p, 30, h-200)
    #####sol üst tablo-end#####
    
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
    table.setStyle(tableLeftStyle)
    
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
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, (w/2+5)+(((w/2-35)/3)), h-210)
    table.drawOn(p, (w/2+5)+(((w/2-35)/3)), h-210)
    #####sağ üst tablo-end#####
    
    #####sol üst tablo sol#####
    data=[["VESSEL / PLANT"],
        ["LOA"],
        ["BEAM"]
        ]
    table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
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
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, 30+(((w/2-35)/4)), h-210)
    table.drawOn(p, 30+(((w/2-35)/4)), h-210)
    #####sol üst tablo sol-end#####
    
    #####sol üst tablo sağ#####
    data=[["IMO"],
        ["DRAUGHT"],
        ["B.YEAR"]
        ]
    table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
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
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, 30+(((w/2-35)/4)*3), h-210)
    table.drawOn(p, 30+(((w/2-35)/4)*3), h-210)
    #####sol üst tablo sağ-end#####
    
    #####parça sayısına göre sayfa dilimleme#####
    #standart ayar
    slice = 28
    pageNum = 1
    pageCount = len(items) // slice
    #standart ayar
    if len(items) % slice != 0:
        pageCount = pageCount + 1
    #standart ayar
    for index, i in enumerate(range(0, len(items), slice)):
        #standart ayar
        partsList = items[i:i+slice]
        #standart ayar
        p.drawInlineImage(esmsImg, 30, ystart-10, width=(esmsImg.size[0]/esmsImg.size[1])*40,height=40)
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
        
        partsTableStyleLeft = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 6),
                                ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                ('ALIGN', (5, 0), (-1, -1), "RIGHT"),
                                ('TEXTCOLOR',(0,0), (-1,0), colors.white),
                                ('BACKGROUND',(0,0), (-1,0), "#003865"),
                                ('VALIGN', (0, 0), (-1, -1), "TOP")
                                ])
        
        partsTableStyleRight = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 7),
                                ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 7),
                                ('ALIGN', (0, 0), (-1, -1), "RIGHT"),
                                ('TEXTCOLOR',(0,0), (-1,0), colors.white),
                                ('BACKGROUND',(0,0), (-1,0), "#003865")
                                ])
        
        partsTableStyleCenter = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 7),
                                ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 7),
                                ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                                ('TEXTCOLOR',(0,0), (-1,0), colors.white),
                                ('BACKGROUND',(0,0), (-1,0), "#003865")
                                ])
        
        totalLeftTableStyleLeft = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                ('TEXTCOLOR',(0,0), (-1,-1), colors.white),
                                ('BACKGROUND',(0,0), (-1,-1), "#003865")
                                ])
        
        totalRightTableStyleRight = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                ('ALIGN', (0, 0), (-1, -1), "RIGHT")
                                ])
        
        data=[["Line", "Item", "Description", "Qty", "Unit", "Unit Price", "Total Price"]]
        rowLengths = []
        for j in range(len(partsList)):
            #partsList[j]["description"] = partsList[j]["description"].replace("\r\n", " ")
            #####description with multiple lines#####
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
            #####description with multiple lines-end#####
            
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
            
            
            data.append([j+i+1, partsList[j]["name"], partsList[j]["description"] + str(partRemark), partsList[j]["quantity"], partsList[j]["unit"], str(unitPrice3Fixed) + " " + str(partsList[j]["currency"]), str(totalPrice3Fixed) + " " + str(partsList[j]["currency"])])
        table = Table(data, colWidths=[((w-60)/100)*5 , ((w-60)/100)*11, ((w-60)/100)*52, ((w-60)/100)*4 , ((w-60)/100)*4 , ((w-60)/100)*12 , ((w-60)/100)*12])
        table.setStyle(partsTableStyleLeft)

        
        table.wrapOn(p, 30, -99999999)
        table.drawOn(p, 30, -99999999)
        #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
        tableTotalRowHeight = sum(table._rowHeights)
        table.wrapOn(p, 30, th-215-sum(table._rowHeights))
        table.drawOn(p, 30, th-215-sum(table._rowHeights))
        if pageNum == 999999:
            p.setFont('Inter-Bold', 7)
            p.drawString(30, th-215-sum(table._rowHeights)-10, "PRICES")
            p.drawString(30, th-225-sum(table._rowHeights)-10, "DELIVERY")
            p.drawString(30, th-235-sum(table._rowHeights)-10, "PAYMENT")
        
            p.setFont('Inter', 7)
            p.drawString(80, th-215-sum(table._rowHeights)-10, "NETT. EACH DELIVERY TO BE TREATED AS A SEPERATE CONTRACT")
            if offer.deliveryMethod:
                p.drawString(80, th-225-sum(table._rowHeights)-10, str(offer.deliveryMethod))
            else:
                p.drawString(80, th-225-sum(table._rowHeights)-10, "")
            if offer.paymentType:
                p.drawString(80, th-235-sum(table._rowHeights)-10, str(offer.paymentType))
            else:
                p.drawString(80, th-235-sum(table._rowHeights)-10, "")
                
            p.setFont('Inter-Bold', 7)
            p.drawString(30, th-245-sum(table._rowHeights)-10, "NOTES")
            
            p.setFont('Inter', 7)
            if offer.note:
                note = offer.note
                
            else:
                note = ""
                
            #alt satır komutu
            lines = offer.note.replace("\r\n", "\n")
            lines = lines.split('\n')
            line_height = 10  # İsteğe bağlı, satır yüksekliği
            current_y = th-245-sum(table._rowHeights)-10

            for line in lines:
                p.drawString(80, current_y, line)
                current_y = current_y - line_height
        
        #sütun(tablo) total
        
        if pageNum == 999999999:
            
            dataSubTotal=[["SUB TOTAL"],
                          ["DISCOUNT"],
                          ["NET TOTAL"]
                          ]
            table = Table(dataSubTotal, colWidths=[((w-60)/100)*12, ((w-60)/100)*12], rowHeights=13)
            table.setStyle(totalLeftTableStyleLeft)
            
            table.wrapOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4), th-215-tableTotalRowHeight-39)
            table.drawOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4), th-215-tableTotalRowHeight-39)
            tableTotalLeftLength = table._colWidths[0]
            
            # Para miktarını belirtilen formatta gösterme
            totalTotalPrice3Fixed = "{:,.2f}".format(round(partsTotalsDict["totalTotalPrice3"],2))
            totalDiscountFixed = "{:,.2f}".format(round(partsTotalsDict["totalDiscount"],2))
            totalFinalFixed = "{:,.2f}".format(round(partsTotalsDict["totalFinal"],2))
            # Nokta ile virgülü değiştirme
            totalTotalPrice3Fixed = totalTotalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalDiscountFixed = totalDiscountFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalFinalFixed = totalFinalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            dataSubTotal=[[str(totalTotalPrice3Fixed) + " " + str(offer.currency.code)],
                          [str(totalDiscountFixed) + " " + str(offer.currency.code)],
                          [str(totalFinalFixed) + " " + str(offer.currency.code)]
                          ]
            
            table = Table(dataSubTotal, colWidths=[((w-60)/100)*12, ((w-60)/100)*12], rowHeights=13)
            table.setStyle(totalRightTableStyleRight)
            
            table.wrapOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4)+(((w-60)/100)*12), th-215-tableTotalRowHeight-39)
            table.drawOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4)+(((w-60)/100)*12), th-215-tableTotalRowHeight-39)
            tableTotalLeftLength = table._colWidths[0]
        
        # #sütun(tablo) 1
        # data=[["Line"]]
        # for j in range(len(partsList)):
        #     data.append([j+i+1])
        # table = Table(data, colWidths=((w-60)/100)*5)
        # table.setStyle(partsTableStyleLeft)
    
        # table.wrapOn(p, 30, th-235-(len(data)*partsTableRowHeight))
        # table.drawOn(p, 30, th-235-(len(data)*partsTableRowHeight))
        # table1Length = table._colWidths[0]
        
        # #sütun(tablo) 2
        # data=[["Item"]]
        # for key, part in enumerate(partsList):
        #     data.append([part["name"]])
        # table = Table(data, colWidths=((w-60)/100)*13)
        # table.setStyle(partsTableStyleLeft)
        
        # table.wrapOn(p, 30+table1Length, th-235-(len(data)*partsTableRowHeight))
        # table.drawOn(p, 30+table1Length, th-235-(len(data)*partsTableRowHeight))
        # table2Length = table._colWidths[0]
        
        # #sütun(tablo) 3
        # data=[["Description"]]
        # for part in partsList:
        #     #####bdescription with multiple lines#####
        #     #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        #     newDescription = ""
        #     for i in range(0, len(part["description"]), 50):
        #         chunk = part["description"][i:i+50]
        #         space_index = chunk.rfind(' ')
        #         if space_index != -1:
        #             newDescription += chunk[:space_index] + '\n'
        #             if space_index + 1 < len(chunk):
        #                 newDescription += chunk[space_index+1:]
        #         else:
        #             newDescription += chunk
        #     #alt satır komutu
        #     lines = newDescription.replace("\r\n", "\n")
        #     lines = lines.split('\n')
        #     #####bdescription with multiple lines-end#####
        #     data.append([newDescription])
        # table = Table(data, colWidths=((w-60)/100)*42)
        # table.setStyle(partsTableStyleLeft)
        
        # table.wrapOn(p, 30+table1Length+table2Length, th-235-(len(data)*partsTableRowHeight))
        # table.drawOn(p, 30+table1Length+table2Length, th-235-(len(data)*partsTableRowHeight))
        # table3Length = table._colWidths[0]
        
        # #sütun(tablo) 4
        # data=[["Qty"]]
        # for part in partsList:
        #     data.append([part["quantity"]])
        # table = Table(data, colWidths=((w-60)/100)*5)
        # partsTableStyleRight
        # table.setStyle(partsTableStyleRight)
        
        # table.wrapOn(p, 30+table1Length+table2Length+table3Length, th-235-(len(data)*partsTableRowHeight))
        # table.drawOn(p, 30+table1Length+table2Length+table3Length, th-235-(len(data)*partsTableRowHeight))
        # table4Length = table._colWidths[0]
        
        # #sütun(tablo) 5
        # data=[["Unit"]]
        # for part in partsList:
        #     data.append([part["unit"]])
        # table = Table(data, colWidths=((w-60)/100)*5)
        # partsTableStyleRight
        # table.setStyle(partsTableStyleRight)
        
        # table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length, th-235-(len(data)*partsTableRowHeight))
        # table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length, th-235-(len(data)*partsTableRowHeight))
        # table5Length = table._colWidths[0]
        
        # #sütun(tablo) 6
        # data=[["Unit Price"]]
        # for part in partsList:
        #     if part["id"] == "":
        #         data.append([""])
        #     else:
        #         # Para miktarını belirtilen formatta gösterme
        #         unitPrice3Fixed = "{:,.2f}".format(round(part["unitPrice"],2))
        #         # Nokta ile virgülü değiştirme
        #         unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        #         data.append([str(unitPrice3Fixed) + " " + str(offer.currency.code)])
        # table = Table(data, colWidths=((w-60)/100)*15, hAlign="RIGHT")
        # table.setStyle(partsTableStyleRight)
        
        # table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length, th-235-(len(data)*partsTableRowHeight))
        # table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length, th-235-(len(data)*partsTableRowHeight))
        # table6Length = table._colWidths[0]
        
        # #sütun(tablo) 7
        # data=[["Total Price"]]
        # for part in partsList:
        #     if part["id"] == "":
        #         data.append([""])
        #     else:
        #         # Para miktarını belirtilen formatta gösterme
        #         totalPrice3Fixed = "{:,.2f}".format(round(part["totalPrice"],2))
        #         # Nokta ile virgülü değiştirme
        #         totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        #         data.append([str(totalPrice3Fixed) + " " + str(offer.currency.code)])
        # table = Table(data, colWidths=((w-60)/100)*15)
        # table.setStyle(partsTableStyleRight)
        
        # table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+table6Length, th-235-(len(data)*partsTableRowHeight))
        # table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+table6Length, th-235-(len(data)*partsTableRowHeight))
        # table7Length = table._colWidths[0]
        
        
        
        
        
        
        #sütun(tablo) total
        
        # if pageNum == pageCount:
        #     subTotalPrice = 0
        #     totalPrice = 0
            
        #     for part in parts:
        #         subTotalPrice = subTotalPrice + part.totalPrice2
        #         totalPrice = totalPrice + part.totalPrice3
            
        #     try:
        #         discount = round(1-(totalPrice/subTotalPrice),2)
        #     except:
        #         discount = 0
                
        #     discountPrice  = round(subTotalPrice - totalPrice,2)
            
        #     dataSubTotal=[["SUB TOTAL"],
        #                   ["DISCOUNT"],
        #                   ["NET TOTAL"]
        #                   ]
        #     table = Table(dataSubTotal, colWidths=((w-60)/100)*15, rowHeights=13)
        #     table.setStyle(totalLeftTableStyleLeft)
            
        #     table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length, th-235-((len(data)+3)*partsTableRowHeight))
        #     table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length, th-235-((len(data)+3)*partsTableRowHeight))
        #     tableTotalLeftLength = table._colWidths[0]
            
        #     dataSubTotal=[[str(round(partsTotalsDict["totalTotalPrice3"],2)) + " " + str(offer.currency.code)],
        #           [str(round(partsTotalsDict["totalDiscount"],2)) + " " + str(offer.currency.code)],
        #           [str(round(partsTotalsDict["totalFinal"],2)) + " " + str(offer.currency.code)]]
        #     table = Table(dataSubTotal, colWidths=((w-60)/100)*15, rowHeights=13)
        #     table.setStyle(totalRightTableStyleRight)
            
        #     table.wrapOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+tableTotalLeftLength, th-235-((len(data)+3)*partsTableRowHeight))
        #     table.drawOn(p, 30+table1Length+table2Length+table3Length+table4Length+table5Length+tableTotalLeftLength, th-235-((len(data)+3)*partsTableRowHeight))
        #     tableTotalLeftLength = table._colWidths[0]
        
        
        
        #####parts tablo-end#####
        
        
        
        #####önemli yazı#####
        # p.setFont('Inter', 7)
        # data=[("")]
        # table = Table(data, colWidths=w-60, rowHeights=50)
        # table.setStyle(TableStyle([
        #                             ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        #                         ]))
        
        # table.wrapOn(p, 30, 110)
        # table.drawOn(p, 30, 110)
        
        # p.setFont('Inter-Bold', 6)
        # p.setFillColor(HexColor("#922724"))
        # p.drawCentredString(w/2, 145, "According to SOLAS CHAPTER II-1 Part A-1 Regulation 3-5 , we hereby declare that the offered parts don't contain any asbestos material.")
        # p.drawCentredString(w/2, 135, "Asbestos-Free certificates, if available, can be provided based on request.")
        # p.setFillColor(HexColor("#000"))
        # p.drawCentredString(w/2, 125, "This document contains confidental information belonging to ESMS and must not be disclosed to 3rd parties without permission.")
        
        # p.drawCentredString(w/2, 115, "Cancellation of any confirmed order will result in additional fees (amount of the fees will be changed upon supplier desicion and total amount of order)")
        
        p.setFont('Inter', 7)
        #####önemli yazı-end#####
        
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
        
        #####sayfa numarası#####
        if len(parts) > slice:
            p.setFont('Inter', 7)
            p.drawCentredString(w/2, 10, str(pageNum) + "/" + str(pageCount))
            pageNum = pageNum + 1
        #####sayfa numarası-end#####
        
        if index == len(items) // slice:
            #####
            p.setFont('Inter-Bold', 7)
            p.drawString(30, th-215-sum(table._rowHeights)-10, "PRICES")
            p.drawString(30, th-225-sum(table._rowHeights)-10, "DELIVERY")
            p.drawString(30, th-235-sum(table._rowHeights)-10, "PAYMENT")
        
            p.setFont('Inter', 7)
            p.drawString(80, th-215-sum(table._rowHeights)-10, "NETT. EACH DELIVERY TO BE TREATED AS A SEPERATE CONTRACT")
            if offer.deliveryMethod:
                p.drawString(80, th-225-sum(table._rowHeights)-10, str(offer.deliveryMethod))
            else:
                p.drawString(80, th-225-sum(table._rowHeights)-10, "")
            if offer.paymentType:
                p.drawString(80, th-235-sum(table._rowHeights)-10, str(offer.paymentType))
            else:
                p.drawString(80, th-235-sum(table._rowHeights)-10, "")
                
            p.setFont('Inter-Bold', 7)
            p.drawString(30, th-245-sum(table._rowHeights)-10, "NOTES")
            
            p.setFont('Inter', 7)
            if offer.note:
                note = offer.note
                
            else:
                note = ""
                
            #alt satır komutu
            lines = offer.note.replace("\r\n", "\n")
            lines = lines.split('\n')
            line_height = 10  # İsteğe bağlı, satır yüksekliği
            current_y = th-245-sum(table._rowHeights)-10

            for line in lines:
                p.drawString(80, current_y, line)
                current_y = current_y - line_height

            #####
            dataSubTotal=[["SUB TOTAL"],
                    ["DISCOUNT"],
                    ["NET TOTAL"]
                    ]
            table = Table(dataSubTotal, colWidths=[((w-60)/100)*12, ((w-60)/100)*12], rowHeights=13)
            table.setStyle(totalLeftTableStyleLeft)
            
            table.wrapOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4), th-215-tableTotalRowHeight-39)
            table.drawOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4), th-215-tableTotalRowHeight-39)
            tableTotalLeftLength = table._colWidths[0]
            
            # Para miktarını belirtilen formatta gösterme
            totalTotalPrice3Fixed = "{:,.2f}".format(round(partsTotalsDict["totalTotalPrice3"],2))
            totalDiscountFixed = "{:,.2f}".format(round(partsTotalsDict["totalDiscount"],2))
            totalFinalFixed = "{:,.2f}".format(round(partsTotalsDict["totalFinal"],2))
            # Nokta ile virgülü değiştirme
            totalTotalPrice3Fixed = totalTotalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalDiscountFixed = totalDiscountFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            totalFinalFixed = totalFinalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            dataSubTotal=[[str(totalTotalPrice3Fixed) + " " + str(offer.currency.code)],
                            [str(totalDiscountFixed) + " " + str(offer.currency.code)],
                            [str(totalFinalFixed) + " " + str(offer.currency.code)]
                            ]
            
            table = Table(dataSubTotal, colWidths=[((w-60)/100)*12, ((w-60)/100)*12], rowHeights=13)
            table.setStyle(totalRightTableStyleRight)
            
            table.wrapOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4)+(((w-60)/100)*12), th-215-tableTotalRowHeight-39)
            table.drawOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4)+(((w-60)/100)*12), th-215-tableTotalRowHeight-39)
            tableTotalLeftLength = table._colWidths[0]
        
        p.showPage()

    

    p.save()
