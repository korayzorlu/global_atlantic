from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab import rl_config
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.tables import Table
from reportlab.platypus import TableStyle, Paragraph, KeepTogether, SimpleDocTemplate, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER

import os
import io

from datetime import datetime

def pdf_settings(path,fileName):
    #standart ayar
    buffer = io.BytesIO()
    
    #dosyanın kaydedileceği konum
    folderPath = path
    
    #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    
    #font ayarları
    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
    pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
    
    #standart ayar
    p = canvas.Canvas(f"{folderPath}/{fileName}", pagesize = A4)
    
    #standart ayar
    w, h = A4

    p.setLineWidth(0.5)

    return p, w, h

def pdf_header(p,w,h,headerHeight,logo=None):
    #logo
    if logo:
        logoHeight = 40
        logoWidth = (logo.size[0]/logo.size[1])*40
        p.drawInlineImage(logo, 30, h - headerHeight + ((headerHeight-logoHeight)/2), width=logoWidth,height=logoHeight)
    
    #date
    # dateWidth = pdfmetrics.stringWidth(str(datetime.today().date().strftime("%d.%m.%Y")), "Inter-Bold", 6)
    # p.setFont('Inter', 6)
    # p.drawString(w-dateWidth-30, h - headerHeight + ((headerHeight-6)/2), str(datetime.today().date().strftime("%d.%m.%Y")))

    #title
    titleTableStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 9),
                                        ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                                        ('VALIGN',(0,0),(-1,-1),'MIDDLE')
                                    ])
    
    data=[["STATEMENT OF ACCOUNT"]
    ]
    table = Table(data, rowHeights=9+5)
    table.setStyle(titleTableStyle)
    
    table.wrapOn(p, w, h-50)
    tableWidth = sum(table._colWidths)
    tableHeight = sum(table._rowHeights)

    table.drawOn(p, w-tableWidth-30, h - headerHeight + ((headerHeight-tableHeight)/2))

def pdf_header_for_invoice(p,w,h,headerHeight,headerText,invoiceNo,logo=None):
    p.saveState()
    #logo
    if logo:
        logoHeight = 40
        logoWidth = (logo.size[0]/logo.size[1])*40
        p.drawInlineImage(logo, 30, h - headerHeight + ((headerHeight-logoHeight)/2), width=logoWidth,height=logoHeight)
        

    #title
    titleTableStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                        ('FONT', (0, 0), (-1, -1), 'Inter', 9),
                                        ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                                        ('VALIGN',(0,0),(-1,-1),'MIDDLE')
                                    ])
    
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.fontName = "Inter"
    styleN.fontSize = 9
    styleN.alignment = TA_CENTER

    data=[
        [Paragraph(f"<font name='Inter-Bold'><b>{headerText}</b></font><br/>",styleN)],
        [invoiceNo]
    ]
    table = Table(data,colWidths=(w/2-35)/2)
    table.setStyle(titleTableStyle)
    
    table.wrapOn(p, w, h-50)
    tableWidth = sum(table._colWidths)
    tableHeight = sum(table._rowHeights)

    table.drawOn(p, w-tableWidth-30, h - headerHeight + ((headerHeight-tableHeight)/2))
    p.restoreState()


def pdf_project_info_table_for_invoice(p,w,h,headerHeight,footerHeight,contentHeight,yPosition,sourceCompany,logo,invoiceNo,projectData):
    tableLeftStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                            ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                            ('FONT', (0, 0), (-1, -1), 'Inter-Bold', 6),
                            ('BACKGROUND',(0,0), (0,-1), "#c7d3e1")
                            ])
    
    dataTableLeft=[
        ["PROJE NO / PROJECT NO",projectData["projectNo"]],
        ["SİPARİŞ TARİHİ / ORDER DATE",projectData["orderDate"]],
        ["TESLİMAT ŞEKLİ / DELİVERY TYPE",projectData["deliveryType"]],
        ["TESLİMAT NO / DELİVERY NO",projectData["deliveryNo"]]
    ]

    dataTableRight=[
        ["MAKER",projectData["maker"]],
        ["TİP / TYPE",projectData["makerType"]],
        ["MÜŞTERİ REF / CUSTOMER REF",projectData["customerRef"]],
        ["ÖDEME ŞEKLİ / PAYMENT TERM",projectData["payment"]]
    ]

    tableLeft = Table(dataTableLeft,colWidths=(w/2-35)/2)
    tableLeft.setStyle(tableLeftStyle)

    tableRight = Table(dataTableRight,colWidths=(w/2-35)/2)
    tableRight.setStyle(tableLeftStyle)

    page_width, page_height = A4
    tableLeftWidth, tableLeftHeight = tableLeft.wrap(page_width, page_height)
    tableRightWidth, tableRightHeight = tableRight.wrap(page_width, page_height)

    tableHeight = tableLeftHeight
    if yPosition - tableHeight < footerHeight:
        p.showPage()
        pdf_header_for_invoice(p,w,h,headerHeight,invoiceNo,logo)
        pdf_footer(p,w,h,footerHeight,sourceCompany)
        yPosition = h - headerHeight

    tableLeft.wrapOn(p, 30, contentHeight)
    tableLeft.drawOn(p, 30, yPosition - tableHeight)

    tableRight.wrapOn(p, w/2+5, contentHeight)
    tableRight.drawOn(p, w/2+5, yPosition - tableHeight)

    return yPosition - tableHeight, tableHeight

def pdf_footer(p,w,h,footerHeight,sourceCompany):
    #page number
    p.setFont('Inter', 7)
    p.drawString(30, footerHeight - 10 + 2, f"PAGE {p.getPageNumber()}")
    
    #line
    p.setStrokeColor(HexColor("#808080"))
    p.line(30, footerHeight - 10, w-30, footerHeight - 10)
    p.line(30, 40, w-30, 40)

    #text
    fontSize = 7
    lineHeigth = fontSize + 4
    textsHeight = (fontSize+4)*5

    p.setFont('Inter-Bold', 7)
    p.drawString(30, 40+2+2.5+lineHeigth+lineHeigth+lineHeigth+lineHeigth, sourceCompany.formalName if sourceCompany.formalName else "")

    p.setFont('Inter-Bold', 7)
    p.drawString(30, 40+2+2.5+lineHeigth+lineHeigth, "Office")
    p.setFont('Inter', 7)
    p.drawString(60, 40+2+2.5+lineHeigth+lineHeigth, sourceCompany.address if sourceCompany.address else "")

    p.setFont('Inter-Bold', 7)
    p.drawString(30, 40+2+2.5+lineHeigth, "Tel")
    p.setFont('Inter', 7)
    p.drawString(60, 40+2+2.5+lineHeigth, sourceCompany.phone1 if sourceCompany.phone1 else "")

    p.setFont('Inter-Bold', 7)
    p.drawString(30, 40+2+2.5, "Fax")
    p.setFont('Inter', 7)
    p.drawString(60, 40+2+2.5, sourceCompany.fax if sourceCompany.fax else "")
    

    #date
    dateWidth = pdfmetrics.stringWidth(f"Document Date: {str(datetime.today().date().strftime('%d.%m.%Y'))}", "Inter", 7)
    p.setFont('Inter', 7)
    p.drawString(w-dateWidth-30, 30, f"Document Date: {str(datetime.today().date().strftime('%d.%m.%Y'))}")

def pdf_table_styles():
    defaultStyle = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Inter-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ])

    partsTableStyleLeftZero = TableStyle([('INNERGRID', (0,2), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
        ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
        ('BOX', (0,0), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
        ('FONT', (0, 0), (-1, -1), 'Inter', 6),
        ('FONT', (0, 0), (-1, 2), 'Inter-Bold', 6),
        ('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
        ('ALIGN', (0, 0), (-1, -1), "LEFT"),
        ('ALIGN', (5, 0), (-1, -1), "RIGHT"),
        ('TEXTCOLOR',(0,1), (-1,1), colors.white),
        ('TEXTCOLOR',(0,2), (-1,2), colors.white),
        #('BACKGROUND',(0,0), (-1,0), "#009999"),
        ('BACKGROUND',(0,0), (-1,0), "rgba(0,56,101,0.40)"),
        ('BACKGROUND',(0,1), (-1,1), "#9d2235"),
        ('BACKGROUND',(0,2), (-1,2), "#003865"),
        ('BACKGROUND',(6,-1), (-1,-1), "rgba(0,56,101,0.40)"),
        ('INNERGRID', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('BOX', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('VALIGN', (0, 0), (-1, -1), "TOP")
    ])
    partsTableStyleLeft = TableStyle([('INNERGRID', (0,1), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
        ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
        ('BOX', (0,0), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
        ('FONT', (0, 0), (-1, -1), 'Inter', 6),
        ('FONT', (0, 0), (-1, 1), 'Inter-Bold', 6),
        ('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
        ('ALIGN', (0, 0), (-1, -1), "LEFT"),
        ('ALIGN', (5, 0), (-1, -1), "RIGHT"),
        ('TEXTCOLOR',(0,0), (-1,1), colors.white),
        #('BACKGROUND',(0,0), (-1,0), "#009999"),
        ('BACKGROUND',(0,0), (-1,0), "#9d2235"),
        ('BACKGROUND',(0,1), (-1,1), "#003865"),
        ('BACKGROUND',(6,-1), (-1,-1), "rgba(0,56,101,0.40)"),
        ('INNERGRID', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('BOX', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('VALIGN', (0, 0), (-1, -1), "TOP"),
        ("WORDWRAP", (0, 0), (-1, -1), True)
    ])
    itemsTableStyleLeft = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                    ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                     ('ALIGN', (0, 0), (0, -1), "RIGHT"),
                                    ('BACKGROUND',(0,0), (-1,0), "#c7d3e1")
    ])
    partsTableStyleLeftNoTitle = TableStyle([('INNERGRID', (0,1), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
        ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
        ('BOX', (0,0), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
        ('FONT', (0, 0), (-1, -1), 'Inter', 6),
        ('FONT', (0, 0), (-1, 0), 'Inter-Bold', 6),
        ('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
        ('ALIGN', (0, 0), (-1, -1), "LEFT"),
        ('ALIGN', (5, 0), (-1, -1), "RIGHT"),
        ('TEXTCOLOR',(0,0), (-1,0), colors.white),
        #('BACKGROUND',(0,0), (-1,0), "#009999"),
        ('BACKGROUND',(0,0), (-1,0), "#003865"),
        ('BACKGROUND',(6,-1), (-1,-1), "rgba(0,56,101,0.40)"),
        ('INNERGRID', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('BOX', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('VALIGN', (0, 0), (-1, -1), "TOP")
    ])
    partsTableStyleLeftBasic = TableStyle([('INNERGRID', (0,0), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
        ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
        ('BOX', (0,0), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
        ('FONT', (0, 0), (-1, -1), 'Inter', 6),
        ('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
        ('ALIGN', (0, 0), (-1, -1), "LEFT"),
        ('ALIGN', (5, 0), (-1, -1), "RIGHT"),
        ('BACKGROUND',(6,-1), (-1,-1), "rgba(0,56,101,0.40)"),
        ('INNERGRID', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('BOX', (6,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('VALIGN', (0, 0), (-1, -1), "TOP"),
        ("WORDWRAP", (0, 0), (-1, -1), True)
    ])
    partsTableStyleCustomer = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('FONT', (0,0), (-1,-1), 'Inter-Bold', 10),
        ('ALIGN', (0,0), (-1,-1), "LEFT"),
        ('TEXTCOLOR',(0,0), (-1,-1), colors.black),
        ('BACKGROUND',(0,0), (-1,-1), "#ffdf00"),
        ('VALIGN', (0,0), (-1,-1), "MIDDLE")
    ])
    partsTableStyleSupplier = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('FONT', (0,0), (-1,-1), 'Inter-Bold', 10),
        ('ALIGN', (0,0), (-1,-1), "LEFT"),
        ('TEXTCOLOR',(0,0), (-1,-1), colors.white),
        ('BACKGROUND',(0,0), (-1,-1), "#9d2235"),
        ('VALIGN', (0,0), (-1,-1), "MIDDLE")
    ])
    totalTableStyle = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
        ('FONT', (0,0), (-1,1), 'Inter-Bold', 6),
        ('FONT', (0,1), (-1,-1), 'Inter', 6),
        ('ALIGN', (0,0), (-1,-1), "LEFT"),
        ('ALIGN', (1,2), (-1,-1), "RIGHT"),
        ('TEXTCOLOR',(0,0), (-1,2), colors.white),
        ('TEXTCOLOR',(0,2), (-1,-1), colors.black),
        ('BACKGROUND',(0,0), (-1,0), "#9d2235"),
        ('BACKGROUND',(0,1), (-1,1), "#003865"),
        ('VALIGN', (0,0), (-1,-1), "MIDDLE")
    ])

    return defaultStyle, itemsTableStyleLeft, partsTableStyleLeftZero, partsTableStyleLeft, partsTableStyleLeftNoTitle, partsTableStyleLeftBasic, partsTableStyleCustomer, partsTableStyleSupplier, totalTableStyle


def pdf_sub_line(text, length):
    #####text with multiple lines#####
    #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
    if text:
        newText = ""
        for k in range(0, len(text), length):
            chunk = text[k:k+length]
            if len(chunk) < length:
                newText += chunk
            else:
                space_index = chunk.rfind(" ")
                if space_index != -1:
                    newText += chunk[:space_index] + '\n'
                    if space_index + 1 < len(chunk):
                        newText += chunk[space_index+1:]
                else:
                    newText += chunk
        #alt satır komutu
        newText = newText.replace("\r\n", "\n")
    else:
        newText = ""
    #####text with multiple lines-end#####

    return newText

def get_address(company):
    if company.address:
        address = company.address
        if company.city:
            billingCity = company.city.name
            address = address + " " + billingCity + " /"
        if company.country:
            billingCountry = company.country.international_formal_name
            address = address + " " + billingCountry
    else:
        address = ""
        if company.city:
            billingCity = company.city.name
            address = address + " " + billingCity + " /"
        if company.country:
            billingCountry = company.country.international_formal_name
            address = address + " " + billingCountry

    return address
