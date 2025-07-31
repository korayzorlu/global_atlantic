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

from ..models import Acceptance,AcceptanceServiceCard,AcceptanceEquipment
from card.models import EnginePart

#####SETUP#####
def pageSettings(p, w, h, title):
    #başlık
    p.setFont('Inter', 18)
    p.setFillColor(HexColor("#9d2235"))
    p.drawCentredString(w/2, h-100, title)   

def pageTemplate(p, w, h, ystart,sourceCompany):
    #logo
    #esmsImg = Image.open(os.path.join(os.getcwd(), "static", "images", "esms-mechanics-logo.jpg"))
    esmsImg = Image.open(os.path.join(os.getcwd(),"media","source","companies",str(sourceCompany.id),str(sourceCompany.documentLogo.name.split('/')[-1])))

    #p.drawInlineImage(esmsImg, (w/2)-(264/2), ystart-10, width=264,height=40)
    p.drawInlineImage(esmsImg, 30, ystart-10, width=(esmsImg.size[0]/esmsImg.size[1])*40,height=40)
    
    # ######sayfa altı########
    # p.setStrokeColor(HexColor("#808080"))
    # p.line(30, 100, w-30, 100)
    # p.setFont('Inter-Bold', 7)
    # p.drawString(30, 90, sourceCompanyFormalName)
    # p.drawString(30, 70, "Office")
    # p.setFont('Inter', 7)
    # p.drawString(60, 70, sourceCompanyAddress)
    # #p.drawString(60, 70, "No:126 57/C P.K. 34947 Tuzla İstanbul TR")
    # p.setFont('Inter-Bold', 7)
    # p.drawString(30, 60, "Tel")
    # p.setFont('Inter', 7)
    # p.drawString(60, 60, sourceCompanyPhone)
    # p.setFont('Inter-Bold', 7)
    # p.drawString(30, 50, "Fax")
    # p.setFont('Inter', 7)
    # p.drawString(60, 50, sourceCompanyFax)
    
    # lrImg = Image.open(os.path.join(os.getcwd(), "static", "images", "sale", "lr-logo4.jpg"))
    
    # p.drawInlineImage(lrImg, 415, 46, width=150,height=50)
    
    # p.line(30, 40, w-30, 40)
    # p.setFont('Inter-Bold', 7)
    # #p.drawString(30, 30, str(offer.user.first_name) + " " + str(offer.user.last_name) + " / " + str(offer.user.profile.positionType))
    # p.setFont('Inter-Bold', 7)
    # p.drawString(310, 30, "Document Date: " + str(datetime.today().date().strftime("%d.%m.%Y")))
    # ######sayfa altı-end########

def pageFooter(p,w,h,ystart,sourceCompanyFormalName,sourceCompanyAddress,sourceCompanyPhone,sourceCompanyFax):
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

#####SETUP-END#####

#####PDF#####

def acceptancePdf(acceptance, sourceCompany):
    #quotation içerisindeki part listesi
    #parts = orderConfirmation.quotation.quotationpart_set.select_related("inquiryPart")

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
        
    serviceCards = AcceptanceServiceCard.objects.filter(acceptance = acceptance).order_by("id")
    equipments = AcceptanceEquipment.objects.select_related("equipment","equipment__maker","equipment__makerType").filter(acceptance = acceptance).order_by("id")
    
    items = []
    for equipment in equipments:
        items.append({"id" : equipment.id,
                    "maker":equipment.equipment.maker.name,
                    "type" : equipment.equipment.makerType.type,
                    "category" : equipment.equipment.category,
                    "serial" : equipment.equipment.serialNo,
                    "cyl" : equipment.equipment.cyl,
                    "description" : equipment.equipment.description,
                    "version" : equipment.equipment.version,
                    "remark" : "",
                    "note" : ""
                    })
    
    #standart ayar
    buffer = io.BytesIO()
    
    #dosyanın kaydedileceği konum
    folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "service", "acceptance", "documents")
    
    #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    
    #font ayarları
    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
    pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
    
    #standart ayar
    p = canvas.Canvas(folderPath + "/" + acceptance.acceptanceNo + ".pdf", pagesize = A4)
    
    #standart ayar
    w, h = A4
    
    ystart = 780
    
    pageTemplate(p, w, h, ystart,sourceCompany)
    
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
    esmsImg = Image.open(os.path.join(os.getcwd(), "static", "images", "esms-logo2.jpg"))
    
    #başlık
    p.setFont('Inter', 18)
    p.setFillColor(HexColor("#9d2235"))
    p.drawCentredString(w/2, h-100, "WORKSHOP ACCEPTANCE")
    
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
    p.drawString(35, h-130, "COMPANY:")
    p.setFont('Inter', 6)
    #customer
    if acceptance.customer:
        customerName = acceptance.customer.name
    else:    
        customerName = ""
    
    #####customer name with multiple lines#####
    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
    newCustomerName = ""
    for i in range(0, len(customerName), 50):
        chunk = customerName[i:i+50]
        if len(chunk) < 50:
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
    current_y = h-130

    for line in lines:
        p.drawString(75, current_y, line)
        current_y = current_y - line_height
    #####customer name with multiple lines-end#####
    
    #####address with multiple lines#####
    #alt satır komutu
        
    if acceptance.customer:
        customerName = acceptance.customer.name
        if acceptance.customer.address:
            customerAddress = acceptance.customer.address
            if acceptance.customer.city:
                customerCity = acceptance.customer.city.name
                customerAddress = customerAddress + " " + customerCity + " /"
            if acceptance.customer.country:
                customerCountry = acceptance.customer.country.international_formal_name
                customerAddress = customerAddress + " " + customerCountry
        else:
            customerAddress = ""
            if acceptance.customer.city:
                customerCity = acceptance.customer.city.name
                customerAddress = customerAddress + " " + customerCity + " /"
            if acceptance.customer.country:
                customerCountry = acceptance.customer.country.international_formal_name
                customerAddress = customerAddress + " " + customerCountry
    else:    
        customerName = ""
        customerAddress = ""
        
    lines = customerAddress.replace("\r\n", "\n")
    lines = lines.split('\n')
    line_height = 8  # İsteğe bağlı, satır yüksekliği
    current_y = current_y

    for line in lines:
        p.drawString(35, current_y, line)
        current_y = current_y - line_height
    #####address with multiple lines-end#####
    
    #####person with multiple lines#####
    if acceptance.person:
        person = acceptance.person.name
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
    if acceptance.person:
        title = acceptance.person.title
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
    if acceptance.person:
        if acceptance.person.email:
            email = acceptance.person.email
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
        ["VESSEL"],
        ["IMO"]
        ]
    table = Table(data, colWidths=(w/2-35)/3, rowHeights=tableRowHeight)
    table.setStyle(tableLeftStyle)
    
    table.wrapOn(p, w/2+5, h-170)
    table.drawOn(p, w/2+5, h-170)
        
    if acceptance.equipment:
        maker = acceptance.equipment.maker.name
        if acceptance.equipment.makerType:
            makerType = acceptance.equipment.makerType.type
        else:
            makerType = ""
        serial = acceptance.equipment.serialNo
        cyl = acceptance.equipment.cyl
    else:
        maker = ""
        makerType = ""
        serial = ""
        cyl = ""
    
    if acceptance.vessel:
        vessel = acceptance.vessel.name
        loa = acceptance.vessel.loa
        beam = acceptance.vessel.beam
        imo = acceptance.vessel.imo
        draught = acceptance.vessel.draught
        building = acceptance.vessel.building
    else:
        vessel = ""
        loa = ""
        beam = ""
        imo = ""
        draught = ""
        building = ""
    
    data=[[acceptance.acceptanceNo],
        [acceptance.customerRef],
        [vessel],
        [imo]
        ]
    table = Table(data, colWidths=((w/2-35)/3)*2, rowHeights=tableRowHeight)
    table.setStyle(tableRightStyle)
    
    table.wrapOn(p, (w/2+5)+(((w/2-35)/3)), h-170)
    table.drawOn(p, (w/2+5)+(((w/2-35)/3)), h-170)
    #####sağ üst tablo-end#####
    
    # #####sol üst tablo sol#####
    # data=[["VESSEL / PLANT"],
    #     ["LOA"],
    #     ["BEAM"]
    #     ]
    # table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
    # table.setStyle(tableLeftStyle)
    
    # table.wrapOn(p, 30, h-210)
    # table.drawOn(p, 30, h-210)
    
    # if acceptance.vessel:
    #     vessel = acceptance.vessel.name
    #     loa = acceptance.vessel.loa
    #     beam = acceptance.vessel.beam
    #     imo = acceptance.vessel.imo
    #     draught = acceptance.vessel.draught
    #     building = acceptance.vessel.building
    # else:
    #     vessel = ""
    #     loa = ""
    #     beam = ""
    #     imo = ""
    #     draught = ""
    #     building = ""
    
    
    # data=[[vessel],
    #     [loa],
    #     [beam]
    #     ]
    # table = Table(data, colWidths=((w/2-35)/4), rowHeights=tableRowHeight)
    # table.setStyle(tableRightStyle)
    
    # table.wrapOn(p, 30+(((w/2-35)/4)), h-210)
    # table.drawOn(p, 30+(((w/2-35)/4)), h-210)
    # #####sol üst tablo sol-end#####
    
    # #####sol üst tablo sağ#####
    # data=[["IMO"],
    #     ["DRAUGHT"],
    #     ["B.YEAR"]
    #     ]
    # table = Table(data, colWidths=(w/2-35)/4, rowHeights=tableRowHeight)
    # table.setStyle(tableLeftStyle)
    
    # table.wrapOn(p, 30+(((w/2-35)/4)*2), h-210)
    # table.drawOn(p, 30+(((w/2-35)/4)*2), h-210)
    
    # if acceptance.vessel:
    #     vessel = acceptance.vessel.name
    #     loa = acceptance.vessel.loa
    #     beam = acceptance.vessel.beam
    #     imo = acceptance.vessel.imo
    #     draught = acceptance.vessel.draught
    #     building = acceptance.vessel.building
    # else:
    #     vessel = ""
    #     loa = ""
    #     beam = ""
    #     imo = ""
    #     draught = ""
    #     building = ""
    
    
    # data=[[imo],
    #     [draught],
    #     [building]
    #     ]
    # table = Table(data, colWidths=((w/2-35)/4), rowHeights=tableRowHeight)
    # table.setStyle(tableRightStyle)
    
    # table.wrapOn(p, 30+(((w/2-35)/4)*3), h-210)
    # table.drawOn(p, 30+(((w/2-35)/4)*3), h-210)
    # #####sol üst tablo sağ-end#####
    
    
    firstPageTableMaxHeight = 490
    firstLastPageTableMaxHeight = 445
    tableMaxHeight = 600
    lastPageTableMaxHeight = 540
    firstPage = True
    allItems = []
    partsList = []
    tableHeight = 13.2
    #####parça sayısına göre sayfa dilimleme#####
    for key, i in enumerate(range(len(items))):
        tableHeight = tableHeight + 13.2
        #####description with multiple lines#####
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        description = items[i]["description"].replace("\r\n", "\n")
        description = description.replace("\n", " ")
        newDescription = ""
        for k in range(0, len(description), 50):
            chunk = description[k:k+50]
            if len(chunk) < 50:
                newDescription += chunk
            else:
                space_index = chunk.rfind(" ")
                if space_index != -1:
                    newDescription += chunk[:space_index] + '\n'
                    if space_index + 1 < len(chunk):
                        newDescription += chunk[space_index+1:]
                else:
                    newDescription += chunk
        #alt satır komutu
        newDescription = newDescription.replace("\r\n", "\n")
        if items[i]["remark"]:
            remark = items[i]["remark"]
            newRemark = ""
            for k in range(0, len(remark), 50):
                chunk = remark[k:k+50]
                if len(chunk) < 50:
                    newRemark += chunk
                else:
                    space_index = chunk.rfind(" ")
                    if space_index != -1:
                        newRemark += chunk[:space_index] + '\n'
                        if space_index + 1 < len(chunk):
                            newRemark += chunk[space_index+1:]
                    else:
                        newRemark += chunk
            #alt satır komutu
            newRemark = newRemark.replace("\r\n", "\n")
            if newDescription == "":
                newDescription = newRemark
            else:
                newDescription = newDescription + "\n" + newRemark
        #####description with multiple lines-end#####
        #####note with multiple lines#####
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        if items[i]["note"]:
            newNote = ""
            for k in range(0, len(items[i]["note"]), 11):
                chunk = items[i]["note"][k:k+11]
                if len(chunk) < 11:
                    newNote += chunk
                else:
                    space_index = chunk.rfind(" ")
                    if space_index != -1:
                        newNote += chunk[:space_index] + '\n'
                        if space_index + 1 < len(chunk):
                            newNote += chunk[space_index+1:]
                    else:
                        newNote += chunk
            #alt satır komutu
            newNote = newNote.replace("\r\n", "\n")
        else:
            newNote = ""
        #####note with multiple lines-end#####
        #print("description line count: " + str(newDescription.count('\n')) + " - note line count: " + str(newNote.count('\n')))
        if newDescription.count('\n') > newNote.count('\n'):
            tableHeight = tableHeight + (7.2 * newDescription.count('\n'))
        else:
            tableHeight = tableHeight + (7.2 * newNote.count('\n'))
        
        #item'ları dilimler
        if firstPage:
            partsList.append(items[i])
        
        if not firstPage:
            partsList.append(items[i])
            
            if key < len(items) - 1 and tableHeight > tableMaxHeight: #son item'a ulaşmadan 700'ü geçerse
                partsList.remove(items[i])
                allItems.append({
                    "height" : tableHeight - 13.2,
                    "parts" : partsList
                })
                
                #tabloyu sıfırladık yeni sayfaya geçtik
                partsList = []
                tableHeight = 0
                partsList.append(items[i])

            if key == len(items) - 1 and tableHeight > tableMaxHeight: #son item'a ulaşıp 700'ü geçerse
                allItems.append({
                    "height" : tableHeight,
                    "parts" : partsList
                })
            
            if key == len(items) - 1 and tableHeight < tableMaxHeight: #son item'a ulaşıp 700'ün altında kalırsa
                allItems.append({
                    "height" : tableHeight,
                    "parts" : partsList
                })
            
        if firstPage and key < len(items) - 1 and tableHeight > firstPageTableMaxHeight:
            firstPage = False
            partsList.remove(items[i])
            allItems.append({
                "height" : tableHeight - 13.2,
                "parts" : partsList
            })
            
            #tabloyu sıfırladık yeni sayfaya geçtik
            partsList = []
            tableHeight = 0
            partsList.append(items[i])
            
        if firstPage and key == len(items) - 1:
            firstPage = False
            allItems.append({
                "height" : tableHeight - 13.2,
                "parts" : partsList
            })
        
    #####parça sayısına göre sayfa dilimleme-end#####
    
    pageCount = 0
    th = h
    for key, theItems in enumerate(allItems):
        #####sayfa numarası ve sayfa sonu kontrolü#####
        pageNumber = key + 1
        if len(allItems) > 1 and allItems[-1]["height"] > lastPageTableMaxHeight:
            extraPage = 1
        elif len(allItems) == 1 and allItems[-1]["height"] > firstLastPageTableMaxHeight:
            extraPage = 1
        else:
            extraPage = 0
        pageCount = len(allItems) + extraPage
        
        if key < len(allItems) - 1:
            p.setFont('Inter', 7)
            p.drawString(30, 105, "PAGE     " + str(p.getPageNumber()) + " OF " + str(pageCount) + "     CONTINUED")
            
        if key == len(allItems) - 1 and extraPage == 0:
            p.setFont('Inter', 7)
            p.drawString(30, 105, "PAGE     " + str(p.getPageNumber()) + " OF " + str(pageCount) + "     END")
        
        if key == len(allItems) - 1 and extraPage == 1:
            p.setFont('Inter', 7)
            p.drawString(30, 105, "PAGE     " + str(p.getPageNumber()) + " OF " + str(pageCount) + "     CONTINUED") 
        #####sayfa numarası ve sayfa sonu kontrolü-end#####
        
        #####sayfa üstü logo#####
        p.drawInlineImage(esmsImg, 30, ystart-10, width=(esmsImg.size[0]/esmsImg.size[1])*40,height=40)
        #####sayfa üstü logo-end#####
        
        #####sağ üst yazılar#####
        p.setFont('Inter-Bold', 7)
        p.drawString(450, h-50, "DATE")
        p.setFont('Inter', 7)
        p.drawString(480, h-50, ":" + str(acceptance.acceptanceDate.strftime("%d.%m.%Y")))
        #####sağ üst yazılar-end#####
        
        #####parts tablo styles#####
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
        
        totalLeftTableStyleLeftTotal = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('BOX', (0,0), (-1,-1), 0.25, "#003865"),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                                ('TEXTCOLOR',(0,0), (-1,-1), colors.white),
                                ('BACKGROUND',(0,0), (-1,-1), "#003865")
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
        #####parts tablo styles-end#####
        
        #####parts tablo#####
        data=[["Line", "Maker", "Type", "Category", "Serial", "Cyl"]]
        
        for j in range(len(theItems["parts"])):
            #####description with multiple lines#####
            #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
            description = theItems["parts"][j]["description"].replace("\r\n", "\n")
            description = description.replace("\n", " ")
            newDescription = ""
            for k in range(0, len(description), 50):
                chunk = description[k:k+50]
                if len(chunk) < 50:
                    newDescription += chunk
                else:
                    space_index = chunk.rfind(" ")
                    if space_index != -1:
                        newDescription += chunk[:space_index] + '\n'
                        if space_index + 1 < len(chunk):
                            newDescription += chunk[space_index+1:]
                    else:
                        newDescription += chunk
            #alt satır komutu
            newDescription = newDescription.replace("\r\n", "\n")
            
            if theItems["parts"][j]["remark"]:
                remark = theItems["parts"][j]["remark"]
                newRemark = ""
                for k in range(0, len(remark), 50):
                    chunk = remark[k:k+50]
                    if len(chunk) < 50:
                        newRemark += chunk
                    else:
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newRemark += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newRemark += chunk[space_index+1:]
                        else:
                            newRemark += chunk
                #alt satır komutu
                newRemark = newRemark.replace("\r\n", "\n")
                if newDescription == "":
                    newDescription = newRemark
                else:
                    newDescription = newDescription + "\n" + newRemark
            #####description with multiple lines-end#####
            
            #####note with multiple lines#####
            #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
            if theItems["parts"][j]["note"]:
                newNote = ""
                for k in range(0, len(theItems["parts"][j]["note"]), 11):
                    chunk = theItems["parts"][j]["note"][k:k+11]
                    if len(chunk) < 11:
                        newNote += chunk
                    else:
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newNote += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newNote += chunk[space_index+1:]
                        else:
                            newNote += chunk
                #alt satır komutu
                newNote = newNote.replace("\r\n", "\n")
            else:
                newNote = ""
            #####note with multiple lines-end#####
            
            data.append([j+1, theItems["parts"][j]["maker"], theItems["parts"][j]["type"], theItems["parts"][j]["category"], theItems["parts"][j]["serial"], theItems["parts"][j]["cyl"]])
        
        table = Table(data, colWidths=[((w-60)/100)*4 , ((w-60)/100)*25, ((w-60)/100)*25, ((w-60)/100)*20, ((w-60)/100)*20, ((w-60)/100)*6])
        table.setStyle(partsTableStyleLeft)
        
        table.wrapOn(p, 30, -99999999)
        table.drawOn(p, 30, -99999999)
        tableTotalRowHeight = sum(table._rowHeights)
        table.wrapOn(p, 30, th-175-sum(table._rowHeights))
        table.drawOn(p, 30, th-175-sum(table._rowHeights))
        #print(allItems[-1]["height"])
        #print(sum(table._rowHeights))
        #####parts tablo-end#####
        
        pageFooter(p, w, h, ystart,sourceCompanyFormalName,sourceCompanyAddress,sourceCompanyPhone,sourceCompanyFax)
        
        #####total tablo and notes#####
        if key == len(allItems) - 1 and extraPage == 0:
            
            
            #####alttaki note remark yazıları#####
            p.setFont('Inter-Bold', 7)
            p.drawString(30, th-185-sum(table._rowHeights), "NOTES")
            p.setFont('Inter', 7)
            if acceptance.note:
                note = acceptance.note
                
            else:
                note = ""
            #alt satır komutu
            lines = note.replace("\r\n", "\n")
            lines = lines.split('\n')
            line_height = 10  # İsteğe bağlı, satır yüksekliği
            current_y = th-185-sum(table._rowHeights)
    
            for line in lines:
                p.drawString(80, current_y, line)
                current_y = current_y - line_height
            #####alttaki note remark yazıları-end#####
            
        if key == len(allItems) - 1 and extraPage == 1:
            p.showPage()
            
            if len(allItems) == 1 and allItems[-1]["height"] > firstLastPageTableMaxHeight:
                th = h + 120
            
            p.setFont('Inter', 7)
            p.drawString(30, 105, "PAGE     " + str(p.getPageNumber()) + " OF " + str(pageCount) + "     END")
            
            #####alttaki note remark yazıları##### 
            p.setFont('Inter-Bold', 7)
            p.drawString(30, th-185, "NOTES")
            p.setFont('Inter', 7)
            if acceptance.note:
                note = acceptance.note
                
            else:
                note = ""
            #alt satır komutu
            lines = note.replace("\r\n", "\n")
            lines = lines.split('\n')
            line_height = 10  # İsteğe bağlı, satır yüksekliği
            current_y = th-185
    
            for line in lines:
                p.drawString(80, current_y, line)
                current_y = current_y - line_height
            #####alttaki note remark yazıları-end#####
            
            #####sayfa üstü logo#####
            p.drawInlineImage(esmsImg, 30, ystart-10, width=(esmsImg.size[0]/esmsImg.size[1])*40,height=40)
            #####sayfa üstü logo-end#####
            
            #####sağ üst yazılar#####
            p.setFont('Inter-Bold', 7)
            p.drawString(450, h-50, "DATE")
            p.setFont('Inter', 7)
            p.drawString(480, h-50, ":" + str(acceptance.acceptanceDate.strftime("%d.%m.%Y")))
            #####sağ üst yazılar-end#####
            
            pageFooter(p, w, h, ystart,sourceCompanyFormalName,sourceCompanyAddress,sourceCompanyPhone,sourceCompanyFax)
            
        #####total tablo and notes-end#####
        
        th = h + 120
        
        p.showPage()
     
    
    
    
    
    # #####parça sayısına göre sayfa dilimleme#####
    # #standart ayar
    # slice = 28
    # pageNum = 1
    # pageCount = len(items) // slice
    # #standart ayar
    # if len(items) % slice != 0:
    #     pageCount = pageCount + 1
    # #standart ayar
    # for i in range(0, len(items), slice):
    #     #standart ayar
    #     partsList = items[i:i+slice]
    #     #standart ayar
    #     p.drawInlineImage(esmsImg, 30, ystart-10, width=102,height=40)
    #     p.setFont('Inter-Bold', 7)
    #     #p.drawString(450, h-50, "DATE")
    #     p.setFont('Inter', 7)
    #     #p.drawString(480, h-50, ":" + str(inquiry.inquiryDate.strftime("%d.%m.%Y")))
        
    #     p.setFont('Inter-Bold', 7)
    #     #p.drawString(450, h-70, "REF NO")
    #     p.setFont('Inter', 7)
    #     #p.drawString(480, h-70, ":" + str(inquiry.inquiryNo))
        
    #     #####sağ üst yazılar#####
    #     p.setFont('Inter-Bold', 7)
    #     p.drawString(450, h-50, "DATE")
    #     p.setFont('Inter', 7)
    #     p.drawString(480, h-50, ":" + str(acceptance.acceptanceDate.strftime("%d.%m.%Y")))
    #     #####sağ üst yazılar-end#####
        
    #     if i >= slice:
    #         th = h+100
    #     else:
    #         th = h
        
    #     #####parts tablo#####
        
    #     partsTableStyleLeft = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
    #                             ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
    #                             ('FONT', (0, 0), (-1, -1), 'Inter', 6),
    #                             ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 6),
    #                             ('ALIGN', (0, 0), (-1, -1), "LEFT"),
    #                             ('ALIGN', (5, 0), (-1, -1), "RIGHT"),
    #                             ('TEXTCOLOR',(0,0), (-1,0), colors.white),
    #                             ('BACKGROUND',(0,0), (-1,0), "#003865"),
    #                             ('VALIGN', (0, 0), (-1, -1), "TOP")
    #                             ])
        
    #     partsTableStyleRight = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
    #                             ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
    #                             ('FONT', (0, 0), (-1, -1), 'Inter', 7),
    #                             ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 7),
    #                             ('ALIGN', (0, 0), (-1, -1), "RIGHT"),
    #                             ('TEXTCOLOR',(0,0), (-1,0), colors.white),
    #                             ('BACKGROUND',(0,0), (-1,0), "#003865")
    #                             ])
        
    #     partsTableStyleCenter = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
    #                             ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
    #                             ('FONT', (0, 0), (-1, -1), 'Inter', 7),
    #                             ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 7),
    #                             ('ALIGN', (0, 0), (-1, -1), "CENTER"),
    #                             ('TEXTCOLOR',(0,0), (-1,0), colors.white),
    #                             ('BACKGROUND',(0,0), (-1,0), "#003865")
    #                             ])
        
    #     totalLeftTableStyleLeft = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
    #                             ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
    #                             ('FONT', (0, 0), (-1, -1), 'Inter', 6),
    #                             ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
    #                             ('ALIGN', (0, 0), (-1, -1), "LEFT"),
    #                             ('TEXTCOLOR',(0,0), (-1,-1), colors.white),
    #                             ('BACKGROUND',(0,0), (-1,-1), "#003865")
    #                             ])
        
    #     totalRightTableStyleRight = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
    #                             ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
    #                             ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
    #                             ('ALIGN', (0, 0), (-1, -1), "RIGHT")
    #                             ])
        
    #     data=[["Line", "Item", "Description", "Qty", "Unit", "Unit Price", "Total Price"]]
    #     rowLengths = []
    #     for j in range(len(partsList)):
    #         #partsList[j]["description"] = partsList[j]["description"].replace("\r\n", " ")
    #         #####description with multiple lines#####
    #         #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
    #         newDescription = "" 
    #         for k in range(0, len(partsList[j]["description"]), 80):
    #             chunk = partsList[j]["description"][k:k+80]
    #             space_index = chunk.rfind(" ")
    #             if space_index != -1:
    #                 newDescription += chunk[:space_index] + '\n'
    #                 if space_index + 1 < len(chunk):
    #                     newDescription += chunk[space_index+1:]
    #             else:
    #                 newDescription += chunk
    #                 print(newDescription)
    #         #alt satır komutu
    #         #newDescription = newDescription.replace("\r\n", " ")
    #         lines = newDescription.replace("\r\n", "\n")
    #         lines = lines.split('\n')
    #         #####description with multiple lines-end#####
            
    #         if partsList[j]["remark"]:
    #             partRemark = " - " + str(partsList[j]["remark"])
    #         else:
    #             partRemark = ""
            
    #         # Para miktarını belirtilen formatta gösterme
    #         unitPrice3Fixed = "{:,.2f}".format(round(partsList[j]["unitPrice"],2))
    #         totalPrice3Fixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
    #         # Nokta ile virgülü değiştirme
    #         unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
    #         totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            
    #         data.append([j+i+1, partsList[j]["name"], partsList[j]["description"] + str(partRemark), partsList[j]["quantity"], partsList[j]["unit"], str(unitPrice3Fixed) + " " + str(partsList[j]["currency"]), str(totalPrice3Fixed) + " " + str(partsList[j]["currency"])])
    #     table = Table(data, colWidths=[((w-60)/100)*5 , ((w-60)/100)*11, ((w-60)/100)*52, ((w-60)/100)*4 , ((w-60)/100)*4 , ((w-60)/100)*12 , ((w-60)/100)*12])
    #     table.setStyle(partsTableStyleLeft)

        
    #     table.wrapOn(p, 30, -99999999)
    #     table.drawOn(p, 30, -99999999)
    #     #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
    #     tableTotalRowHeight = sum(table._rowHeights)
    #     table.wrapOn(p, 30, th-215-sum(table._rowHeights))
    #     table.drawOn(p, 30, th-215-sum(table._rowHeights))
    #     if pageNum == pageCount:
    #         p.setFont('Inter-Bold', 7)
    #         p.drawString(30, th-215-sum(table._rowHeights)-10, "PRICES")
    #         p.drawString(30, th-225-sum(table._rowHeights)-10, "DELIVERY")
    #         p.drawString(30, th-235-sum(table._rowHeights)-10, "PAYMENT")
        
    #         p.setFont('Inter', 7)
    #         p.drawString(80, th-215-sum(table._rowHeights)-10, "NETT. EACH DELIVERY TO BE TREATED AS A SEPERATE CONTRACT")
    #         if acceptance.deliveryMethod:
    #             p.drawString(80, th-225-sum(table._rowHeights)-10, str(acceptance.deliveryMethod))
    #         else:
    #             p.drawString(80, th-225-sum(table._rowHeights)-10, "")
    #         if acceptance.paymentType:
    #             p.drawString(80, th-235-sum(table._rowHeights)-10, str(acceptance.paymentType))
    #         else:
    #             p.drawString(80, th-235-sum(table._rowHeights)-10, "")
                
    #         p.setFont('Inter-Bold', 7)
    #         p.drawString(30, th-245-sum(table._rowHeights)-10, "NOTES")
            
    #         p.setFont('Inter', 7)
    #         if acceptance.note:
    #             note = acceptance.note
                
    #         else:
    #             note = ""
                
    #         #alt satır komutu
    #         lines = acceptance.note.replace("\r\n", "\n")
    #         lines = lines.split('\n')
    #         line_height = 10  # İsteğe bağlı, satır yüksekliği
    #         current_y = th-245-sum(table._rowHeights)-10

    #         for line in lines:
    #             p.drawString(80, current_y, line)
    #             current_y = current_y - line_height
        
    #     #sütun(tablo) total
        
    #     if pageNum == pageCount:
            
    #         dataSubTotal=[["SUB TOTAL"],
    #                       ["DISCOUNT"],
    #                       ["NET TOTAL"]
    #                       ]
    #         table = Table(dataSubTotal, colWidths=[((w-60)/100)*12, ((w-60)/100)*12], rowHeights=13)
    #         table.setStyle(totalLeftTableStyleLeft)
            
    #         table.wrapOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4), th-215-tableTotalRowHeight-39)
    #         table.drawOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4), th-215-tableTotalRowHeight-39)
    #         tableTotalLeftLength = table._colWidths[0]
            
    #         # Para miktarını belirtilen formatta gösterme
    #         totalTotalPrice3Fixed = "{:,.2f}".format(round(partsTotalsDict["totalTotalPrice3"],2))
    #         totalDiscountFixed = "{:,.2f}".format(round(partsTotalsDict["totalDiscount"],2))
    #         totalFinalFixed = "{:,.2f}".format(round(partsTotalsDict["totalFinal"],2))
    #         # Nokta ile virgülü değiştirme
    #         totalTotalPrice3Fixed = totalTotalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
    #         totalDiscountFixed = totalDiscountFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
    #         totalFinalFixed = totalFinalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
    #         dataSubTotal=[[str(totalTotalPrice3Fixed) + " " + str(acceptance.currency.code)],
    #                       [str(totalDiscountFixed) + " " + str(acceptance.currency.code)],
    #                       [str(totalFinalFixed) + " " + str(acceptance.currency.code)]
    #                       ]
            
    #         table = Table(dataSubTotal, colWidths=[((w-60)/100)*12, ((w-60)/100)*12], rowHeights=13)
    #         table.setStyle(totalRightTableStyleRight)
            
    #         table.wrapOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4)+(((w-60)/100)*12), th-215-tableTotalRowHeight-39)
    #         table.drawOn(p, 30+(((w-60)/100)*5)+(((w-60)/100)*11)+(((w-60)/100)*52)+(((w-60)/100)*4)+(((w-60)/100)*4)+(((w-60)/100)*12), th-215-tableTotalRowHeight-39)
    #         tableTotalLeftLength = table._colWidths[0]
        
        
    #     p.setFont('Inter', 7)
    #     #####önemli yazı-end#####
        
    #     ######sayfa altı########
    #     p.setStrokeColor(HexColor("#808080"))
    #     p.line(30, 100, w-30, 100)
    #     p.setFont('Inter-Bold', 7)
    #     p.drawString(30, 90, sourceCompanyFormalName)
    #     p.drawString(30, 70, "Office")
    #     p.setFont('Inter', 7)
    #     p.drawString(60, 70, sourceCompanyAddress)
    #     #p.drawString(60, 70, "No:126 57/C P.K. 34947 Tuzla İstanbul TR")
    #     p.setFont('Inter-Bold', 7)
    #     p.drawString(30, 60, "Tel")
    #     p.setFont('Inter', 7)
    #     p.drawString(60, 60, sourceCompanyPhone)
    #     p.setFont('Inter-Bold', 7)
    #     p.drawString(30, 50, "Fax")
    #     p.setFont('Inter', 7)
    #     p.drawString(60, 50, sourceCompanyFax)
        
    #     lrImg = Image.open(os.path.join(os.getcwd(), "static", "images", "sale", "lr-logo4.jpg"))
        
    #     p.drawInlineImage(lrImg, 415, 46, width=150,height=50)
        
    #     p.line(30, 40, w-30, 40)
    #     p.setFont('Inter-Bold', 7)
    #     #p.drawString(30, 30, str(offer.user.first_name) + " " + str(offer.user.last_name) + " / " + str(offer.user.profile.positionType))
    #     p.setFont('Inter-Bold', 7)
    #     p.drawString(310, 30, "Document Date: " + str(datetime.today().date().strftime("%d.%m.%Y")))
    #     ######sayfa altı-end########
        
    #     #####sayfa numarası#####
    #     if len(items) > slice:
    #         p.setFont('Inter', 7)
    #         p.drawCentredString(w/2, 10, str(pageNum) + "/" + str(pageCount))
    #         pageNum = pageNum + 1
    #     #####sayfa numarası-end#####
        
    #     p.showPage()



    

    p.save()
