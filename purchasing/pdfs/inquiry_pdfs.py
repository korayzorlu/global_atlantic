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

from ..models import InquiryItem, Inquiry
from card.models import EnginePart
from source.models import Company as SourceCompany
  
def inquiryPdf(id,sourceCompanyId):
    logger = logging.getLogger("django")
    try:
        #inquiry içerisindeki part listesi
        #parts = inquiry.inquirypart_set.select_related("requestPart")
        #parts = InquiryPart.objects.filter(inquiry = inquiry).order_by("sequency")
        
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
        
        inquiry = Inquiry.objects.select_related().filter(id = id).first()
        
        parts = inquiry.inquiryitem_set.select_related("projectItem__part").order_by("sequency").all()
        items = []
        makers = []
        types = []
        for part in parts:
            if part.quantity == 0:
                quantity = int(0)
            elif part.quantity % 1 == 0:
                quantity = int(part.quantity)
            else:
                # Para miktarını belirtilen formatta gösterme
                quantity = "{:,.2f}".format(round(part.quantity,2))
                # Nokta ile virgülü değiştirme
            partNo = part.projectItem.part.partNo if part.projectItem.part.partNo else ""
            items.append({"id" : part.id,
                        "name":partNo,
                        "description" : part.projectItem.description,
                        "remark" : part.remark,
                        "quantity" : quantity,
                        "unit" : part.projectItem.unit,
                        "note" : part.note,
                        "sequency" : part.sequency,
                        })
            if part.projectItem.part.maker:
                makers.append(part.projectItem.part.maker.name)
            if part.projectItem.part.type:
                types.append(part.projectItem.part.type.type)
        
        makers = list(set(makers))
        types = list(set(types))
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

        partsTotalsDict["totalFinal"] = partsTotalsDict["totalTotalPrice3"]
        
        #standart ayar
        buffer = io.BytesIO()
        
        #dosyanın kaydedileceği konum
        folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "purchasing", "inquiry", "documents")
        
        #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
            
        #font ayarları
        rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
        pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
        
        #standart ayar
        p = canvas.Canvas(folderPath + "/" + inquiry.inquiryNo + ".pdf", pagesize = A4)
        
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
        p.drawCentredString(w/2, h-100, "INQUIRY")

        #company
        p.setFillColor(HexColor("#000"))
        p.setFont('Inter-Bold', 6)
        p.drawString(35, h-130, "TO:")
        p.setFont('Inter', 6)
        #customer
        if inquiry.supplier:
            supplierName = inquiry.supplier.name
            if inquiry.supplier.address:
                if inquiry.supplier.country:
                    supplierCountry = inquiry.supplier.country.international_formal_name
                else:
                    supplierCountry = ""
                if inquiry.supplier.city:
                    supplierCity = inquiry.supplier.city.name
                else:
                    supplierCity = ""
                supplierAddress = inquiry.supplier.address + " " + supplierCity + "/" + supplierCountry
            else:
                if inquiry.supplier.country:
                    supplierCountry = inquiry.supplier.country.international_formal_name
                else:
                    supplierCountry = ""
                if inquiry.supplier.city:
                    supplierCity = inquiry.supplier.city.name
                else:
                    supplierCity = ""
                supplierAddress = supplierCity + "/" + supplierCountry
        else:    
            supplierName = ""
            supplierAddress = ""
            
        if inquiry.supplier:
            supplierName = inquiry.supplier.name
            if inquiry.supplier.address:
                supplierAddress = inquiry.supplier.address
                if inquiry.supplier.city:
                    supplierCity = inquiry.supplier.city.name
                    supplierAddress = supplierAddress + " " + supplierCity + " /"
                if inquiry.supplier.country:
                    supplierCountry = inquiry.supplier.country.international_formal_name
                    supplierAddress = supplierAddress + " " + supplierCountry
            else:
                supplierAddress = ""
                if inquiry.supplier.city:
                    supplierCity = inquiry.supplier.city.name
                    supplierAddress = supplierAddress + " " + supplierCity + " /"
                if inquiry.supplier.country:
                    supplierCountry = inquiry.supplier.country.international_formal_name
                    supplierAddress = supplierAddress + " " + supplierCountry
        else:    
            supplierName = ""
            supplierAddress = ""
        
        #####customer name with multiple lines#####
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
        #####customer name with multiple lines-end#####
        
        #####customer address with multiple lines#####
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
        #####customer address with multiple lines-end#####
        
        #####sağ üst tablo#####
        data = [
            ["MAKER"],
            ["TYPE"],
            ["SERIAL"]
        ]
        table = Table(data, colWidths=(w/2-35)/3, rowHeights=tableRowHeight)
        table.setStyle(tableLeftStyle)
        
        table.wrapOn(p, w/2+5, h-160)
        table.drawOn(p, w/2+5, h-160)
        
        makersStr = makers[0] if len(makers) > 0 else ""
        for maker in makers[1:]:
            makersStr += f", {maker}"
        typesStr = types[0] if len(types) > 0 else ""
        for type in types[1:]:
            typesStr += f", {type}"
        data=[
            [makersStr],
            [typesStr],
            [""]
            ]
        table = Table(data, colWidths=((w/2-35)/3)*2, rowHeights=tableRowHeight)
        table.setStyle(tableRightStyle)
        
        table.wrapOn(p, (w/2+5)+(((w/2-35)/3)), h-160)
        table.drawOn(p, (w/2+5)+(((w/2-35)/3)), h-160)
        #####sağ üst tablo-end#####
        
        firstPageTableMaxHeight = 560
        firstLastPageTableMaxHeight = 530
        tableMaxHeight = 600
        lastPageTableMaxHeight = 570
        firstPage = True
        allItems = []
        partsList = []
        tableHeight = 13.2
        #####parça sayısına göre sayfa dilimleme#####
        for key, i in enumerate(range(len(items))):
            tableHeight = tableHeight + 13.2
            #####name with multiple lines#####
            #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
            name = items[i]["name"].replace("\r\n", "\n")
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
            description = items[i]["description"].replace("\r\n", "\n")
            description = description.replace("\n", " ")
            newDescription = ""
            for k in range(0, len(description), 80):
                chunk = description[k:k+80]
                if len(chunk) < 80:
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
                for k in range(0, len(remark), 80):
                    chunk = remark[k:k+80]
                    if len(chunk) < 80:
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
            if newDescription.count('\n') > newNote.count('\n') and newDescription.count('\n') > newName.count('\n'):
                tableHeight = tableHeight + (7.2 * newDescription.count('\n'))
            elif newName.count('\n') > newDescription.count('\n') and newName.count('\n') > newNote.count('\n'):
                tableHeight = tableHeight + (7.2 * newName.count('\n'))
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
            p.drawString(480, h-50, ":" + str(inquiry.inquiryDate.strftime("%d.%m.%Y")))
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
            data=[["Line", "Item", "Description", "Notes", "Qty", "Unit"]]
            
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
                for k in range(0, len(description), 80):
                    chunk = description[k:k+80]
                    if len(chunk) < 80:
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
                    for k in range(0, len(remark), 80):
                        chunk = remark[k:k+80]
                        if len(chunk) < 80:
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

                sequency = str(theItems["parts"][j]["sequency"])
                
                data.append([sequency, newName, newDescription, newNote, theItems["parts"][j]["quantity"], theItems["parts"][j]["unit"]])
            
            table = Table(data, colWidths=[((w-60)/100)*4 , ((w-60)/100)*15, ((w-60)/100)*52, ((w-60)/100)*21, ((w-60)/100)*4 , ((w-60)/100)*4])
            table.setStyle(partsTableStyleLeft)
            
            table.wrapOn(p, 30, -99999999)
            table.drawOn(p, 30, -99999999)
            tableTotalRowHeight = sum(table._rowHeights)
            table.wrapOn(p, 30, th-165-sum(table._rowHeights))
            table.drawOn(p, 30, th-165-sum(table._rowHeights))
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
            p.drawString(30, 30, str(inquiry.project.user.first_name) + " " + str(inquiry.project.user.last_name) + " / " + str(inquiry.project.user.profile.positionType))
            p.drawString(310, 30, "Document Date: " + str(datetime.today().date().strftime("%d.%m.%Y")))
            ######sayfa altı-end########
            
            #####total tablo and notes#####
            if key == len(allItems) - 1 and extraPage == 0:
                p.setFont('Inter', 7)
                p.drawString(30, th-175-sum(table._rowHeights), "Please state out reference number on all your quotations.")
                p.drawString(30, th-185-sum(table._rowHeights), "Looking forward receiving your competetive offer,")
                p.drawString(30, th-195-sum(table._rowHeights), "Best Regards")
            
            if key == len(allItems) - 1 and extraPage == 1:
                p.showPage()
                
                if len(allItems) == 1 and allItems[-1]["height"] > firstLastPageTableMaxHeight:
                    th = h + 100
                
                p.setFont('Inter', 7)
                p.drawString(30, 105, "PAGE     " + str(p.getPageNumber()) + " OF " + str(pageCount) + "     END")
                
                #####alttaki duyuru yazıları##### 
                p.setFont('Inter', 7)
                p.drawString(30, th-225, "Please state out reference number on all your quotations.")
                p.drawString(30, th-235, "Looking forward receiving your competetive offer,")
                p.drawString(30, th-245, "Best Regards")
                #####alttaki duyuru yazıları-end#####
                
                #####sayfa üstü logo#####
                p.drawInlineImage(esmsImg, 30, ystart-10, width=(esmsImg.size[0]/esmsImg.size[1])*40,height=40)
                #####sayfa üstü logo-end#####
                
                #####sağ üst yazılar#####
                p.setFont('Inter-Bold', 7)
                p.drawString(450, h-50, "DATE")
                p.setFont('Inter', 7)
                p.drawString(480, h-50, ":" + str(inquiry.inquiryDate.strftime("%d.%m.%Y")))
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
                p.drawString(30, 30, str(inquiry.project.user.first_name) + " " + str(inquiry.project.user.last_name) + " / " + str(inquiry.project.user.profile.positionType))
                p.drawString(310, 30, "Document Date: " + str(datetime.today().date().strftime("%d.%m.%Y")))
                ######sayfa altı-end########
                
            #####total tablo and notes-end#####
            
            th = h + 70
            
            p.showPage()
            
        p.save()
    except Exception as e:
        logger.exception(e)
  