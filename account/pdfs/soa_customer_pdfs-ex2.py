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

import os
import io
import shutil
from django.utils import timezone
from datetime import datetime
from decimal import Decimal

import logging

from ..models import SendInvoice, IncomingInvoice, ProformaInvoiceExpense,ProformaInvoiceItem, SendInvoicePart, SendInvoiceExpense,SendInvoiceItem,CommericalInvoice,CommericalInvoiceItem,CommericalInvoiceExpense
from card.models import EnginePart, Vessel, Billing, Company
from sale.models import QuotationPart
from source.models import Company as SourceCompany

def soaCustomerPdf(sourceCompanyId):
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
            
        sendInvoices = SendInvoice.objects.filter(payed = False).order_by("id").annotate(num_vessels=Count('vessel')).order_by('-num_vessels', 'vessel', 'customer__name')
        if sendInvoices:
            items = []
        else:
            items = [{
                        "customerId":"",
                        "customerName":"",
                        "vesselType":"",
                        "vessel":"",
                        "billing":"",
                        "request":"",
                        "invoiceNo":"",
                        "invoiceDate":"",
                        "dueDate":"",
                        "totalPrice":"",
                        "paidPrice":"",
                        "balance":"",
                        "currency":""
            }]
        usdCount = 0
        eurCount = 0
        gbpCount = 0
        qarCount = 0
        rubCount = 0
        jpyCount = 0
        tryCount = 0
        currencyList = []
        extraLineHeight = 0
        customerList = []
        
        for sendInvoice in sendInvoices:
            if sendInvoice.customer:
                customerId = sendInvoice.customer.id
                customerName = sendInvoice.customer.name
            else:
                customerId = ""
                customerName = ""
            if sendInvoice.billing:
                billing = sendInvoice.billing.name
            else:
                billing = ""
            if sendInvoice.vessel:
                vesselType = sendInvoice.vessel.get_type_display()
                vessel = sendInvoice.vessel.name
            else:
                vesselType = ""
                vessel = ""
            if sendInvoice.theRequest:
                project = sendInvoice.theRequest.requestNo
            elif sendInvoice.offer:
                project = sendInvoice.offer.offerNo
            else:
                project = ""
                
            items.append({
                        "customerId":customerId,
                        "customerName":customerName,
                        "vesselType":vesselType,
                        "vessel":vessel,
                        "billing":billing,
                        "request":project,
                        "invoiceNo":sendInvoice.sendInvoiceNo,
                        "invoiceDate":sendInvoice.sendInvoiceDate.strftime("%d.%m.%Y"),
                        "dueDate":sendInvoice.paymentDate.strftime("%d.%m.%Y"),
                        "totalPrice":sendInvoice.totalPrice,
                        "paidPrice":sendInvoice.paidPrice,
                        "balance":"",
                        "currency":sendInvoice.currency.code
            })
            if sendInvoice.currency.code == "USD":
                usdCount = usdCount + 1
                currencyList.append("USD")
            elif sendInvoice.currency.code == "EUR":
                eurCount = eurCount + 1
                currencyList.append("EUR")
            elif sendInvoice.currency.code == "GBP":
                gbpCount = gbpCount + 1
                currencyList.append("GBP")
            elif sendInvoice.currency.code == "QAR":
                qarCount = qarCount + 1
                currencyList.append("QAR")
            elif sendInvoice.currency.code == "RUB":
                rubCount = rubCount + 1
                currencyList.append("RUB")
            elif sendInvoice.currency.code == "JPY":
                jpyCount = jpyCount + 1
                currencyList.append("JPY")
            elif sendInvoice.currency.code == "TRY":
                tryCount = tryCount + 1
                currencyList.append("TRY")

            customerList.append(sendInvoice.customer)

        customerList = list(set(customerList))
        currencyList = list(set(currencyList))
        logger.info(currencyList)
        if len(currencyList) > 1:
            extraLineHeight = 14 * (len(currencyList) - 1)
            
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
        p = canvas.Canvas(f"{folderPath}/soa-customer-list.pdf", pagesize = A4)
        
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
                                    ('TEXTCOLOR',(0,0), (-1,-1), colors.white),
                                    ('BACKGROUND',(0,0), (-1,-1), "#9d2235")
                                ])
        tableLeftStyleAmount = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                                        ('BOX', (0,0), (-1,-1), 0.25, colors.grey),
                                        ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                        ('FONT', (0, 0), (0,-1), 'Inter-Bold', 6),
                                        ('TEXTCOLOR',(0,0), (0,-1), colors.white),
                                        ('ALIGN', (0, 0), (0, -1), "LEFT"),
                                        ('ALIGN', (1, 0), (1, -1), "RIGHT"),
                                        ('BACKGROUND',(0,0), (0,-1), "#9d2235"),
                                        ('VALIGN', (0, 0), (-1, -1), "TOP")
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
        
        p.setFillColor(HexColor("#000"))
        
        #####sağ üst tablo2#####
        totalAmountText = ""
        totalDueAmountText = ""
        for key, currency in enumerate(currencyList):
            sendInvoicess = SendInvoice.objects.filter(currency__code = currency)
            sendInvoiceAmountTotal = 0
            sendInvoiceDueAmountTotal = 0
            for sendInvoicee in sendInvoicess:
                sendInvoiceAmountTotal = sendInvoiceAmountTotal + (sendInvoicee.totalPrice - sendInvoicee.paidPrice)
                if sendInvoicee.paymentDate < timezone.now().date():
                    sendInvoiceDueAmountTotal = sendInvoiceDueAmountTotal + (sendInvoicee.totalPrice - sendInvoicee.paidPrice)
            # Para miktarını belirtilen formatta gösterme
            sendInvoiceAmountTotalFixed = "{:,.2f}".format(round(sendInvoiceAmountTotal,2))
            sendInvoiceDueAmountTotalFixed = "{:,.2f}".format(round(sendInvoiceDueAmountTotal,2))
            # Nokta ile virgülü değiştirme
            sendInvoiceAmountTotalFixed = sendInvoiceAmountTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            sendInvoiceDueAmountTotalFixed = sendInvoiceDueAmountTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            keyCount = key + 1
            if keyCount == len(currencyList):
                totalAmountText = totalAmountText + str(sendInvoiceAmountTotalFixed) + " " + str(currency)
                totalDueAmountText = totalDueAmountText + str(sendInvoiceDueAmountTotalFixed) + " " + str(currency)
            else:
                totalAmountText = totalAmountText + str(sendInvoiceAmountTotalFixed) + " " + str(currency) + "\n"
                totalDueAmountText = totalDueAmountText + str(sendInvoiceDueAmountTotalFixed) + " " + str(currency) + "\n"
        data=[["TOTAL AMOUNT", totalAmountText],
            ["T. O/DUE AMOUNT", totalDueAmountText]
            ]
        table = Table(data, colWidths=[((w/2-35)/2/2)-(5/2),((w/2-35)/2/2)-(5/2)])
        table.setStyle(tableLeftStyleAmount)
        
        table.wrapOn(p, (w/2+5)+((w/2-35)/2)+5, h-115-extraLineHeight)
        table.drawOn(p, (w/2+5)+((w/2-35)/2)+5, h-115-extraLineHeight)
        #####sağ üst tablo2-end#####
        
        
        
        #####parça sayısına göre sayfa dilimleme#####
        #standart ayar
        slice = 38
        pageNum = 1
        pageCount = len(items) // slice
        #standart ayar
        if len(items) % slice != 0:
            pageCount = pageCount + 1
        #standart ayar
        balanceTotal = 0
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

            data=[["STATEMENT OF ACCOUNT"]
            ]
            table = Table(data, colWidths=(w/2-35)/2, rowHeights=tableRowHeight+5)
            table.setStyle(invoiceTableStyleTitle)
            
            table.wrapOn(p, (w/2+5)+((w/2-35)/2), h-50)
            table.drawOn(p, (w/2+5)+((w/2-35)/2), h-50)
            
            p.setFont('Inter-Bold', 6)
            p.drawString((w/2+5)+((w/2-35)/2), h-67, "DATE: ")
            p.setFont('Inter', 6)
            p.drawString((w/2+5)+((w/2-35)/2)+30, h-67, str(datetime.today().date().strftime("%d.%m.%Y")))
            #####sağ üst yazılar-end#####
            
            if i >= slice:
                th = h+150
            else:
                th = h
                
            #####parts tablo#####
            
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
                                    ('VALIGN', (0, 0), (-1, -1), "TOP")
                                    ])
            partsTableStyleCustomer = TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0,0), (-1,-1), 'Inter-Bold', 8),
                                    ('ALIGN', (0,0), (-1,-1), "LEFT"),
                                    ('TEXTCOLOR',(0,0), (-1,-1), colors.black),
                                    ('BACKGROUND',(0,0), (-1,-1), "#ffdf00"),
                                    ('VALIGN', (0,0), (-1,-1), "TOP")
                                    ])
            

            
            for index,customer in enumerate(customerList):
                data=[[customer.name]
                    ]
                
                tablecustomer = Table(data, colWidths=[((w-60)/100)*100])
                tablecustomer.setStyle(partsTableStyleCustomer)
                
                tablecustomer.wrapOn(p, 30, -99999999)
                tablecustomer.drawOn(p, 30, -99999999)

                tableTotalRowHeight = tableTotalRowHeight + sum(tablecustomer._rowHeights)

                if index == 0:
                    tablecustomer.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight)
                    tablecustomer.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight)
                else:
                    tablecustomer.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                    tablecustomer.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)

                partsList = [item for item in items if item["customerId"] == customer.id]

                ##########usd talo##########
                
                if usdCount > 0:
                
                    data=[["USD STATEMENT OF ACCOUNT IS AS SHOWN BELOW"]
                        ]
                    
                    
                    previous_vessel = None
                    tableStyleControlKey = 0
                    for k in range(len(partsList)):
                        current_vessel = partsList[k]["vessel"]
                        if current_vessel != previous_vessel:
                            #her yeni vessel için döngü
                            data.append([partsList[k]["billing"]])
                            data.append(["Vessel", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"])
                            rowLengths = []
                            projectsList = []
                            balanceTotal = 0
                            for j in range(len(partsList)):
                                if partsList[j]["currency"] == "USD" and partsList[j]["vessel"] == current_vessel:
                                    projectsList.append(partsList[j])
                                    # Para miktarını belirtilen formatta gösterme
                                    totalPriceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                                    paidPriceFixed = "{:,.2f}".format(round(partsList[j]["paidPrice"],2))
                                    balanceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"] - partsList[j]["paidPrice"],2))
                                    # Nokta ile virgülü değiştirme
                                    totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    rowLengths.append(partsList[j])
                                    
                                    serviceCardsSequency = serviceCardsSequency + 1
                                    data.append([str(partsList[j]["vesselType"]) + " " + str(partsList[j]["vessel"]), partsList[j]["request"], partsList[j]["invoiceNo"], partsList[j]["invoiceDate"], partsList[j]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[j]["currency"]])
                                    
                                    balanceTotal = balanceTotal + (partsList[j]["totalPrice"] - partsList[j]["paidPrice"])
                            
                            # Para miktarını belirtilen formatta gösterme
                            balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
                            # Nokta ile virgülü değiştirme
                            balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                            
                            data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "USD"])
                            table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
                            if tableStyleControlKey == 0:
                                table1.setStyle(partsTableStyleLeftZero)
                            else:
                                table1.setStyle(partsTableStyleLeft)
                            
                            table1.wrapOn(p, 30, -99999999)
                            table1.drawOn(p, 30, -99999999)
                            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
                            table1TotalRowHeight = sum(table1._rowHeights)
                            if len(projectsList) > 0:
                                tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                                table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                                table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                                tableSpace = tableSpace + 10
                            
                            #her yeni vessel için döngü-end
                            data = []
                            tableStyleControlKey = tableStyleControlKey + 1
                            previous_vessel = current_vessel

                        
                ##########usd talo-end##########
                
                ##########eur talo##########
                if eurCount > 0:
                
                    data=[["EUR STATEMENT OF ACCOUNT IS AS SHOWN BELOW"]
                        ]
                    
                    previous_vessel = None
                    tableStyleControlKey = 0
                    for k in range(len(partsList)):
                        current_vessel = partsList[k]["vessel"]
                        if current_vessel != previous_vessel:
                            #her yeni vessel için döngü
                            data.append([partsList[k]["billing"]])
                            data.append(["Vessel", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"])
                            rowLengths = []
                            projectsList = []
                            balanceTotal = 0
                            for j in range(len(partsList)):
                                if partsList[j]["currency"] == "EUR" and partsList[j]["vessel"] == current_vessel:
                                    projectsList.append(partsList[j])
                                    # Para miktarını belirtilen formatta gösterme
                                    totalPriceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                                    paidPriceFixed = "{:,.2f}".format(round(partsList[j]["paidPrice"],2))
                                    balanceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"] - partsList[j]["paidPrice"],2))
                                    # Nokta ile virgülü değiştirme
                                    totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    rowLengths.append(partsList[j])
                                    
                                    serviceCardsSequency = serviceCardsSequency + 1
                                    data.append([str(partsList[j]["vesselType"]) + " " + str(partsList[j]["vessel"]), partsList[j]["request"], partsList[j]["invoiceNo"], partsList[j]["invoiceDate"], partsList[j]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[j]["currency"]])
                                    
                                    balanceTotal = balanceTotal + (partsList[j]["totalPrice"] - partsList[j]["paidPrice"])
                            
                            # Para miktarını belirtilen formatta gösterme
                            balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
                            # Nokta ile virgülü değiştirme
                            balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                            
                            data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "EUR"])
                            table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
                            if tableStyleControlKey == 0:
                                table1.setStyle(partsTableStyleLeftZero)
                            else:
                                table1.setStyle(partsTableStyleLeft)
                    
                            
                            table1.wrapOn(p, 30, -99999999)
                            table1.drawOn(p, 30, -99999999)
                            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
                            table1TotalRowHeight = sum(table1._rowHeights)
                            if len(projectsList) > 0:
                                tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                                table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                                table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                                tableSpace = tableSpace + 10
                            
                            #her yeni vessel için döngü-end
                            data = []
                            tableStyleControlKey = tableStyleControlKey + 1
                            previous_vessel = current_vessel
                            
                ##########eur talo-end##########
                
                ##########try talo##########
                if tryCount > 0:
                
                    data=[["TRY STATEMENT OF ACCOUNT IS AS SHOWN BELOW"]
                        ]
                    
                    previous_vessel = None
                    tableStyleControlKey = 0
                    for k in range(len(partsList)):
                        current_vessel = partsList[k]["vessel"]
                        if current_vessel != previous_vessel:
                            #her yeni vessel için döngü
                            data.append([partsList[k]["billing"]])
                            data.append(["Vessel", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"])
                            rowLengths = []
                            projectsList = []
                            balanceTotal = 0
                            for j in range(len(partsList)):
                                if partsList[j]["currency"] == "TRY" and partsList[j]["vessel"] == current_vessel:
                                    projectsList.append(partsList[j])
                                    
                                    # Para miktarını belirtilen formatta gösterme
                                    totalPriceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                                    paidPriceFixed = "{:,.2f}".format(round(partsList[j]["paidPrice"],2))
                                    balanceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"] - partsList[j]["paidPrice"],2))
                                    # Nokta ile virgülü değiştirme
                                    totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    rowLengths.append(partsList[j])
                                    
                                    serviceCardsSequency = serviceCardsSequency + 1
                                    data.append([str(partsList[j]["vesselType"]) + " " + str(partsList[j]["vessel"]), partsList[j]["request"], partsList[j]["invoiceNo"], partsList[j]["invoiceDate"], partsList[j]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[j]["currency"]])
                                    
                                    balanceTotal = balanceTotal + (partsList[j]["totalPrice"] - partsList[j]["paidPrice"])
                            
                            # Para miktarını belirtilen formatta gösterme
                            balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
                            # Nokta ile virgülü değiştirme
                            balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                            
                            data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "TRY"])
                            table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
                            if tableStyleControlKey == 0:
                                table1.setStyle(partsTableStyleLeftZero)
                            else:
                                table1.setStyle(partsTableStyleLeft)
                    
                            
                            table1.wrapOn(p, 30, -99999999)
                            table1.drawOn(p, 30, -99999999)
                            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
                            table1TotalRowHeight = sum(table1._rowHeights)
                            if len(projectsList) > 0:
                                tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                                table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                                table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                                tableSpace = tableSpace + 10
                            
                            #her yeni vessel için döngü-end
                            data = []
                            tableStyleControlKey = tableStyleControlKey + 1
                            previous_vessel = current_vessel
                            
                ##########try talo-end##########
                
                ##########rub talo##########
                if rubCount > 0:
                
                    data=[["RUB STATEMENT OF ACCOUNT IS AS SHOWN BELOW"]
                        ]
                    
                    previous_vessel = None
                    tableStyleControlKey = 0
                    for k in range(len(partsList)):
                        current_vessel = partsList[k]["vessel"]
                        if current_vessel != previous_vessel:
                            #her yeni vessel için döngü
                            data.append([partsList[k]["billing"]])
                            data.append(["Vessel", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"])
                            rowLengths = []
                            projectsList = []
                            balanceTotal = 0
                            for j in range(len(partsList)):
                                if partsList[j]["currency"] == "RUB" and partsList[j]["vessel"] == current_vessel:
                                    projectsList.append(partsList[j])
                                    
                                    # Para miktarını belirtilen formatta gösterme
                                    totalPriceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                                    paidPriceFixed = "{:,.2f}".format(round(partsList[j]["paidPrice"],2))
                                    balanceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"] - partsList[j]["paidPrice"],2))
                                    # Nokta ile virgülü değiştirme
                                    totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    rowLengths.append(partsList[j])
                                    
                                    serviceCardsSequency = serviceCardsSequency + 1
                                    data.append([str(partsList[j]["vesselType"]) + " " + str(partsList[j]["vessel"]), partsList[j]["request"], partsList[j]["invoiceNo"], partsList[j]["invoiceDate"], partsList[j]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[j]["currency"]])
                                    
                                    balanceTotal = balanceTotal + (partsList[j]["totalPrice"] - partsList[j]["paidPrice"])
                            
                            # Para miktarını belirtilen formatta gösterme
                            balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
                            # Nokta ile virgülü değiştirme
                            balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                            
                            data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "RUB"])
                            table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
                            if tableStyleControlKey == 0:
                                table1.setStyle(partsTableStyleLeftZero)
                            else:
                                table1.setStyle(partsTableStyleLeft)
                    
                            
                            table1.wrapOn(p, 30, -99999999)
                            table1.drawOn(p, 30, -99999999)
                            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
                            table1TotalRowHeight = sum(table1._rowHeights)
                            if len(projectsList) > 0:
                                tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                                table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                                table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                                tableSpace = tableSpace + 10
                            
                            #her yeni vessel için döngü-end
                            data = []
                            tableStyleControlKey = tableStyleControlKey + 1
                            previous_vessel = current_vessel
                            
                ##########rub talo-end##########
                
                ##########gbp talo##########
                if gbpCount > 0:
                
                    data=[["GBP STATEMENT OF ACCOUNT IS AS SHOWN BELOW"]
                        ]
                    
                    previous_vessel = None
                    tableStyleControlKey = 0
                    for k in range(len(partsList)):
                        current_vessel = partsList[k]["vessel"]
                        if current_vessel != previous_vessel:
                            #her yeni vessel için döngü
                            data.append([partsList[k]["billing"]])
                            data.append(["Vessel", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"])
                            rowLengths = []
                            projectsList = []
                            balanceTotal = 0
                            for j in range(len(partsList)):
                                if partsList[j]["currency"] == "GBP" and partsList[j]["vessel"] == current_vessel:
                                    projectsList.append(partsList[j])
                                    
                                    # Para miktarını belirtilen formatta gösterme
                                    totalPriceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
                                    paidPriceFixed = "{:,.2f}".format(round(partsList[j]["paidPrice"],2))
                                    balanceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"] - partsList[j]["paidPrice"],2))
                                    # Nokta ile virgülü değiştirme
                                    totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                                    rowLengths.append(partsList[j])
                                    
                                    serviceCardsSequency = serviceCardsSequency + 1
                                    data.append([str(partsList[j]["vesselType"]) + " " + str(partsList[j]["vessel"]), partsList[j]["request"], partsList[j]["invoiceNo"], partsList[j]["invoiceDate"], partsList[j]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[j]["currency"]])
                                    
                                    balanceTotal = balanceTotal + (partsList[j]["totalPrice"] - partsList[j]["paidPrice"])
                            
                            # Para miktarını belirtilen formatta gösterme
                            balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
                            # Nokta ile virgülü değiştirme
                            balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                            
                            data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "GBP"])
                            table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
                            if tableStyleControlKey == 0:
                                table1.setStyle(partsTableStyleLeftZero)
                            else:
                                table1.setStyle(partsTableStyleLeft)
                    
                            
                            table1.wrapOn(p, 30, -99999999)
                            table1.drawOn(p, 30, -99999999)
                            #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
                            table1TotalRowHeight = sum(table1._rowHeights)
                            if len(projectsList) > 0:
                                tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                                table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                                table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-10)
                                tableSpace = tableSpace + 10
                            
                            #her yeni vessel için döngü-end
                            data = []
                            tableStyleControlKey = tableStyleControlKey + 1
                            previous_vessel = current_vessel
                            
                ##########gbp talo-end##########
            
            
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
            if len(items) > slice:
                p.setFont('Inter', 7)
                p.drawCentredString(w/2, 10, str(pageNum) + "/" + str(pageCount))
                pageNum = pageNum + 1
            #####sayfa numarası-end#####
            
            p.showPage()

        p.save()
    except Exception as e:
        logger.exception(e)
