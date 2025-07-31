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

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import os
import pwd
import grp
import io
import shutil
from datetime import datetime
import math

from sale.models import OrderConfirmation, PurchaseOrder
from account.models import SendInvoice, IncomingInvoice, Payment
from source.models import Bank as SourceBank
from source.models import Company as SourceCompany

def financialReportPdf(request,startDate,endDate,sourceCompanyId):
    sourceCompany = SourceCompany.objects.filter(id = int(sourceCompanyId)).first()
    
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
        
    channel_layer = get_channel_layer()
    
    seq = 0
    
    async_to_sync(channel_layer.group_send)(
        'private_' + str(request),
        {
            "type": "send_percent",
            "message": seq,
            "location" : "financial_report_pdf",
            "totalCount" : 100,
            "ready" : "false"
        }
    )
    
    #standart ayar
    buffer = io.BytesIO()
    
    #dosyanın kaydedileceği konum
    folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "report", "financial_report", "documents")
    
    #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
        
    #font ayarları
    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
    pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
    
    #standart ayar
    p = canvas.Canvas(folderPath + "/financial_report_" + str(datetime.today().date().strftime('%d_%m_%Y')) + ".pdf", pagesize = A4)
    
    
    
    #standart ayar
    w, h = A4
    
    ystart = 780
    
    #tablo satır yükseklikleri
    tableRowHeight = 12
    #partsTableRowHeight = (max(descriptionLengths)/70)*20
    
    #tablo stilleri
    tableLeftStyle = TableStyle([('INNERGRID', (0,1), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
                                ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('SPAN', (0, 0), (-1, 0)),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                #('FONT', (0, 0), (-1, 1), 'Inter-Bold', 6),
                                #('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
                                ('ALIGN', (0, 0), (-1, 0), "CENTER"),
                                ('ALIGN', (0, 2), (-1, -1), "LEFT"),
                                ('ALIGN', (1, 1), (-1, -1), "RIGHT"),
                                ('TEXTCOLOR',(0,0), (-1,1), colors.white),
                                #('BACKGROUND',(0,0), (-1,0), "#009999"),
                                ('BACKGROUND',(0,0), (0,0), "#9d2235"),
                                ('BACKGROUND',(0,1), (-1,1), "#003865"),
                                #('BACKGROUND',(4,-1), (-1,-1), "rgba(0,56,101,0.40)"),
                                ('INNERGRID', (0, 1), (-1, -1), 0.25, "rgba(0,56,101,0.65)"),
                                #('BOX', (4,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('VALIGN', (0, 0), (-1, -1), "TOP")
                                ])
    tableLeft2Style = TableStyle([('INNERGRID', (0,1), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
                                ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('SPAN', (0, 0), (-1, 0)),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                #('FONT', (0, 0), (-1, 1), 'Inter-Bold', 6),
                                #('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
                                ('ALIGN', (0, 0), (-1, 0), "CENTER"),
                                ('ALIGN', (0, 2), (-1, -1), "LEFT"),
                                ('ALIGN', (1, 1), (-1, -1), "RIGHT"),
                                ('TEXTCOLOR',(0,0), (-1,1), colors.white),
                                #('BACKGROUND',(0,0), (-1,0), "#009999"),
                                #('BACKGROUND',(0,0), (0,0), "#9d2235"),
                                ('BACKGROUND',(0,1), (-1,1), "#003865"),
                                ('BACKGROUND',(0,0), (0,0), "rgba(0,56,101,0.40)"),
                                ('INNERGRID', (0, 1), (-1, -1), 0.25, "rgba(0,56,101,0.65)"),
                                #('BOX', (4,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('VALIGN', (0, 0), (-1, -1), "TOP")
                                ])
    
    tableLeftDetailStyle = TableStyle([('INNERGRID', (0,1), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
                                ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('SPAN', (0, 0), (-1, 0)),
                                ('SPAN', (0, 1), (-1, 1)),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                #('FONT', (0, 0), (-1, 1), 'Inter-Bold', 6),
                                #('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
                                ('ALIGN', (0, 0), (-1, 1), "CENTER"),
                                ('ALIGN', (0, 2), (-1, -1), "LEFT"),
                                ('ALIGN', (1, 1), (-1, -1), "RIGHT"),
                                ('TEXTCOLOR',(0,0), (-1,2), colors.white),
                                #('BACKGROUND',(0,0), (-1,0), "#009999"),
                                ('BACKGROUND',(0,0), (-1,0), "#9d2235"),
                                ('BACKGROUND',(0,2), (-1,2), "#003865"),
                                ('BACKGROUND',(0,1), (-1,1), "rgba(0,56,101,0.40)"),
                                ('INNERGRID', (0, 1), (-1, -1), 0.25, "rgba(0,56,101,0.65)"),
                                #('BOX', (4,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('VALIGN', (0, 0), (-1, -1), "TOP")
                                ])
    
    #?
    p.setLineWidth(0.5)
    
    #logo
    esmsImg = Image.open(os.path.join(os.getcwd(), "static", "images", "esms-logo2.jpg"))
    
    #####tarih#####
    if startDate == "":
        startDate = datetime.strptime("01/01/2024", "%d/%m/%Y").date()
    else:
        startDate = datetime.strptime(startDate, "%d/%m/%Y").date()
        
    if endDate == "":
        endDate = datetime.today().date()
    else:
        endDate = datetime.strptime(endDate, "%d/%m/%Y").date()
    #####tarih-end#####
    
    #başlık
    p.setFont('Inter', 18)
    p.setFillColor(HexColor("#9d2235"))
    if startDate == endDate:
        p.drawCentredString(w/2, h-100, "DAILY FINANCIAL REPORT")
    else:
        p.drawCentredString(w/2, h-100, "FINANCIAL REPORT")
    
    #yazı düzelt
    p.setFillColor(HexColor("#000"))
    p.setFont('Inter-Bold', 6)
    p.setFont('Inter', 6)
    
    #####sayfa üstü logo#####
    p.drawInlineImage(esmsImg, 30, ystart-10, width=102,height=40)
    #####sayfa üstü logo-end#####
    
    #####sağ üst yazılar#####
    p.setFont('Inter-Bold', 7)
    p.drawString(450, h-50, "DATE")
    p.setFont('Inter', 7)
    if startDate == endDate:
        p.drawString(480, h-50, ":" + str(datetime.today().date().strftime('%d.%m.%Y')))
    else:
        p.drawString(480, h-50, ":" + str(startDate.strftime('%d.%m.%Y')) + " - " + str(endDate.strftime('%d.%m.%Y')))
    
    p.setFont('Inter-Bold', 7)
    p.drawString(450, h-60, "PAGE")
    p.setFont('Inter', 7)
    p.drawString(480, h-60, ":1/2")
    #####sağ üst yazılar-end#####
    
    
    
    #####ORDER#####
    def orderProcess(data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany):
        #order confirmation
        orderConfirmationUSDTotal = 0
        orderConfirmationEURTotal = 0
        orderConfirmationTRYTotal = 0
        orderConfirmationRUBTotal = 0
        
        orderConfirmationsUSD= OrderConfirmation.objects.select_related("quotation").filter(sourceCompany = sourceCompany, quotation__currency__code = "USD", orderConfirmationDate__range=(startDate,endDate))
        orderConfirmationsEUR = OrderConfirmation.objects.select_related("quotation").filter(sourceCompany = sourceCompany, quotation__currency__code = "EUR", orderConfirmationDate__range=(startDate,endDate))
        orderConfirmationsTRY = OrderConfirmation.objects.select_related("quotation").filter(sourceCompany = sourceCompany, quotation__currency__code = "TRY", orderConfirmationDate__range=(startDate,endDate))
        orderConfirmationsRUB= OrderConfirmation.objects.select_related("quotation").filter(sourceCompany = sourceCompany, quotation__currency__code = "RUB", orderConfirmationDate__range=(startDate,endDate))
        
        for orderConfirmationUSD in orderConfirmationsUSD:
            orderConfirmationUSDTotal = orderConfirmationUSDTotal + orderConfirmationUSD.quotation.totalSellingPrice
            
        for orderConfirmationEUR in orderConfirmationsEUR:
            orderConfirmationEURTotal = orderConfirmationEURTotal + orderConfirmationEUR.quotation.totalSellingPrice
            
        for orderConfirmationTRY in orderConfirmationsTRY:
            orderConfirmationTRYTotal = orderConfirmationTRYTotal + orderConfirmationTRY.quotation.totalSellingPrice
            
        for orderConfirmationRUB in orderConfirmationsRUB:
            orderConfirmationRUBTotal = orderConfirmationRUBTotal + orderConfirmationRUB.quotation.totalSellingPrice
        
        # Para miktarını belirtilen formatta gösterme
        orderConfirmationUSDTotalFixed = "{:,.2f}".format(round(orderConfirmationUSDTotal,2))
        orderConfirmationEURTotalFixed = "{:,.2f}".format(round(orderConfirmationEURTotal,2))
        orderConfirmationTRYTotalFixed = "{:,.2f}".format(round(orderConfirmationTRYTotal,2))
        orderConfirmationRUBTotalFixed = "{:,.2f}".format(round(orderConfirmationRUBTotal,2))
        # Nokta ile virgülü değiştirme
        orderConfirmationUSDTotalFixed = orderConfirmationUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        orderConfirmationEURTotalFixed = orderConfirmationEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        orderConfirmationTRYTotalFixed = orderConfirmationTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        orderConfirmationRUBTotalFixed = orderConfirmationRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["ORDER AMOUNT", orderConfirmationUSDTotalFixed, orderConfirmationEURTotalFixed, orderConfirmationTRYTotalFixed, orderConfirmationRUBTotalFixed])
        
        #purchase order
        purchaseOrderUSDTotal = 0
        purchaseOrderEURTotal = 0
        purchaseOrderTRYTotal = 0
        purchaseOrderRUBTotal = 0
        
        purchaseOrdersUSD= PurchaseOrder.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", purchaseOrderDate__range=(startDate,endDate))
        purchaseOrdersEUR = PurchaseOrder.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", purchaseOrderDate__range=(startDate,endDate))
        purchaseOrdersTRY = PurchaseOrder.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", purchaseOrderDate__range=(startDate,endDate))
        purchaseOrdersRUB= PurchaseOrder.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", purchaseOrderDate__range=(startDate,endDate))
        
        for purchaseOrderUSD in purchaseOrdersUSD:
            purchaseOrderUSDTotal = purchaseOrderUSDTotal + purchaseOrderUSD.totalTotalPrice
            
        for purchaseOrderEUR in purchaseOrdersEUR:
            purchaseOrderEURTotal = purchaseOrderEURTotal + purchaseOrderEUR.totalTotalPrice
            
        for purchaseOrderTRY in purchaseOrdersTRY:
            purchaseOrderTRYTotal = purchaseOrderTRYTotal + purchaseOrderTRY.totalTotalPrice
            
        for purchaseOrderRUB in purchaseOrdersRUB:
            purchaseOrderRUBTotal = purchaseOrderRUBTotal + purchaseOrderRUB.totalTotalPrice
        
        # Para miktarını belirtilen formatta gösterme
        purchaseOrderUSDTotalFixed = "{:,.2f}".format(round(purchaseOrderUSDTotal,2))
        purchaseOrderEURTotalFixed = "{:,.2f}".format(round(purchaseOrderEURTotal,2))
        purchaseOrderTRYTotalFixed = "{:,.2f}".format(round(purchaseOrderTRYTotal,2))
        purchaseOrderRUBTotalFixed = "{:,.2f}".format(round(purchaseOrderRUBTotal,2))
        # Nokta ile virgülü değiştirme
        purchaseOrderUSDTotalFixed = purchaseOrderUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        purchaseOrderEURTotalFixed = purchaseOrderEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        purchaseOrderTRYTotalFixed = purchaseOrderTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        purchaseOrderRUBTotalFixed = purchaseOrderRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["PO AMOUNT", purchaseOrderUSDTotalFixed, purchaseOrderEURTotalFixed, purchaseOrderTRYTotalFixed, purchaseOrderRUBTotalFixed])
        
        #balance
        balanceUSDTotal = orderConfirmationUSDTotal - purchaseOrderUSDTotal
        balanceEURTotal = orderConfirmationEURTotal - purchaseOrderEURTotal
        balanceTRYTotal = orderConfirmationTRYTotal - purchaseOrderTRYTotal
        balanceRUBTotal = orderConfirmationRUBTotal - purchaseOrderRUBTotal
        
        # Para miktarını belirtilen formatta gösterme
        balanceUSDTotalFixed = "{:,.2f}".format(round(balanceUSDTotal,2))
        balanceEURTotalFixed = "{:,.2f}".format(round(balanceEURTotal,2))
        balanceTRYTotalFixed = "{:,.2f}".format(round(balanceTRYTotal,2))
        balanceRUBTotalFixed = "{:,.2f}".format(round(balanceRUBTotal,2))
        # Nokta ile virgülü değiştirme
        balanceUSDTotalFixed = balanceUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balanceEURTotalFixed = balanceEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balanceTRYTotalFixed = balanceTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balanceRUBTotalFixed = balanceRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["BALANCE", balanceUSDTotalFixed, balanceEURTotalFixed, balanceTRYTotalFixed, balanceRUBTotalFixed])
        
        table1 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table1.setStyle(tableStyle)
        
        table1.wrapOn(p, 30, h-200-tableRowsHeight)
        table1.drawOn(p, 30, h-200-tableRowsHeight)
    
    data=[["RECIEVED ORDERS AND DETAILS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*0)
    
    orderProcess(data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    #####ORDER-end#####
    
    #####SEND INVOICE#####
    def sendInvoiceProcess(data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany):
        #send invoice
        sendInvoiceUSDTotal = 0
        sendInvoiceEURTotal = 0
        sendInvoiceTRYTotal = 0
        sendInvoiceRUBTotal = 0
        
        sendInvoicesUSD= SendInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", group = "order", sendInvoiceDate__range=(startDate,endDate))
        sendInvoicesEUR = SendInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", group = "order", sendInvoiceDate__range=(startDate,endDate))
        sendInvoicesTRY = SendInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", group = "order", sendInvoiceDate__range=(startDate,endDate))
        sendInvoicesRUB= SendInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", group = "order", sendInvoiceDate__range=(startDate,endDate))
        
        for sendInvoiceUSD in sendInvoicesUSD:
            sendInvoiceUSDTotal = sendInvoiceUSDTotal + sendInvoiceUSD.totalPrice
            
        for sendInvoiceEUR in sendInvoicesEUR:
            sendInvoiceEURTotal = sendInvoiceEURTotal + sendInvoiceEUR.totalPrice
            
        for sendInvoiceTRY in sendInvoicesTRY:
            sendInvoiceTRYTotal = sendInvoiceTRYTotal + sendInvoiceTRY.totalPrice
            
        for sendInvoiceRUB in sendInvoicesRUB:
            sendInvoiceRUBTotal = sendInvoiceRUBTotal + sendInvoiceRUB.totalPrice
        
        # Para miktarını belirtilen formatta gösterme
        sendInvoiceUSDTotalFixed = "{:,.2f}".format(round(sendInvoiceUSDTotal,2))
        sendInvoiceEURTotalFixed = "{:,.2f}".format(round(sendInvoiceEURTotal,2))
        sendInvoiceTRYTotalFixed = "{:,.2f}".format(round(sendInvoiceTRYTotal,2))
        sendInvoiceRUBTotalFixed = "{:,.2f}".format(round(sendInvoiceRUBTotal,2))
        # Nokta ile virgülü değiştirme
        sendInvoiceUSDTotalFixed = sendInvoiceUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        sendInvoiceEURTotalFixed = sendInvoiceEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        sendInvoiceTRYTotalFixed = sendInvoiceTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        sendInvoiceRUBTotalFixed = sendInvoiceRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["AMOUNT", sendInvoiceUSDTotalFixed, sendInvoiceEURTotalFixed, sendInvoiceTRYTotalFixed, sendInvoiceRUBTotalFixed])
        
        table2 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table2.setStyle(tableStyle)
        
        table2.wrapOn(p, 30, h-200-tableRowsHeight-10)
        table2.drawOn(p, 30, h-200-tableRowsHeight-10)
        
    data=[["OUTGOING INVOICES"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*3)
    
    sendInvoiceProcess(data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    #####SEND INVOICE-end#####
    
    #####INCOMING INVOICE#####
    
    def incomingInvoiceProcess(data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany):
        #incoming invoice
        incomingInvoiceUSDTotal = 0
        incomingInvoiceEURTotal = 0
        incomingInvoiceTRYTotal = 0
        incomingInvoiceRUBTotal = 0
        
        incomingInvoicesUSD= IncomingInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", incomingInvoiceDate__range=(startDate,endDate))
        incomingInvoicesEUR = IncomingInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", incomingInvoiceDate__range=(startDate,endDate))
        incomingInvoicesTRY = IncomingInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", incomingInvoiceDate__range=(startDate,endDate))
        incomingInvoicesRUB= IncomingInvoice.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", incomingInvoiceDate__range=(startDate,endDate))
        
        for incomingInvoiceUSD in incomingInvoicesUSD:
            incomingInvoiceUSDTotal = incomingInvoiceUSDTotal + incomingInvoiceUSD.totalPrice
            
        for incomingInvoiceEUR in incomingInvoicesEUR:
            incomingInvoiceEURTotal = incomingInvoiceEURTotal + incomingInvoiceEUR.totalPrice
            
        for incomingInvoiceTRY in incomingInvoicesTRY:
            incomingInvoiceTRYTotal = incomingInvoiceTRYTotal + incomingInvoiceTRY.totalPrice
            
        for incomingInvoiceRUB in incomingInvoicesRUB:
            incomingInvoiceRUBTotal = incomingInvoiceRUBTotal + incomingInvoiceRUB.totalPrice
        
        # Para miktarını belirtilen formatta gösterme
        incomingInvoiceUSDTotalFixed = "{:,.2f}".format(round(incomingInvoiceUSDTotal,2))
        incomingInvoiceEURTotalFixed = "{:,.2f}".format(round(incomingInvoiceEURTotal,2))
        incomingInvoiceTRYTotalFixed = "{:,.2f}".format(round(incomingInvoiceTRYTotal,2))
        incomingInvoiceRUBTotalFixed = "{:,.2f}".format(round(incomingInvoiceRUBTotal,2))
        # Nokta ile virgülü değiştirme
        incomingInvoiceUSDTotalFixed = incomingInvoiceUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        incomingInvoiceEURTotalFixed = incomingInvoiceEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        incomingInvoiceTRYTotalFixed = incomingInvoiceTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        incomingInvoiceRUBTotalFixed = incomingInvoiceRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["AMOUNT", incomingInvoiceUSDTotalFixed, incomingInvoiceEURTotalFixed, incomingInvoiceTRYTotalFixed, incomingInvoiceRUBTotalFixed])
        
        table3 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table3.setStyle(tableStyle)
        
        table3.wrapOn(p, 30, h-200-tableRowsHeight-20)
        table3.drawOn(p, 30, h-200-tableRowsHeight-20)
    
    data=[["INCOMING INVOICES"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*6)
    
    incomingInvoiceProcess(data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    #####INCOMING INVOICE-end#####
    
    #####PAYMENT#####
    def paymentProcess(type, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany):
        #payment in
        paymentInUSDTotal = 0
        paymentInEURTotal = 0
        paymentInTRYTotal = 0
        paymentInRUBTotal = 0
        
        paymentInsUSD= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", type = type, paymentDate__range=(startDate,endDate))
        paymentInsEUR = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", type = type, paymentDate__range=(startDate,endDate))
        paymentInsTRY = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", type = type, paymentDate__range=(startDate,endDate))
        paymentInsRUB= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", type = type, paymentDate__range=(startDate,endDate))
        
        for paymentInUSD in paymentInsUSD:
            paymentInUSDTotal = paymentInUSDTotal + paymentInUSD.amount
            
        for paymentInEUR in paymentInsEUR:
            paymentInEURTotal = paymentInEURTotal + paymentInEUR.amount
            
        for paymentInTRY in paymentInsTRY:
            paymentInTRYTotal = paymentInTRYTotal + paymentInTRY.amount
            
        for paymentInRUB in paymentInsRUB:
            paymentInRUBTotal = paymentInRUBTotal + paymentInRUB.amount
        
        # Para miktarını belirtilen formatta gösterme
        paymentInUSDTotalFixed = "{:,.2f}".format(round(paymentInUSDTotal,2))
        paymentInEURTotalFixed = "{:,.2f}".format(round(paymentInEURTotal,2))
        paymentInTRYTotalFixed = "{:,.2f}".format(round(paymentInTRYTotal,2))
        paymentInRUBTotalFixed = "{:,.2f}".format(round(paymentInRUBTotal,2))
        # Nokta ile virgülü değiştirme
        paymentInUSDTotalFixed = paymentInUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInEURTotalFixed = paymentInEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInTRYTotalFixed = paymentInTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInRUBTotalFixed = paymentInRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["AMOUNT", paymentInUSDTotalFixed, paymentInEURTotalFixed, paymentInTRYTotalFixed, paymentInRUBTotalFixed])
        
        table4 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table4.setStyle(tableStyle)
        
        table4.wrapOn(p, 30, h-200-tableRowsHeight-30)
        table4.drawOn(p, 30, h-200-tableRowsHeight-30)
    
    #in
    data=[["INCOMING TRANSFERS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    type = "in"
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*9)
    
    paymentProcess(type, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    
    #out
    data=[["OUTGOING TRANSFERS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    type = "out"
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*12+10)
    
    paymentProcess(type, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    #####PAYMENT-end#####
    
    #####BANK ACCOUNT#####
    def bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany):
        paymentInBankUSDTotal = 0
        paymentInBankEURTotal = 0
        paymentInBankTRYTotal = 0
        paymentInBankRUBTotal = 0
        
        paymentInBanksUSD= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", type = "in", sourceBank__bankName = bankNames[0], paymentDate__range=(startDate,endDate))
        paymentInBanksEUR = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", type = "in", sourceBank__bankName = bankNames[1], paymentDate__range=(startDate,endDate))
        paymentInBanksTRY = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", type = "in", sourceBank__bankName = bankNames[2], paymentDate__range=(startDate,endDate))
        paymentInBanksRUB = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", type = "in", sourceBank__bankName = bankNames[3], paymentDate__range=(startDate,endDate))
        
        for paymentInBankUSD in paymentInBanksUSD:
            paymentInBankUSDTotal = paymentInBankUSDTotal + paymentInBankUSD.amount
            
        for paymentInBankEUR in paymentInBanksEUR:
            paymentInBankEURTotal = paymentInBankEURTotal + paymentInBankEUR.amount
            
        for paymentInBankTRY in paymentInBanksTRY:
            paymentInBankTRYTotal = paymentInBankTRYTotal + paymentInBankTRY.amount
            
        for paymentInBankRUB in paymentInBanksRUB:
            paymentInBankRUBTotal = paymentInBankRUBTotal + paymentInBankRUB.amount
        
        # Para miktarını belirtilen formatta gösterme
        paymentInBankUSDTotalFixed = "{:,.2f}".format(round(paymentInBankUSDTotal,2))
        paymentInBankEURTotalFixed = "{:,.2f}".format(round(paymentInBankEURTotal,2))
        paymentInBankTRYTotalFixed = "{:,.2f}".format(round(paymentInBankTRYTotal,2))
        paymentInBankRUBTotalFixed = "{:,.2f}".format(round(paymentInBankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        paymentInBankUSDTotalFixed = paymentInBankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInBankEURTotalFixed = paymentInBankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInBankTRYTotalFixed = paymentInBankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInBankRUBTotalFixed = paymentInBankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        paymentOutBankUSDTotal = 0
        paymentOutBankEURTotal = 0
        paymentOutBankTRYTotal = 0
        paymentOutBankRUBTotal = 0
        
        paymentOutBanksUSD= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", type = "out", sourceBank__bankName = bankNames[0], paymentDate__range=(startDate,endDate))
        paymentOutBanksEUR = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", type = "out", sourceBank__bankName = bankNames[1], paymentDate__range=(startDate,endDate))
        paymentOutBanksTRY = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", type = "out", sourceBank__bankName = bankNames[2], paymentDate__range=(startDate,endDate))
        paymentOutBanksRUB= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", type = "out", sourceBank__bankName = bankNames[3], paymentDate__range=(startDate,endDate))
        
        for paymentOutBankUSD in paymentOutBanksUSD:
            paymentOutBankUSDTotal = paymentOutBankUSDTotal + paymentOutBankUSD.amount
            
        for paymentOutBankEUR in paymentOutBanksEUR:
            paymentOutBankEURTotal = paymentOutBankEURTotal + paymentOutBankEUR.amount
            
        for paymentOutBankTRY in paymentOutBanksTRY:
            paymentOutBankTRYTotal = paymentOutBankTRYTotal + paymentOutBankTRY.amount
            
        for paymentOutBankRUB in paymentOutBanksRUB:
            paymentOutBankRUBTotal = paymentOutBankRUBTotal + paymentOutBankRUB.amount
        
        # Para miktarını belirtilen formatta gösterme
        paymentOutBankUSDTotalFixed = "{:,.2f}".format(round(paymentOutBankUSDTotal,2))
        paymentOutBankEURTotalFixed = "{:,.2f}".format(round(paymentOutBankEURTotal,2))
        paymentOutBankTRYTotalFixed = "{:,.2f}".format(round(paymentOutBankTRYTotal,2))
        paymentOutBankRUBTotalFixed = "{:,.2f}".format(round(paymentOutBankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        paymentOutBankUSDTotalFixed = paymentOutBankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentOutBankEURTotalFixed = paymentOutBankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentOutBankTRYTotalFixed = paymentOutBankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentOutBankRUBTotalFixed = paymentOutBankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #balance
        balancePaymentBankUSDTotal = paymentInBankUSDTotal - paymentOutBankUSDTotal
        balancePaymentBankEURTotal = paymentInBankEURTotal - paymentOutBankEURTotal
        balancePaymentBankTRYTotal = paymentInBankTRYTotal - paymentOutBankTRYTotal
        balancePaymentBankRUBTotal = paymentInBankRUBTotal - paymentOutBankRUBTotal
        
        # Para miktarını belirtilen formatta gösterme
        balancePaymentBankUSDTotalFixed = "{:,.2f}".format(round(balancePaymentBankUSDTotal,2))
        balancePaymentBankEURTotalFixed = "{:,.2f}".format(round(balancePaymentBankEURTotal,2))
        balancePaymentBankTRYTotalFixed = "{:,.2f}".format(round(balancePaymentBankTRYTotal,2))
        balancePaymentBankRUBTotalFixed = "{:,.2f}".format(round(balancePaymentBankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        balancePaymentBankUSDTotalFixed = balancePaymentBankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balancePaymentBankEURTotalFixed = balancePaymentBankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balancePaymentBankTRYTotalFixed = balancePaymentBankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balancePaymentBankRUBTotalFixed = balancePaymentBankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        bankUSD = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "USD", bankName = bankNames[0]).first()
        bankEUR = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "EUR", bankName = bankNames[1]).first()
        bankTRY = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "TRY", bankName = bankNames[2]).first()
        bankRUB = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "RUB", bankName = bankNames[3]).first()
        
        if bankUSD:
            bankUSDTotal = bankUSD.balance
        else:
            bankUSDTotal = 0
            
        if bankEUR:
            bankEURTotal = bankEUR.balance
        else:
            bankEURTotal = 0
            
        if bankTRY:
            bankTRYTotal = bankTRY.balance
        else:
            bankTRYTotal = 0
            
        if bankRUB:
            bankRUBTotal = bankRUB.balance
        else:
            bankRUBTotal = 0
        
        # Para miktarını belirtilen formatta gösterme
        bankUSDTotalFixed = "{:,.2f}".format(round(bankUSDTotal,2))
        bankEURTotalFixed = "{:,.2f}".format(round(bankEURTotal,2))
        bankTRYTotalFixed = "{:,.2f}".format(round(bankTRYTotal,2))
        bankRUBTotalFixed = "{:,.2f}".format(round(bankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        bankUSDTotalFixed = bankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankEURTotalFixed = bankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankTRYTotalFixed = bankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankRUBTotalFixed = bankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["TRANS. BALANCE", balancePaymentBankUSDTotalFixed, balancePaymentBankEURTotalFixed, balancePaymentBankTRYTotalFixed, balancePaymentBankRUBTotalFixed])
        data.append(["IN", paymentInBankUSDTotalFixed, paymentInBankEURTotalFixed, paymentInBankTRYTotalFixed, paymentInBankRUBTotalFixed])
        data.append(["OUT", paymentOutBankUSDTotalFixed, paymentOutBankEURTotalFixed, paymentOutBankTRYTotalFixed, paymentOutBankRUBTotalFixed])
        data.append(["BALANCE", bankUSDTotalFixed, bankEURTotalFixed, bankTRYTotalFixed, bankRUBTotalFixed])
        
        table6 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table6.setStyle(tableStyle)
        
        table6.wrapOn(p, 30, h-200-tableRowsHeight-60)
        table6.drawOn(p, 30, h-200-tableRowsHeight-60)
    
    #halkbank
    data=[["BANK ACCOUNT DETAILS"],
          ["HALKBANK - " + str(sourceCompany.name)],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["HALKBANK USD","HALKBANK EUR","HALKBANK TL","HALKBANK RUB"]
    tableStyle = tableLeftDetailStyle
    tableRowsHeight = (tableRowHeight*18)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    
    #vakıfbank
    data=[["VAKIFBANK - " + str(sourceCompany.name)],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["VAKIFBANK USD","VAKIFBANK EUR","VAKIFBANK TL","VAKIFBANK RUB"]
    tableStyle = tableLeft2Style
    tableRowsHeight = (tableRowHeight*24)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    
    #iş bankası
    data=[["TÜRKİYE İŞ BANKASI - " + str(sourceCompany.name)],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["İŞ BANKASI USD","İŞ BANKASI EUR","İŞ BANKASI TL","İŞ BANKASI RUB"]
    tableStyle = tableLeft2Style
    tableRowsHeight = (tableRowHeight*30)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    
    #albarakatürk
    data=[["ALBARAKA TÜRK - " + str(sourceCompany.name)],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["ALBARAKA TÜRK KATILIM BANKASI A.Ş.","ALBARAKA TÜRK KATILIM BANKASI A.Ş.","ALBARAKA TÜRK KATILIM BANKASI A.Ş.","ALBARAKA TÜRK KATILIM BANKASI A.Ş."]
    tableStyle = tableLeft2Style
    tableRowsHeight = (tableRowHeight*36)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    
    #emlakkatılım
    data=[["EMLAK KATILIM - " + str(sourceCompany.name)],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["TÜRKİYE EMLAK KATILIM BANKASI A.Ş.","TÜRKİYE EMLAK KATILIM BANKASI A.Ş.","TÜRKİYE EMLAK KATILIM BANKASI A.Ş.","TÜRKİYE EMLAK KATILIM BANKASI A.Ş."]
    tableStyle = tableLeft2Style
    tableRowsHeight = (tableRowHeight*42)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    
    #vakıfkatılım
    data=[["VAKIF KATILIM - " + str(sourceCompany.name)],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["VAKIF KATILIM BANKASI A.Ş.","VAKIF KATILIM BANKASI A.Ş.","VAKIF KATILIM BANKASI A.Ş.","VAKIF KATILIM BANKASI A.Ş."]
    tableStyle = tableLeft2Style
    tableRowsHeight = (tableRowHeight*48)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    
    p.showPage()
    
    #yazı düzelt
    p.setFillColor(HexColor("#000"))
    p.setFont('Inter-Bold', 6)
    p.setFont('Inter', 6)
    
    #####sayfa üstü logo#####
    p.drawInlineImage(esmsImg, 30, ystart-10, width=102,height=40)
    #####sayfa üstü logo-end#####
    
    #####sağ üst yazılar#####
    p.setFont('Inter-Bold', 7)
    p.drawString(450, h-50, "DATE")
    p.setFont('Inter', 7)
    if startDate == endDate:
        p.drawString(480, h-50, ":" + str(datetime.today().date().strftime('%d.%m.%Y')))
    else:
        p.drawString(480, h-50, ":" + str(startDate.strftime('%d.%m.%Y')) + " - " + str(endDate.strftime('%d.%m.%Y')))
    
    p.setFont('Inter-Bold', 7)
    p.drawString(450, h-60, "PAGE")
    p.setFont('Inter', 7)
    p.drawString(480, h-60, ":2/2")
    #####sağ üst yazılar-end#####
    
    #ziraatkatılım
    data=[["BANK ACCOUNT DETAILS"],
          ["ZIRAAT KATILIM - " + str(sourceCompany.name)],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["ZİRAAT KATILIM BANKASI A.Ş.","ZİRAAT KATILIM BANKASI A.Ş.","ZİRAAT KATILIM BANKASI A.Ş.","ZİRAAT KATILIM BANKASI A.Ş."]
    tableStyle = tableLeftDetailStyle
    tableRowsHeight = (tableRowHeight*0-80)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany)
    
    #total
    def bankTotalProcess(data, tableStyle, tableRowsHeight, sourceCompany):
        banksUSD = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "USD")
        banksEUR = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "EUR")
        banksTRY = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "TRY")
        banksRUB = SourceBank.objects.select_related().filter(company = sourceCompany, currency__code = "RUB")
        
        bankUSDTotal = 0
        bankEURTotal = 0
        bankTRYTotal = 0
        bankRUBTotal = 0
        
        for bankUSD in banksUSD:
            bankUSDTotal = bankUSDTotal + bankUSD.balance
        for bankEUR in banksEUR:
            bankEURTotal = bankEURTotal + bankEUR.balance
        for bankTRY in banksTRY:
            bankTRYTotal = bankTRYTotal + bankTRY.balance
        for bankRUB in banksRUB:
            bankRUBTotal = bankRUBTotal + bankRUB.balance
        
        # Para miktarını belirtilen formatta gösterme
        bankUSDTotalFixed = "{:,.2f}".format(round(bankUSDTotal,2))
        bankEURTotalFixed = "{:,.2f}".format(round(bankEURTotal,2))
        bankTRYTotalFixed = "{:,.2f}".format(round(bankTRYTotal,2))
        bankRUBTotalFixed = "{:,.2f}".format(round(bankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        bankUSDTotalFixed = bankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankEURTotalFixed = bankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankTRYTotalFixed = bankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankRUBTotalFixed = bankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

        data.append(["ESMS", bankUSDTotalFixed, bankEURTotalFixed, bankTRYTotalFixed, bankRUBTotalFixed])
        
        table7 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table7.setStyle(tableStyle)
        
        table7.wrapOn(p, 30, h-200-tableRowsHeight-20)
        table7.drawOn(p, 30, h-200-tableRowsHeight-20)
    
    data=[["BANK BALANCE TOTAL"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*7-80)
    
    bankTotalProcess(data, tableStyle, tableRowsHeight, sourceCompany)
    #####BANK ACCOUNT-end#####
    
    #####PAYMENT DAILY#####
    def paymentDailyProcess(type, data, tableStyle, tableRowsHeight, startDate, endDate, sourceCompany):
        #payment in
        paymentInUSDTotal = 0
        paymentInEURTotal = 0
        paymentInTRYTotal = 0
        paymentInRUBTotal = 0
        
        paymentInsUSD= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "USD", type = type, paymentDate__range=(startDate,endDate))
        paymentInsEUR = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "EUR", type = type, paymentDate__range=(startDate,endDate))
        paymentInsTRY = Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "TRY", type = type, paymentDate__range=(startDate,endDate))
        paymentInsRUB= Payment.objects.select_related().filter(sourceCompany = sourceCompany, currency__code = "RUB", type = type, paymentDate__range=(startDate,endDate))
        
        data.append(["USD", ""])
        for paymentInUSD in paymentInsUSD:
            paymentInUSDTotal = paymentInUSDTotal + paymentInUSD.amount
            
            processText = "A transfer has been made from " + paymentInUSD.customer.name + " to " + paymentInUSD.sourceBank.bankName + " account"
            # Para miktarını belirtilen formatta gösterme
            paymentInUSDFixed = "{:,.2f}".format(round(paymentInUSD.amount,2))
            # Nokta ile virgülü değiştirme
            paymentInUSDFixed = paymentInUSDFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            data.append([processText, paymentInUSDFixed])
        
        table4 = Table(data, colWidths=[((w-60)/100)*80 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table4.setStyle(tableStyle)
        
        table4.wrapOn(p, 30, h-200-tableRowsHeight-40)
        table4.drawOn(p, 30, h-200-tableRowsHeight-40)

        data=[]
        data.append(["EUR", ""])
        
        for paymentInEUR in paymentInsEUR:
            paymentInEURTotal = paymentInEURTotal + paymentInEUR.amount
            
            processText = "A transfer has been made from " + paymentInUSD.customer.name + " to " + paymentInUSD.sourceBank.bankName + " account"
            # Para miktarını belirtilen formatta gösterme
            paymentInUSDFixed = "{:,.2f}".format(round(paymentInUSD.amount,2))
            # Nokta ile virgülü değiştirme
            paymentInUSDFixed = paymentInUSDFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            data.append([processText, paymentInUSDFixed])
            
        table4 = Table(data, colWidths=[((w-60)/100)*80 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table4.setStyle(tableStyle)
        
        table4.wrapOn(p, 30, h-200-tableRowsHeight-40)
        table4.drawOn(p, 30, h-200-tableRowsHeight-40)
            
        for paymentInTRY in paymentInsTRY:
            paymentInTRYTotal = paymentInTRYTotal + paymentInTRY.amount
            
        for paymentInRUB in paymentInsRUB:
            paymentInRUBTotal = paymentInRUBTotal + paymentInRUB.amount

    
    #in
    data=[["DAILY INCOMING TRANSFERS"]
                ]
    type = "in"
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*10-80)
    # if startDate == endDate:
    #     paymentDailyProcess(type, data, tableStyle, tableRowsHeight, startDate, endDate)
    #####PAYMENT DAILY-end#####
    
    p.save()
    
    seq = 100
    
    async_to_sync(channel_layer.group_send)(
        'private_' + str(request),
        {
            "type": "send_percent",
            "message": seq,
            "location" : "financial_report_pdf",
            "totalCount" : 100,
            "ready" : "true"
            }
    )
    
def financialReportForMailPdf(startDate,endDate):
    channel_layer = get_channel_layer()
    
    #standart ayar
    buffer = io.BytesIO()
    
    #dosyanın kaydedileceği konum
    folderPath = os.path.join(os.getcwd(), "media", "report", "financial_report", "documents")
    
    #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
        
    #font ayarları
    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
    pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
    
    #standart ayar
    p = canvas.Canvas(folderPath + "/financial_report_" + str(datetime.today().date().strftime('%d_%m_%Y')) + ".pdf", pagesize = A4)
    
    #standart ayar
    w, h = A4
    
    ystart = 780
    
    #tablo satır yükseklikleri
    tableRowHeight = 12
    #partsTableRowHeight = (max(descriptionLengths)/70)*20
    
    #tablo stilleri
    tableLeftStyle = TableStyle([('INNERGRID', (0,1), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
                                ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('SPAN', (0, 0), (-1, 0)),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                #('FONT', (0, 0), (-1, 1), 'Inter-Bold', 6),
                                #('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
                                ('ALIGN', (0, 0), (-1, 0), "CENTER"),
                                ('ALIGN', (0, 2), (-1, -1), "LEFT"),
                                ('ALIGN', (1, 1), (-1, -1), "RIGHT"),
                                ('TEXTCOLOR',(0,0), (-1,1), colors.white),
                                #('BACKGROUND',(0,0), (-1,0), "#009999"),
                                ('BACKGROUND',(0,0), (0,0), "#9d2235"),
                                ('BACKGROUND',(0,1), (-1,1), "#003865"),
                                #('BACKGROUND',(4,-1), (-1,-1), "rgba(0,56,101,0.40)"),
                                ('INNERGRID', (0, 1), (-1, -1), 0.25, "rgba(0,56,101,0.65)"),
                                #('BOX', (4,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('VALIGN', (0, 0), (-1, -1), "TOP")
                                ])
    tableLeft2Style = TableStyle([('INNERGRID', (0,1), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
                                ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('SPAN', (0, 0), (-1, 0)),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                #('FONT', (0, 0), (-1, 1), 'Inter-Bold', 6),
                                #('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
                                ('ALIGN', (0, 0), (-1, 0), "CENTER"),
                                ('ALIGN', (0, 2), (-1, -1), "LEFT"),
                                ('ALIGN', (1, 1), (-1, -1), "RIGHT"),
                                ('TEXTCOLOR',(0,0), (-1,1), colors.white),
                                #('BACKGROUND',(0,0), (-1,0), "#009999"),
                                #('BACKGROUND',(0,0), (0,0), "#9d2235"),
                                ('BACKGROUND',(0,1), (-1,1), "#003865"),
                                ('BACKGROUND',(0,0), (0,0), "rgba(0,56,101,0.40)"),
                                ('INNERGRID', (0, 1), (-1, -1), 0.25, "rgba(0,56,101,0.65)"),
                                #('BOX', (4,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('VALIGN', (0, 0), (-1, -1), "TOP")
                                ])
    
    tableLeftDetailStyle = TableStyle([('INNERGRID', (0,1), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
                                ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
                                ('BOX', (0,0), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('SPAN', (0, 0), (-1, 0)),
                                ('SPAN', (0, 1), (-1, 1)),
                                ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                #('FONT', (0, 0), (-1, 1), 'Inter-Bold', 6),
                                #('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
                                ('ALIGN', (0, 0), (-1, 1), "CENTER"),
                                ('ALIGN', (0, 2), (-1, -1), "LEFT"),
                                ('ALIGN', (1, 1), (-1, -1), "RIGHT"),
                                ('TEXTCOLOR',(0,0), (-1,2), colors.white),
                                #('BACKGROUND',(0,0), (-1,0), "#009999"),
                                ('BACKGROUND',(0,0), (-1,0), "#9d2235"),
                                ('BACKGROUND',(0,2), (-1,2), "#003865"),
                                ('BACKGROUND',(0,1), (-1,1), "rgba(0,56,101,0.40)"),
                                ('INNERGRID', (0, 1), (-1, -1), 0.25, "rgba(0,56,101,0.65)"),
                                #('BOX', (4,-1), (-1,-1), 0.25, "rgba(0,56,101,0.65)"),
                                ('VALIGN', (0, 0), (-1, -1), "TOP")
                                ])
    
    #?
    p.setLineWidth(0.5)
    
    #logo
    esmsImg = Image.open(os.path.join(os.getcwd(), "static", "images", "esms-logo2.jpg"))
    
    #başlık
    p.setFont('Inter', 18)
    p.setFillColor(HexColor("#9d2235"))
    if startDate == endDate:
        p.drawCentredString(w/2, h-100, "DAILY FINANCIAL REPORT")
    else:
        p.drawCentredString(w/2, h-100, "FINANCIAL REPORT")
    
    #yazı düzelt
    p.setFillColor(HexColor("#000"))
    p.setFont('Inter-Bold', 6)
    p.setFont('Inter', 6)
    
    #####sayfa üstü logo#####
    p.drawInlineImage(esmsImg, 30, ystart-10, width=102,height=40)
    #####sayfa üstü logo-end#####
    
    #####sağ üst yazılar#####
    p.setFont('Inter-Bold', 7)
    p.drawString(450, h-50, "DATE")
    p.setFont('Inter', 7)
    if startDate == endDate:
        p.drawString(480, h-50, ":" + str(datetime.today().date().strftime('%d.%m.%Y')))
    else:
        p.drawString(480, h-50, ":" + str(startDate.strftime('%d.%m.%Y')) + " - " + str(endDate.strftime('%d.%m.%Y')))
    
    p.setFont('Inter-Bold', 7)
    p.drawString(450, h-60, "PAGE")
    p.setFont('Inter', 7)
    p.drawString(480, h-60, ":1/2")
    #####sağ üst yazılar-end#####
    
    
    
    #####ORDER#####
    def orderProcess(data, tableStyle, tableRowsHeight, startDate, endDate):
        #order confirmation
        orderConfirmationUSDTotal = 0
        orderConfirmationEURTotal = 0
        orderConfirmationTRYTotal = 0
        orderConfirmationRUBTotal = 0
        
        orderConfirmationsUSD= OrderConfirmation.objects.select_related("quotation").filter(quotation__currency__code = "USD", orderConfirmationDate__range=(startDate,endDate))
        orderConfirmationsEUR = OrderConfirmation.objects.select_related("quotation").filter(quotation__currency__code = "EUR", orderConfirmationDate__range=(startDate,endDate))
        orderConfirmationsTRY = OrderConfirmation.objects.select_related("quotation").filter(quotation__currency__code = "TRY", orderConfirmationDate__range=(startDate,endDate))
        orderConfirmationsRUB= OrderConfirmation.objects.select_related("quotation").filter(quotation__currency__code = "RUB", orderConfirmationDate__range=(startDate,endDate))
        
        for orderConfirmationUSD in orderConfirmationsUSD:
            orderConfirmationUSDTotal = orderConfirmationUSDTotal + orderConfirmationUSD.quotation.totalSellingPrice
            
        for orderConfirmationEUR in orderConfirmationsEUR:
            orderConfirmationEURTotal = orderConfirmationEURTotal + orderConfirmationEUR.quotation.totalSellingPrice
            
        for orderConfirmationTRY in orderConfirmationsTRY:
            orderConfirmationTRYTotal = orderConfirmationTRYTotal + orderConfirmationTRY.quotation.totalSellingPrice
            
        for orderConfirmationRUB in orderConfirmationsRUB:
            orderConfirmationRUBTotal = orderConfirmationRUBTotal + orderConfirmationRUB.quotation.totalSellingPrice
        
        # Para miktarını belirtilen formatta gösterme
        orderConfirmationUSDTotalFixed = "{:,.2f}".format(round(orderConfirmationUSDTotal,2))
        orderConfirmationEURTotalFixed = "{:,.2f}".format(round(orderConfirmationEURTotal,2))
        orderConfirmationTRYTotalFixed = "{:,.2f}".format(round(orderConfirmationTRYTotal,2))
        orderConfirmationRUBTotalFixed = "{:,.2f}".format(round(orderConfirmationRUBTotal,2))
        # Nokta ile virgülü değiştirme
        orderConfirmationUSDTotalFixed = orderConfirmationUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        orderConfirmationEURTotalFixed = orderConfirmationEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        orderConfirmationTRYTotalFixed = orderConfirmationTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        orderConfirmationRUBTotalFixed = orderConfirmationRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["ORDER AMOUNT", orderConfirmationUSDTotalFixed, orderConfirmationEURTotalFixed, orderConfirmationTRYTotalFixed, orderConfirmationRUBTotalFixed])
        
        #purchase order
        purchaseOrderUSDTotal = 0
        purchaseOrderEURTotal = 0
        purchaseOrderTRYTotal = 0
        purchaseOrderRUBTotal = 0
        
        purchaseOrdersUSD= PurchaseOrder.objects.select_related().filter(currency__code = "USD", purchaseOrderDate__range=(startDate,endDate))
        purchaseOrdersEUR = PurchaseOrder.objects.select_related().filter(currency__code = "EUR", purchaseOrderDate__range=(startDate,endDate))
        purchaseOrdersTRY = PurchaseOrder.objects.select_related().filter(currency__code = "TRY", purchaseOrderDate__range=(startDate,endDate))
        purchaseOrdersRUB= PurchaseOrder.objects.select_related().filter(currency__code = "RUB", purchaseOrderDate__range=(startDate,endDate))
        
        for purchaseOrderUSD in purchaseOrdersUSD:
            purchaseOrderUSDTotal = purchaseOrderUSDTotal + purchaseOrderUSD.totalTotalPrice
            
        for purchaseOrderEUR in purchaseOrdersEUR:
            purchaseOrderEURTotal = purchaseOrderEURTotal + purchaseOrderEUR.totalTotalPrice
            
        for purchaseOrderTRY in purchaseOrdersTRY:
            purchaseOrderTRYTotal = purchaseOrderTRYTotal + purchaseOrderTRY.totalTotalPrice
            
        for purchaseOrderRUB in purchaseOrdersRUB:
            purchaseOrderRUBTotal = purchaseOrderRUBTotal + purchaseOrderRUB.totalTotalPrice
        
        # Para miktarını belirtilen formatta gösterme
        purchaseOrderUSDTotalFixed = "{:,.2f}".format(round(purchaseOrderUSDTotal,2))
        purchaseOrderEURTotalFixed = "{:,.2f}".format(round(purchaseOrderEURTotal,2))
        purchaseOrderTRYTotalFixed = "{:,.2f}".format(round(purchaseOrderTRYTotal,2))
        purchaseOrderRUBTotalFixed = "{:,.2f}".format(round(purchaseOrderRUBTotal,2))
        # Nokta ile virgülü değiştirme
        purchaseOrderUSDTotalFixed = purchaseOrderUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        purchaseOrderEURTotalFixed = purchaseOrderEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        purchaseOrderTRYTotalFixed = purchaseOrderTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        purchaseOrderRUBTotalFixed = purchaseOrderRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["PO AMOUNT", purchaseOrderUSDTotalFixed, purchaseOrderEURTotalFixed, purchaseOrderTRYTotalFixed, purchaseOrderRUBTotalFixed])
        
        #balance
        balanceUSDTotal = orderConfirmationUSDTotal - purchaseOrderUSDTotal
        balanceEURTotal = orderConfirmationEURTotal - purchaseOrderEURTotal
        balanceTRYTotal = orderConfirmationTRYTotal - purchaseOrderTRYTotal
        balanceRUBTotal = orderConfirmationRUBTotal - purchaseOrderRUBTotal
        
        # Para miktarını belirtilen formatta gösterme
        balanceUSDTotalFixed = "{:,.2f}".format(round(balanceUSDTotal,2))
        balanceEURTotalFixed = "{:,.2f}".format(round(balanceEURTotal,2))
        balanceTRYTotalFixed = "{:,.2f}".format(round(balanceTRYTotal,2))
        balanceRUBTotalFixed = "{:,.2f}".format(round(balanceRUBTotal,2))
        # Nokta ile virgülü değiştirme
        balanceUSDTotalFixed = balanceUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balanceEURTotalFixed = balanceEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balanceTRYTotalFixed = balanceTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balanceRUBTotalFixed = balanceRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["BALANCE", balanceUSDTotalFixed, balanceEURTotalFixed, balanceTRYTotalFixed, balanceRUBTotalFixed])
        
        table1 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table1.setStyle(tableStyle)
        
        table1.wrapOn(p, 30, h-200-tableRowsHeight)
        table1.drawOn(p, 30, h-200-tableRowsHeight)
    
    data=[["RECIEVED ORDERS AND DETAILS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*0)
    
    orderProcess(data, tableStyle, tableRowsHeight, startDate, endDate)
    #####ORDER-end#####
    
    #####SEND INVOICE#####
    def sendInvoiceProcess(data, tableStyle, tableRowsHeight, startDate, endDate):
        #send invoice
        sendInvoiceUSDTotal = 0
        sendInvoiceEURTotal = 0
        sendInvoiceTRYTotal = 0
        sendInvoiceRUBTotal = 0
        
        sendInvoicesUSD= SendInvoice.objects.select_related().filter(currency__code = "USD", group = "order", sendInvoiceDate__range=(startDate,endDate))
        sendInvoicesEUR = SendInvoice.objects.select_related().filter(currency__code = "EUR", group = "order", sendInvoiceDate__range=(startDate,endDate))
        sendInvoicesTRY = SendInvoice.objects.select_related().filter(currency__code = "TRY", group = "order", sendInvoiceDate__range=(startDate,endDate))
        sendInvoicesRUB= SendInvoice.objects.select_related().filter(currency__code = "RUB", group = "order", sendInvoiceDate__range=(startDate,endDate))
        
        for sendInvoiceUSD in sendInvoicesUSD:
            sendInvoiceUSDTotal = sendInvoiceUSDTotal + sendInvoiceUSD.totalPrice
            
        for sendInvoiceEUR in sendInvoicesEUR:
            sendInvoiceEURTotal = sendInvoiceEURTotal + sendInvoiceEUR.totalPrice
            
        for sendInvoiceTRY in sendInvoicesTRY:
            sendInvoiceTRYTotal = sendInvoiceTRYTotal + sendInvoiceTRY.totalPrice
            
        for sendInvoiceRUB in sendInvoicesRUB:
            sendInvoiceRUBTotal = sendInvoiceRUBTotal + sendInvoiceRUB.totalPrice
        
        # Para miktarını belirtilen formatta gösterme
        sendInvoiceUSDTotalFixed = "{:,.2f}".format(round(sendInvoiceUSDTotal,2))
        sendInvoiceEURTotalFixed = "{:,.2f}".format(round(sendInvoiceEURTotal,2))
        sendInvoiceTRYTotalFixed = "{:,.2f}".format(round(sendInvoiceTRYTotal,2))
        sendInvoiceRUBTotalFixed = "{:,.2f}".format(round(sendInvoiceRUBTotal,2))
        # Nokta ile virgülü değiştirme
        sendInvoiceUSDTotalFixed = sendInvoiceUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        sendInvoiceEURTotalFixed = sendInvoiceEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        sendInvoiceTRYTotalFixed = sendInvoiceTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        sendInvoiceRUBTotalFixed = sendInvoiceRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["AMOUNT", sendInvoiceUSDTotalFixed, sendInvoiceEURTotalFixed, sendInvoiceTRYTotalFixed, sendInvoiceRUBTotalFixed])
        
        table2 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table2.setStyle(tableStyle)
        
        table2.wrapOn(p, 30, h-200-tableRowsHeight-10)
        table2.drawOn(p, 30, h-200-tableRowsHeight-10)
        
    data=[["OUTGOING INVOICES"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*3)
    
    sendInvoiceProcess(data, tableStyle, tableRowsHeight, startDate, endDate)
    #####SEND INVOICE-end#####
    
    #####INCOMING INVOICE#####
    
    def incomingInvoiceProcess(data, tableStyle, tableRowsHeight, startDate, endDate):
        #incoming invoice
        incomingInvoiceUSDTotal = 0
        incomingInvoiceEURTotal = 0
        incomingInvoiceTRYTotal = 0
        incomingInvoiceRUBTotal = 0
        
        incomingInvoicesUSD= IncomingInvoice.objects.select_related().filter(currency__code = "USD", incomingInvoiceDate__range=(startDate,endDate))
        incomingInvoicesEUR = IncomingInvoice.objects.select_related().filter(currency__code = "EUR", incomingInvoiceDate__range=(startDate,endDate))
        incomingInvoicesTRY = IncomingInvoice.objects.select_related().filter(currency__code = "TRY", incomingInvoiceDate__range=(startDate,endDate))
        incomingInvoicesRUB= IncomingInvoice.objects.select_related().filter(currency__code = "RUB", incomingInvoiceDate__range=(startDate,endDate))
        
        for incomingInvoiceUSD in incomingInvoicesUSD:
            incomingInvoiceUSDTotal = incomingInvoiceUSDTotal + incomingInvoiceUSD.totalPrice
            
        for incomingInvoiceEUR in incomingInvoicesEUR:
            incomingInvoiceEURTotal = incomingInvoiceEURTotal + incomingInvoiceEUR.totalPrice
            
        for incomingInvoiceTRY in incomingInvoicesTRY:
            incomingInvoiceTRYTotal = incomingInvoiceTRYTotal + incomingInvoiceTRY.totalPrice
            
        for incomingInvoiceRUB in incomingInvoicesRUB:
            incomingInvoiceRUBTotal = incomingInvoiceRUBTotal + incomingInvoiceRUB.totalPrice
        
        # Para miktarını belirtilen formatta gösterme
        incomingInvoiceUSDTotalFixed = "{:,.2f}".format(round(incomingInvoiceUSDTotal,2))
        incomingInvoiceEURTotalFixed = "{:,.2f}".format(round(incomingInvoiceEURTotal,2))
        incomingInvoiceTRYTotalFixed = "{:,.2f}".format(round(incomingInvoiceTRYTotal,2))
        incomingInvoiceRUBTotalFixed = "{:,.2f}".format(round(incomingInvoiceRUBTotal,2))
        # Nokta ile virgülü değiştirme
        incomingInvoiceUSDTotalFixed = incomingInvoiceUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        incomingInvoiceEURTotalFixed = incomingInvoiceEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        incomingInvoiceTRYTotalFixed = incomingInvoiceTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        incomingInvoiceRUBTotalFixed = incomingInvoiceRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["AMOUNT", incomingInvoiceUSDTotalFixed, incomingInvoiceEURTotalFixed, incomingInvoiceTRYTotalFixed, incomingInvoiceRUBTotalFixed])
        
        table3 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table3.setStyle(tableStyle)
        
        table3.wrapOn(p, 30, h-200-tableRowsHeight-20)
        table3.drawOn(p, 30, h-200-tableRowsHeight-20)
    
    data=[["INCOMING INVOICES"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*6)
    
    incomingInvoiceProcess(data, tableStyle, tableRowsHeight, startDate, endDate)
    #####INCOMING INVOICE-end#####
    
    #####PAYMENT#####
    def paymentProcess(type, data, tableStyle, tableRowsHeight, startDate, endDate):
        #payment in
        paymentInUSDTotal = 0
        paymentInEURTotal = 0
        paymentInTRYTotal = 0
        paymentInRUBTotal = 0
        
        paymentInsUSD= Payment.objects.select_related().filter(currency__code = "USD", type = type, paymentDate__range=(startDate,endDate))
        paymentInsEUR = Payment.objects.select_related().filter(currency__code = "EUR", type = type, paymentDate__range=(startDate,endDate))
        paymentInsTRY = Payment.objects.select_related().filter(currency__code = "TRY", type = type, paymentDate__range=(startDate,endDate))
        paymentInsRUB= Payment.objects.select_related().filter(currency__code = "RUB", type = type, paymentDate__range=(startDate,endDate))
        
        for paymentInUSD in paymentInsUSD:
            paymentInUSDTotal = paymentInUSDTotal + paymentInUSD.amount
            
        for paymentInEUR in paymentInsEUR:
            paymentInEURTotal = paymentInEURTotal + paymentInEUR.amount
            
        for paymentInTRY in paymentInsTRY:
            paymentInTRYTotal = paymentInTRYTotal + paymentInTRY.amount
            
        for paymentInRUB in paymentInsRUB:
            paymentInRUBTotal = paymentInRUBTotal + paymentInRUB.amount
        
        # Para miktarını belirtilen formatta gösterme
        paymentInUSDTotalFixed = "{:,.2f}".format(round(paymentInUSDTotal,2))
        paymentInEURTotalFixed = "{:,.2f}".format(round(paymentInEURTotal,2))
        paymentInTRYTotalFixed = "{:,.2f}".format(round(paymentInTRYTotal,2))
        paymentInRUBTotalFixed = "{:,.2f}".format(round(paymentInRUBTotal,2))
        # Nokta ile virgülü değiştirme
        paymentInUSDTotalFixed = paymentInUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInEURTotalFixed = paymentInEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInTRYTotalFixed = paymentInTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInRUBTotalFixed = paymentInRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["AMOUNT", paymentInUSDTotalFixed, paymentInEURTotalFixed, paymentInTRYTotalFixed, paymentInRUBTotalFixed])
        
        table4 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table4.setStyle(tableStyle)
        
        table4.wrapOn(p, 30, h-200-tableRowsHeight-30)
        table4.drawOn(p, 30, h-200-tableRowsHeight-30)
    
    #in
    data=[["INCOMING TRANSFERS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    type = "in"
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*9)
    
    paymentProcess(type, data, tableStyle, tableRowsHeight, startDate, endDate)
    
    #out
    data=[["OUTGOING TRANSFERS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    type = "out"
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*12+10)
    
    paymentProcess(type, data, tableStyle, tableRowsHeight, startDate, endDate)
    #####PAYMENT-end#####
    
    #####BANK ACCOUNT#####
    def bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate):
        paymentInBankUSDTotal = 0
        paymentInBankEURTotal = 0
        paymentInBankTRYTotal = 0
        paymentInBankRUBTotal = 0
        
        paymentInBanksUSD= Payment.objects.select_related().filter(currency__code = "USD", type = "in", sourceBank__bankName = bankNames[0], paymentDate__range=(startDate,endDate))
        paymentInBanksEUR = Payment.objects.select_related().filter(currency__code = "EUR", type = "in", sourceBank__bankName = bankNames[1], paymentDate__range=(startDate,endDate))
        paymentInBanksTRY = Payment.objects.select_related().filter(currency__code = "TRY", type = "in", sourceBank__bankName = bankNames[2], paymentDate__range=(startDate,endDate))
        paymentInBanksRUB = Payment.objects.select_related().filter(currency__code = "RUB", type = "in", sourceBank__bankName = bankNames[3], paymentDate__range=(startDate,endDate))
        
        for paymentInBankUSD in paymentInBanksUSD:
            paymentInBankUSDTotal = paymentInBankUSDTotal + paymentInBankUSD.amount
            
        for paymentInBankEUR in paymentInBanksEUR:
            paymentInBankEURTotal = paymentInBankEURTotal + paymentInBankEUR.amount
            
        for paymentInBankTRY in paymentInBanksTRY:
            paymentInBankTRYTotal = paymentInBankTRYTotal + paymentInBankTRY.amount
            
        for paymentInBankRUB in paymentInBanksRUB:
            paymentInBankRUBTotal = paymentInBankRUBTotal + paymentInBankRUB.amount
        
        # Para miktarını belirtilen formatta gösterme
        paymentInBankUSDTotalFixed = "{:,.2f}".format(round(paymentInBankUSDTotal,2))
        paymentInBankEURTotalFixed = "{:,.2f}".format(round(paymentInBankEURTotal,2))
        paymentInBankTRYTotalFixed = "{:,.2f}".format(round(paymentInBankTRYTotal,2))
        paymentInBankRUBTotalFixed = "{:,.2f}".format(round(paymentInBankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        paymentInBankUSDTotalFixed = paymentInBankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInBankEURTotalFixed = paymentInBankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInBankTRYTotalFixed = paymentInBankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentInBankRUBTotalFixed = paymentInBankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        paymentOutBankUSDTotal = 0
        paymentOutBankEURTotal = 0
        paymentOutBankTRYTotal = 0
        paymentOutBankRUBTotal = 0
        
        paymentOutBanksUSD= Payment.objects.select_related().filter(currency__code = "USD", type = "out", sourceBank__bankName = bankNames[0], paymentDate__range=(startDate,endDate))
        paymentOutBanksEUR = Payment.objects.select_related().filter(currency__code = "EUR", type = "out", sourceBank__bankName = bankNames[1], paymentDate__range=(startDate,endDate))
        paymentOutBanksTRY = Payment.objects.select_related().filter(currency__code = "TRY", type = "out", sourceBank__bankName = bankNames[2], paymentDate__range=(startDate,endDate))
        paymentOutBanksRUB= Payment.objects.select_related().filter(currency__code = "RUB", type = "out", sourceBank__bankName = bankNames[3], paymentDate__range=(startDate,endDate))
        
        for paymentOutBankUSD in paymentOutBanksUSD:
            paymentOutBankUSDTotal = paymentOutBankUSDTotal + paymentOutBankUSD.amount
            
        for paymentOutBankEUR in paymentOutBanksEUR:
            paymentOutBankEURTotal = paymentOutBankEURTotal + paymentOutBankEUR.amount
            
        for paymentOutBankTRY in paymentOutBanksTRY:
            paymentOutBankTRYTotal = paymentOutBankTRYTotal + paymentOutBankTRY.amount
            
        for paymentOutBankRUB in paymentOutBanksRUB:
            paymentOutBankRUBTotal = paymentOutBankRUBTotal + paymentOutBankRUB.amount
        
        # Para miktarını belirtilen formatta gösterme
        paymentOutBankUSDTotalFixed = "{:,.2f}".format(round(paymentOutBankUSDTotal,2))
        paymentOutBankEURTotalFixed = "{:,.2f}".format(round(paymentOutBankEURTotal,2))
        paymentOutBankTRYTotalFixed = "{:,.2f}".format(round(paymentOutBankTRYTotal,2))
        paymentOutBankRUBTotalFixed = "{:,.2f}".format(round(paymentOutBankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        paymentOutBankUSDTotalFixed = paymentOutBankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentOutBankEURTotalFixed = paymentOutBankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentOutBankTRYTotalFixed = paymentOutBankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        paymentOutBankRUBTotalFixed = paymentOutBankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #balance
        balancePaymentBankUSDTotal = paymentInBankUSDTotal - paymentOutBankUSDTotal
        balancePaymentBankEURTotal = paymentInBankEURTotal - paymentOutBankEURTotal
        balancePaymentBankTRYTotal = paymentInBankTRYTotal - paymentOutBankTRYTotal
        balancePaymentBankRUBTotal = paymentInBankRUBTotal - paymentOutBankRUBTotal
        
        # Para miktarını belirtilen formatta gösterme
        balancePaymentBankUSDTotalFixed = "{:,.2f}".format(round(balancePaymentBankUSDTotal,2))
        balancePaymentBankEURTotalFixed = "{:,.2f}".format(round(balancePaymentBankEURTotal,2))
        balancePaymentBankTRYTotalFixed = "{:,.2f}".format(round(balancePaymentBankTRYTotal,2))
        balancePaymentBankRUBTotalFixed = "{:,.2f}".format(round(balancePaymentBankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        balancePaymentBankUSDTotalFixed = balancePaymentBankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balancePaymentBankEURTotalFixed = balancePaymentBankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balancePaymentBankTRYTotalFixed = balancePaymentBankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        balancePaymentBankRUBTotalFixed = balancePaymentBankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        bankUSD = SourceBank.objects.select_related().filter(currency__code = "USD", bankName = bankNames[0]).first()
        bankEUR = SourceBank.objects.select_related().filter(currency__code = "EUR", bankName = bankNames[1]).first()
        bankTRY = SourceBank.objects.select_related().filter(currency__code = "TRY", bankName = bankNames[2]).first()
        bankRUB = SourceBank.objects.select_related().filter(currency__code = "RUB", bankName = bankNames[3]).first()
        
        if bankUSD:
            bankUSDTotal = bankUSD.balance
        else:
            bankUSDTotal = 0
            
        if bankEUR:
            bankEURTotal = bankEUR.balance
        else:
            bankEURTotal = 0
            
        if bankTRY:
            bankTRYTotal = bankTRY.balance
        else:
            bankTRYTotal = 0
            
        if bankRUB:
            bankRUBTotal = bankRUB.balance
        else:
            bankRUBTotal = 0
        
        # Para miktarını belirtilen formatta gösterme
        bankUSDTotalFixed = "{:,.2f}".format(round(bankUSDTotal,2))
        bankEURTotalFixed = "{:,.2f}".format(round(bankEURTotal,2))
        bankTRYTotalFixed = "{:,.2f}".format(round(bankTRYTotal,2))
        bankRUBTotalFixed = "{:,.2f}".format(round(bankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        bankUSDTotalFixed = bankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankEURTotalFixed = bankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankTRYTotalFixed = bankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankRUBTotalFixed = bankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        data.append(["TRANS. BALANCE", balancePaymentBankUSDTotalFixed, balancePaymentBankEURTotalFixed, balancePaymentBankTRYTotalFixed, balancePaymentBankRUBTotalFixed])
        data.append(["IN", paymentInBankUSDTotalFixed, paymentInBankEURTotalFixed, paymentInBankTRYTotalFixed, paymentInBankRUBTotalFixed])
        data.append(["OUT", paymentOutBankUSDTotalFixed, paymentOutBankEURTotalFixed, paymentOutBankTRYTotalFixed, paymentOutBankRUBTotalFixed])
        data.append(["BALANCE", bankUSDTotalFixed, bankEURTotalFixed, bankTRYTotalFixed, bankRUBTotalFixed])
        
        table6 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table6.setStyle(tableStyle)
        
        table6.wrapOn(p, 30, h-200-tableRowsHeight-60)
        table6.drawOn(p, 30, h-200-tableRowsHeight-60)
    
    #halkbank
    data=[["BANK ACCOUNT DETAILS"],
          ["HALKBANK - ESMS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["HALKBANK USD","HALKBANK EUR","HALKBANK TL","HALKBANK RUB"]
    tableStyle = tableLeftDetailStyle
    tableRowsHeight = (tableRowHeight*18)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate)
    
    #vakıfbank
    data=[["VAKIFBANK - ESMS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["VAKIFBANK USD","VAKIFBANK EUR","VAKIFBANK TL","VAKIFBANK RUB"]
    tableStyle = tableLeft2Style
    tableRowsHeight = (tableRowHeight*24)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate)
    
    #iş bankası
    data=[["TÜRKİYE İŞ BANKASI - ESMS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["İŞ BANKASI USD","İŞ BANKASI EUR","İŞ BANKASI TL","İŞ BANKASI RUB"]
    tableStyle = tableLeft2Style
    tableRowsHeight = (tableRowHeight*30)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate)
    
    #albarakatürk
    data=[["ALBARAKA TÜRK - ESMS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["ALBARAKA TÜRK KATILIM BANKASI A.Ş.","ALBARAKA TÜRK KATILIM BANKASI A.Ş.","ALBARAKA TÜRK KATILIM BANKASI A.Ş.","ALBARAKA TÜRK KATILIM BANKASI A.Ş."]
    tableStyle = tableLeft2Style
    tableRowsHeight = (tableRowHeight*36)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate)
    
    #emlakkatılım
    data=[["EMLAK KATILIM - ESMS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["TÜRKİYE EMLAK KATILIM BANKASI A.Ş.","TÜRKİYE EMLAK KATILIM BANKASI A.Ş.","TÜRKİYE EMLAK KATILIM BANKASI A.Ş.","TÜRKİYE EMLAK KATILIM BANKASI A.Ş."]
    tableStyle = tableLeft2Style
    tableRowsHeight = (tableRowHeight*42)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate)
    
    #vakıfkatılım
    data=[["VAKIF KATILIM - ESMS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["VAKIF KATILIM BANKASI A.Ş.","VAKIF KATILIM BANKASI A.Ş.","VAKIF KATILIM BANKASI A.Ş.","VAKIF KATILIM BANKASI A.Ş."]
    tableStyle = tableLeft2Style
    tableRowsHeight = (tableRowHeight*48)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate)
    
    p.showPage()
    
    #yazı düzelt
    p.setFillColor(HexColor("#000"))
    p.setFont('Inter-Bold', 6)
    p.setFont('Inter', 6)
    
    #####sayfa üstü logo#####
    p.drawInlineImage(esmsImg, 30, ystart-10, width=102,height=40)
    #####sayfa üstü logo-end#####
    
    #####sağ üst yazılar#####
    p.setFont('Inter-Bold', 7)
    p.drawString(450, h-50, "DATE")
    p.setFont('Inter', 7)
    if startDate == endDate:
        p.drawString(480, h-50, ":" + str(datetime.today().date().strftime('%d.%m.%Y')))
    else:
        p.drawString(480, h-50, ":" + str(startDate.strftime('%d.%m.%Y')) + " - " + str(endDate.strftime('%d.%m.%Y')))
    
    p.setFont('Inter-Bold', 7)
    p.drawString(450, h-60, "PAGE")
    p.setFont('Inter', 7)
    p.drawString(480, h-60, ":2/2")
    #####sağ üst yazılar-end#####
    
    #ziraatkatılım
    data=[["BANK ACCOUNT DETAILS"],
          ["ZIRAAT KATILIM - ESMS"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    
    bankNames = ["ZİRAAT KATILIM BANKASI A.Ş.","ZİRAAT KATILIM BANKASI A.Ş.","ZİRAAT KATILIM BANKASI A.Ş.","ZİRAAT KATILIM BANKASI A.Ş."]
    tableStyle = tableLeftDetailStyle
    tableRowsHeight = (tableRowHeight*0-80)
    
    bankProcess(bankNames, data, tableStyle, tableRowsHeight, startDate, endDate)
    
    #total
    def bankTotalProcess(data, tableStyle, tableRowsHeight):
        banksUSD = SourceBank.objects.select_related().filter(currency__code = "USD")
        banksEUR = SourceBank.objects.select_related().filter(currency__code = "EUR")
        banksTRY = SourceBank.objects.select_related().filter(currency__code = "TRY")
        banksRUB = SourceBank.objects.select_related().filter(currency__code = "RUB")
        
        bankUSDTotal = 0
        bankEURTotal = 0
        bankTRYTotal = 0
        bankRUBTotal = 0
        
        for bankUSD in banksUSD:
            bankUSDTotal = bankUSDTotal + bankUSD.balance
        for bankEUR in banksEUR:
            bankEURTotal = bankEURTotal + bankEUR.balance
        for bankTRY in banksTRY:
            bankTRYTotal = bankTRYTotal + bankTRY.balance
        for bankRUB in banksRUB:
            bankRUBTotal = bankRUBTotal + bankRUB.balance
        
        # Para miktarını belirtilen formatta gösterme
        bankUSDTotalFixed = "{:,.2f}".format(round(bankUSDTotal,2))
        bankEURTotalFixed = "{:,.2f}".format(round(bankEURTotal,2))
        bankTRYTotalFixed = "{:,.2f}".format(round(bankTRYTotal,2))
        bankRUBTotalFixed = "{:,.2f}".format(round(bankRUBTotal,2))
        # Nokta ile virgülü değiştirme
        bankUSDTotalFixed = bankUSDTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankEURTotalFixed = bankEURTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankTRYTotalFixed = bankTRYTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        bankRUBTotalFixed = bankRUBTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')

        data.append(["ESMS", bankUSDTotalFixed, bankEURTotalFixed, bankTRYTotalFixed, bankRUBTotalFixed])
        
        table7 = Table(data, colWidths=[((w-60)/100)*20 , ((w-60)/100)*20, ((w-60)/100)*20 , ((w-60)/100)*20 , ((w-60)/100)*20], rowHeights=tableRowHeight)
        table7.setStyle(tableStyle)
        
        table7.wrapOn(p, 30, h-200-tableRowsHeight-20)
        table7.drawOn(p, 30, h-200-tableRowsHeight-20)
    
    data=[["BANK BALANCE TOTAL"],
          ["", "USD", "EUR", "TRY", "RUB"]
                ]
    tableStyle = tableLeftStyle
    tableRowsHeight = (tableRowHeight*7-80)
    
    bankTotalProcess(data, tableStyle, tableRowsHeight)
    #####BANK ACCOUNT-end#####
    
    
    
    p.save()
