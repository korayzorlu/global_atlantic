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
import logging

from ..models import InquiryItem, Inquiry, PurchaseOrder, PurchaseOrderItem
from card.models import EnginePart
from source.models import Company as SourceCompany

def purchaseOrderPdf(id, sourceCompanyId):
    logger = logging.getLogger("django")
    try:
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
            
        purchaseOrder = PurchaseOrder.objects.select_related("inquiry__project","inquiry__supplier").filter(id = id).first()
        #quotation içerisindeki part listesi
        project = purchaseOrder.inquiry.project
        
        #parts = quotation.quotationpart_set.select_related("inquiryPart")
        parts = purchaseOrder.purchaseorderitem_set.select_related("inquiryItem__projectItem__part").order_by("sequency").all()
        items = []
        for part in parts:
            items.append({"id" : part.id,
                        "name":part.name,
                        "description" : part.description,
                        "remark" : part.remark,
                        "quantity" : part.quantity,
                        "unit" : part.unit,
                        "unitPrice" : part.unitPrice,
                        "totalPrice" : part.totalPrice,
                        "currency" : purchaseOrder.currency.code,
                        "availability" : part.availability,
                        "note" : part.note,
                        "sequency" : part.sequency
                        })
        
        partsSubTotal = 0
        partsTotal = 0
        for part in parts:
            partsSubTotal = partsSubTotal + part.totalPrice
            partsTotal = partsTotal + part.totalPrice
        discountTotal = partsTotal - partsSubTotal
        
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
        folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "purchasing", "purchase_order", "documents")
        
        #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
            
        #font ayarları
        rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
        pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
        
        #standart ayar
        p = canvas.Canvas(folderPath + "/" + purchaseOrder.purchaseOrderNo + ".pdf", pagesize = A4)
        
        #standart ayar
        w, h = A4
        
        ystart = 780
        
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
                                ('FONT', (0, 0), (-1, -1), 'Inter', 5.5),
                                ])
        
        #?
        p.setLineWidth(0.5)
        
        #logo
        #esmsImg = Image.open(os.path.join(os.getcwd(), "static", "images", "esms-logo2.jpg"))
        esmsImg = Image.open(os.path.join(os.getcwd(),"media","source","companies",str(sourceCompany.id),str(sourceCompany.documentLogo.name.split('/')[-1])))

        
        #başlık
        p.setFont('Inter', 18)
        p.setFillColor(HexColor("#9d2235"))
        p.drawCentredString(w/2, h-100, "PURCHASE ORDER")
        
        #company
        p.setFillColor(HexColor("#000"))
        p.setFont('Inter-Bold', 6)
        p.drawString(35, h-130, "TO:")
        p.setFont('Inter', 6)
        #supplier
            
        if purchaseOrder.inquiry.supplier:
            supplierName = purchaseOrder.inquiry.supplier.name
            if purchaseOrder.inquiry.supplier.address:
                supplierAddress = purchaseOrder.inquiry.supplier.address
                if purchaseOrder.inquiry.supplier.city:
                    supplierCity = purchaseOrder.inquiry.supplier.city.name
                    supplierAddress = supplierAddress + " " + supplierCity + " /"
                if purchaseOrder.inquiry.supplier.country:
                    supplierCountry = purchaseOrder.inquiry.supplier.country.international_formal_name
                    supplierAddress = supplierAddress + " " + supplierCountry
            else:
                supplierAddress = ""
                if purchaseOrder.inquiry.supplier.city:
                    supplierCity = purchaseOrder.inquiry.supplier.city.name
                    supplierAddress = supplierAddress + " " + supplierCity + " /"
                if purchaseOrder.inquiry.supplier.country:
                    supplierCountry = purchaseOrder.inquiry.supplier.country.international_formal_name
                    supplierAddress = supplierAddress + " " + supplierCountry
        else:    
            supplierName = ""
            supplierAddress = ""
        
        #####supplier name with multiple lines#####
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        newSupplierName = ""
        for i in range(0, len(supplierName), 75):
            chunk = supplierName[i:i+75]
            if len(chunk) < 75:
                newSupplierName += chunk
            else:
                space_index = chunk.rfind(' ')
                if space_index != -1:
                    newSupplierName += chunk[:space_index] + '\n'
                    if space_index + 1 < len(chunk):
                        newSupplierName += chunk[space_index+1:]
                else:
                    newSupplierName += chunk
        #alt satır komutu
        lines = newSupplierName.replace("\r\n", "\n")
        lines = lines.split('\n')
        line_height = 10  # İsteğe bağlı, satır yüksekliği
        current_y = h-130

        for line in lines:
            p.drawString(50, current_y, line)
            current_y = current_y - line_height
        #####supplier name with multiple lines-end#####
        
        #####supplier address with multiple lines#####
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        supplierAddress = supplierAddress.replace("\r\n", "\n")
        supplierAddress = supplierAddress.replace("\n", " ")
        newSupplierAddress = ""
        for i in range(0, len(supplierAddress), 75):
            chunk = supplierAddress[i:i+75]
            if len(chunk) < 75:
                newSupplierAddress += chunk
            else:
                space_index = chunk.rfind(' ')
                if space_index != -1:
                    newSupplierAddress += chunk[:space_index] + '\n'
                    if space_index + 1 < len(chunk):
                        newSupplierAddress += chunk[space_index+1:]
                else:
                    newSupplierAddress += chunk
        #alt satır komutu
        lines = newSupplierAddress.replace("\r\n", "\n")
        lines = lines.split('\n')
        line_height = 10  # İsteğe bağlı, satır yüksekliği
        #current_y = h-130

        for line in lines:
            p.drawString(35, current_y, line)
            current_y = current_y - line_height
        #####supplier address with multiple lines-end#####
        
        p.drawString(35, h-190, "We thank you for your inquiry and are pleased to offer subject to unsold and subject to our")
        p.drawString(35, h-200, "standard sales & purchase conditions ( available on request) for;")
        
        #####sağ üst tablo#####
        data = [
            ["YOUR REF"],
            ["OUR REF"],
            ["PROJECT NO"],
            ["PURCHASE ORDER NO"],
            ["DELIVERY"],
            ["PAYMENT"]
        ]
        table = Table(data, colWidths=(w/2-35)/3, rowHeights=tableRowHeight)
        table.setStyle(tableLeftStyle)
        
        table.wrapOn(p, w/2+5, h-200)
        table.drawOn(p, w/2+5, h-200)
        
        data=[[purchaseOrder.inquiry.supplierRef],
            [purchaseOrder.project.customerRef],
            [purchaseOrder.project.projectNo],
            [purchaseOrder.purchaseOrderNo],
            [purchaseOrder.delivery],
            [purchaseOrder.payment]
            ]
        table = Table(data, colWidths=((w/2-35)/3)*2, rowHeights=tableRowHeight)
        table.setStyle(tableRightStyle)
        
        table.wrapOn(p, (w/2+5)+(((w/2-35)/3)), h-200)
        table.drawOn(p, (w/2+5)+(((w/2-35)/3)), h-200)
        #####sağ üst tablo-end#####
        
        
        
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
            p.drawString(480, h-50, ":" + str(purchaseOrder.purchaseOrderDate.strftime("%d.%m.%Y")))
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
            data=[["Line", "Item", "Description", "Availability", "Notes", "Qty", "Unit", "Unit Price", "Total Price"]]
            
            for j in range(len(theItems["parts"])):
                #####name with multiple lines#####
                #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
                name = theItems["parts"][j]["name"].replace("\r\n", "\n")
                name = name.replace("\n", " ")
                newName = ""
                for k in range(0, len(name), 20):
                    chunk = name[k:k+20]
                    if len(chunk) < 20:
                        newName += chunk
                    else:
                        space_index = chunk.rfind(" ")
                        if space_index != -1:
                            newName += chunk[:space_index] + '\n'
                            if space_index + 1 < len(chunk):
                                newName += chunk[space_index+1:]
                        else:
                            newName += chunk
                #alt satır komutu
                newName = newName.replace("\r\n", "\n")
                #####name with multiple lines-end#####
                
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
                
                # Para miktarını belirtilen formatta gösterme
                unitPrice3Fixed = "{:,.2f}".format(round(theItems["parts"][j]["unitPrice"],2))
                totalPrice3Fixed = "{:,.2f}".format(round(theItems["parts"][j]["totalPrice"],2))
                # Nokta ile virgülü değiştirme
                unitPrice3Fixed = unitPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalPrice3Fixed = totalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                #availability düzeltmesi
                if int(theItems["parts"][j]["availability"]) > 1:
                    availability = str(theItems["parts"][j]["availability"]) + " days"
                elif int(theItems["parts"][j]["availability"]) == 1:
                    availability = str(theItems["parts"][j]["availability"]) + " day"
                elif int(theItems["parts"][j]["availability"]) < 1:
                    availability = "EX-STOCK"
                else:
                    availability = str(theItems["parts"][j]["availability"]) + " day"

                sequency = str(theItems["parts"][j]["sequency"])
                
                data.append([sequency, newName, newDescription, availability, newNote, theItems["parts"][j]["quantity"], theItems["parts"][j]["unit"], str(unitPrice3Fixed) + " " + str(theItems["parts"][j]["currency"]), str(totalPrice3Fixed) + " " + str(theItems["parts"][j]["currency"])])
            
            table = Table(data, colWidths=[((w-60)/100)*4 , ((w-60)/100)*15, ((w-60)/100)*32, ((w-60)/100)*8, ((w-60)/100)*9, ((w-60)/100)*4 , ((w-60)/100)*4 , ((w-60)/100)*12 , ((w-60)/100)*12])
            table.setStyle(partsTableStyleLeft)
            
            table.wrapOn(p, 30, -99999999)
            table.drawOn(p, 30, -99999999)
            tableTotalRowHeight = sum(table._rowHeights)
            table.wrapOn(p, 30, th-205-sum(table._rowHeights))
            table.drawOn(p, 30, th-205-sum(table._rowHeights))
            #print(allItems[-1]["height"])
            #print(sum(table._rowHeights))
            #####parts tablo-end#####
            
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
            p.drawString(30, 30, str(purchaseOrder.project.user.first_name) + " " + str(purchaseOrder.project.user.last_name) + " / " + str(purchaseOrder.project.user.profile.positionType))
            p.drawString(310, 30, "Document Date: " + str(datetime.today().date().strftime("%d.%m.%Y")))
            ######sayfa altı-end########
            
            #####total tablo and notes#####
            if key == len(allItems) - 1 and extraPage == 0:
                dataSubTotal=[["SUB TOTAL"],
                                ["DISCOUNT"],
                                ["NET TOTAL"]
                                ]
                totalTable = Table(dataSubTotal, colWidths=((w-60)/100)*12, rowHeights=13)
                totalTable.setStyle(totalLeftTableStyleLeftTotal)
                
                totalTable.wrapOn(p, 30+(((w-60)/100)*4)+(((w-60)/100)*15)+(((w-60)/100)*32)+(((w-60)/100)*8)+(((w-60)/100)*9)+(((w-60)/100)*4)+(((w-60)/100)*4), th-205-sum(table._rowHeights)-39)
                totalTable.drawOn(p, 30+(((w-60)/100)*4)+(((w-60)/100)*15)+(((w-60)/100)*32)+(((w-60)/100)*8)+(((w-60)/100)*9)+(((w-60)/100)*4)+(((w-60)/100)*4), th-205-sum(table._rowHeights)-39)
                tableTotalLeftLength = totalTable._colWidths[0]
                
                # Para miktarını belirtilen formatta gösterme
                totalTotalPrice3Fixed = "{:,.2f}".format(round(partsTotalsDict["totalTotalPrice3"],2))
                totalDiscountFixed = "{:,.2f}".format(round(partsTotalsDict["totalDiscount"],2))
                totalFinalFixed = "{:,.2f}".format(round(partsTotalsDict["totalFinal"],2))
                # Nokta ile virgülü değiştirme
                totalTotalPrice3Fixed = totalTotalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalDiscountFixed = totalDiscountFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalFinalFixed = totalFinalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                dataSubTotal=[[str(totalTotalPrice3Fixed) + " " + purchaseOrder.currency.code],
                                [str(totalDiscountFixed) + " " + purchaseOrder.currency.code],
                                [str(totalFinalFixed) + " " + purchaseOrder.currency.code]
                                ]
                totalTable = Table(dataSubTotal, colWidths=((w-60)/100)*12, rowHeights=13)
                totalTable.setStyle(totalRightTableStyleRightTotal)
                
                totalTable.wrapOn(p, 30+(((w-60)/100)*4)+(((w-60)/100)*15)+(((w-60)/100)*32)+(((w-60)/100)*8)+(((w-60)/100)*9)+(((w-60)/100)*4)+(((w-60)/100)*4)+tableTotalLeftLength, th-205-sum(table._rowHeights)-39)
                totalTable.drawOn(p, 30+(((w-60)/100)*4)+(((w-60)/100)*15)+(((w-60)/100)*32)+(((w-60)/100)*8)+(((w-60)/100)*9)+(((w-60)/100)*4)+(((w-60)/100)*4)+tableTotalLeftLength, th-205-sum(table._rowHeights)-39)
                tableTotalLeftLength = totalTable._colWidths[0]
                
                #####alttaki note remark yazıları##### 
                p.setFont('Inter-Bold', 7)
                p.drawString(30, th-215-sum(table._rowHeights), "INVOICE TO")
                p.setFont('Inter', 7)
                p.drawString(80, th-215-sum(table._rowHeights), sourceCompanyFormalName)
                p.drawString(80, th-225-sum(table._rowHeights), sourceCompanyAddress)
                p.drawString(80, th-235-sum(table._rowHeights), "TUZLA VD. 3801139954")
                # p.drawString(30, th-245-sum(table._rowHeights), "DELIVERY")
                # p.drawString(30, th-255-sum(table._rowHeights), "PAYMENT")
            
                # p.setFont('Inter', 7)
                # p.drawString(80, th-235-sum(table._rowHeights), "ARE IN " + str(purchaseOrder.currency.code) + " / STRICTLY NETT - EACH DELIVERY TO BE TREATED AS A SEPARATE CONTRACT")
                # if purchaseOrder.delivery:
                #     p.drawString(80, th-245-sum(table._rowHeights), str(purchaseOrder.delivery))
                # else:
                #     p.drawString(80, th-245-sum(table._rowHeights), "")
                # if purchaseOrder.payment:
                #     p.drawString(80, th-255-sum(table._rowHeights), str(purchaseOrder.payment))
                # else:
                #     p.drawString(80, th-255-sum(table._rowHeights), "")
                
                p.setFont('Inter-Bold', 7)
                p.drawString(30, th-245-sum(table._rowHeights), "NOTES")
                p.setFont('Inter', 7)
                if purchaseOrder.note:
                    note = purchaseOrder.note
                    
                else:
                    note = ""
                
                #alt satır komutu
                lines = note.replace("\r\n", "\n")
                lines = lines.split('\n')
                line_height = 10  # İsteğe bağlı, satır yüksekliği
                current_y = th-245-sum(table._rowHeights)
        
                for line in lines:
                    p.drawString(80, current_y, line)
                    current_y = current_y - line_height
                
                p.setFont('Inter-Bold', 7)
                #p.drawString(30, current_y, "REMARK")
                p.setFont('Inter', 7)
                # if purchaseOrder.remark:
                #     p.drawString(80, current_y, str(purchaseOrder.remark))
                # else:
                #     p.drawString(80, current_y, "")
                #####alttaki note remark yazıları-end#####
                
            if key == len(allItems) - 1 and extraPage == 1:
                p.showPage()
                
                if len(allItems) == 1 and allItems[-1]["height"] > firstLastPageTableMaxHeight:
                    th = h + 120
                
                p.setFont('Inter', 7)
                p.drawString(30, 105, "PAGE     " + str(p.getPageNumber()) + " OF " + str(pageCount) + "     END")
                
                dataSubTotal=[["SUB TOTAL"],
                                ["DISCOUNT"],
                                ["NET TOTAL"]
                                ]
                totalTable = Table(dataSubTotal, colWidths=((w-60)/100)*12, rowHeights=13)
                totalTable.setStyle(totalLeftTableStyleLeftTotal)
                
                totalTable.wrapOn(p, 30+(((w-60)/100)*4)+(((w-60)/100)*15)+(((w-60)/100)*32)+(((w-60)/100)*8)+(((w-60)/100)*9)+(((w-60)/100)*4)+(((w-60)/100)*4), th-205-39)
                totalTable.drawOn(p, 30+(((w-60)/100)*4)+(((w-60)/100)*15)+(((w-60)/100)*32)+(((w-60)/100)*8)+(((w-60)/100)*9)+(((w-60)/100)*4)+(((w-60)/100)*4), th-205-39)
                tableTotalLeftLength = totalTable._colWidths[0]
                
                # Para miktarını belirtilen formatta gösterme
                totalTotalPrice3Fixed = "{:,.2f}".format(round(partsTotalsDict["totalTotalPrice3"],2))
                totalDiscountFixed = "{:,.2f}".format(round(partsTotalsDict["totalDiscount"],2))
                totalFinalFixed = "{:,.2f}".format(round(partsTotalsDict["totalFinal"],2))
                # Nokta ile virgülü değiştirme
                totalTotalPrice3Fixed = totalTotalPrice3Fixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalDiscountFixed = totalDiscountFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                totalFinalFixed = totalFinalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                dataSubTotal=[[str(totalTotalPrice3Fixed) + " " + purchaseOrder.currency.code],
                                [str(totalDiscountFixed) + " " + purchaseOrder.currency.code],
                                [str(totalFinalFixed) + " " + purchaseOrder.currency.code]
                                ]
                totalTable = Table(dataSubTotal, colWidths=((w-60)/100)*12, rowHeights=13)
                totalTable.setStyle(totalRightTableStyleRightTotal)
                
                totalTable.wrapOn(p, 30+(((w-60)/100)*4)+(((w-60)/100)*15)+(((w-60)/100)*32)+(((w-60)/100)*8)+(((w-60)/100)*9)+(((w-60)/100)*4)+(((w-60)/100)*4)+tableTotalLeftLength, th-205-39)
                totalTable.drawOn(p, 30+(((w-60)/100)*4)+(((w-60)/100)*15)+(((w-60)/100)*32)+(((w-60)/100)*8)+(((w-60)/100)*9)+(((w-60)/100)*4)+(((w-60)/100)*4)+tableTotalLeftLength, th-205-39)
                tableTotalLeftLength = totalTable._colWidths[0]
                
                #####alttaki note remark yazıları##### 
                p.setFont('Inter-Bold', 7)
                p.drawString(30, th-235, "INVOICE TO")
                p.setFont('Inter', 7)
                p.drawString(80, th-235, sourceCompanyFormalName)
                p.drawString(80, th-245, sourceCompanyAddress)
                p.drawString(80, th-255, "TUZLA VD. 3801139954")
                # p.drawString(30, th-245, "DELIVERY")
                # p.drawString(30, th-255, "PAYMENT")
            
                # p.setFont('Inter', 7)
                # p.drawString(80, th-235, "ARE IN " + str(purchaseOrder.currency.code) + " / STRICTLY NETT - EACH DELIVERY TO BE TREATED AS A SEPARATE CONTRACT")
                # if purchaseOrder.delivery:
                #     p.drawString(80, th-245, str(purchaseOrder.delivery))
                # else:
                #     p.drawString(80, th-245, "")
                # if purchaseOrder.payment:
                #     p.drawString(80, th-255, str(purchaseOrder.payment))
                # else:
                #     p.drawString(80, th-255, "")
                
                p.setFont('Inter-Bold', 7)
                p.drawString(30, th-265, "NOTES")
                p.setFont('Inter', 7)
                if purchaseOrder.note:
                    note = purchaseOrder.note
                    
                else:
                    note = ""
                #alt satır komutu
                lines = note.replace("\r\n", "\n")
                lines = lines.split('\n')
                line_height = 10  # İsteğe bağlı, satır yüksekliği
                current_y = th-265
        
                for line in lines:
                    p.drawString(80, current_y, line)
                    current_y = current_y - line_height
                
                p.setFont('Inter-Bold', 7)
                #p.drawString(30, current_y, "REMARK")
                # p.setFont('Inter', 7)
                # if purchaseOrder.remark:
                #     p.drawString(80, current_y, str(purchaseOrder.remark))
                # else:
                #     p.drawString(80, current_y, "")
                #####alttaki note remark yazıları-end#####
                
                #####sayfa üstü logo#####
                p.drawInlineImage(esmsImg, 30, ystart-10, width=(esmsImg.size[0]/esmsImg.size[1])*40,height=40)
                #####sayfa üstü logo-end#####
                
                #####sağ üst yazılar#####
                p.setFont('Inter-Bold', 7)
                p.drawString(450, h-50, "DATE")
                p.setFont('Inter', 7)
                p.drawString(480, h-50, ":" + str(purchaseOrder.purchaseOrderDate.strftime("%d.%m.%Y")))
                #####sağ üst yazılar-end#####
                
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
                p.drawString(30, 30, str(purchaseOrder.project.user.first_name) + " " + str(purchaseOrder.project.user.last_name) + " / " + str(purchaseOrder.project.user.profile.positionType))
                p.drawString(310, 30, "Document Date: " + str(datetime.today().date().strftime("%d.%m.%Y")))
                ######sayfa altı-end########
                
            #####total tablo and notes-end#####
            
            th = h + 120
            
            p.showPage()
            
        p.save()
    except Exception as e:
        logger.exception(e)
