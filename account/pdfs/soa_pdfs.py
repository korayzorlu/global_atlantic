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

from ..utils.account_utils import round_price

def soaPdf(companyId, sourceCompanyId):
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
            
        company = Company.objects.filter(id = companyId).first()
        sendInvoices = SendInvoice.objects.filter(customer = company, payed = False).order_by("id").annotate(num_vessels=Count('vessel')).order_by('-num_vessels', 'vessel')
        if sendInvoices:
            items = []
        else:
            items = [{"vesselType":"",
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
        
        for sendInvoice in sendInvoices:
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
                
            items.append({"vesselType":vesselType,
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
                
        currencyList = list(set(currencyList))
        logger.info(currencyList)
        if len(currencyList) > 1:
            extraLineHeight = 14 * (len(currencyList) - 1)
            
        #standart ayar
        buffer = io.BytesIO()
        
        #dosyanın kaydedileceği konum
        folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "account", "soa", "documents")
        
        #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        
        #font ayarları
        rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
        pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
        
        #standart ayar
        p = canvas.Canvas(folderPath + "/" + str(company.id) + ".pdf", pagesize = A4)
        
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
        
        #####sol üst tablo#####
        #company
        p.setFillColor(HexColor("#000"))
        p.setFont('Inter-Bold', 6)
        p.drawString(35, h-100, "COMPANY : ")
        p.setFont('Inter', 6)
        
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        newCompanyName = ""
        for i in range(0, len(company.name), 65):
            chunk = company.name[i:i+65]
            if len(chunk) < 65:
                newCompanyName += chunk
            else:
                space_index = chunk.rfind('')
                if space_index != -1:
                    newCompanyName += chunk[:space_index] + '\n'
                    if space_index + 1 < len(chunk):
                        newCompanyName += chunk[space_index+1:]
                else:
                    newCompanyName += chunk
        #alt satır komutu
        lines = newCompanyName.replace("\r\n", "\n")
        lines = lines.split('\n')
        line_height = 10  # İsteğe bağlı, satır yüksekliği
        current_y = h-100

        for line in lines:
            p.drawString(80, current_y, line)
            current_y = current_y - line_height
        #####company with multiple lines-end#####
        
        #####address with multiple lines#####
        #alt satır komutu
        # lines = company.address.replace("\r\n", "\n")
        # lines = lines.split('\n')
        # line_height = 8  # İsteğe bağlı, satır yüksekliği
        # current_y = current_y

        # for line in lines:
        #     p.drawString(35, current_y, line)
        #     current_y = current_y - line_height
        #####address with multiple lines-end#####

        
        p.setFont('Inter', 6)
        data=[("")]
        table = Table(data, colWidths=w/2-35, rowHeights=(tableRowHeight*2)+extraLineHeight)
        table.setStyle(TableStyle([
                                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                                ]))
        
        table.wrapOn(p, 30, h-115-extraLineHeight)
        table.drawOn(p, 30, h-115-extraLineHeight)
        #####sol üst tablo-end#####
        
        #####sağ üst tablo1#####
        if company.creditPeriod > 0:
            periodType = "DAYS"
        else:
            periodType = "DAY"
        # Para miktarını belirtilen formatta gösterme
        totalCredit = Decimal(str(company.creditLimit))
        creditLimitFixed = "{:,.2f}".format(round(totalCredit,2))
        # Nokta ile virgülü değiştirme
        creditLimitFixed = creditLimitFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        if company.currency:
            currency = company.currency.code
        else:
            currency = ""
        data=[["CREDIT LIMIT", str(creditLimitFixed) + " " + str(currency)],
            ["CREDIT PERIOD", str(company.creditPeriod) + " " + periodType]
            ]
        table = Table(data, colWidths=[((w/2-35)/2/2)-(5/2),((w/2-35)/2/2)-(5/2)], rowHeights=tableRowHeight+(extraLineHeight/2))
        table.setStyle(tableLeftStyleAmount)
        
        table.wrapOn(p, w/2+5, h-115-extraLineHeight)
        table.drawOn(p, w/2+5, h-115-extraLineHeight)
        #####sağ üst tablo1-end#####
        
        #####sağ üst tablo2#####
        totalAmountText = ""
        totalDueAmountText = ""
        for key, currency in enumerate(currencyList):
            sendInvoicess = SendInvoice.objects.filter(customer = company, currency__code = currency)
            
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
            
            ##########usd talo##########
            
            # data.append(["Vessel", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Currency"])
            # rowLengths = []
            # projectsList = []
            # for j in range(len(partsList)):
            #     if partsList[j]["currency"] == "USD":
            #         projectsList.append(partsList[j])
                    
            #         # Para miktarını belirtilen formatta gösterme
            #         totalPriceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
            #         paidPriceFixed = "{:,.2f}".format(round(partsList[j]["paidPrice"],2))
            #         balanceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"] - partsList[j]["paidPrice"],2))
            #         # Nokta ile virgülü değiştirme
            #         totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            #         paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            #         balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            #         rowLengths.append(partsList[j])
                    
            #         serviceCardsSequency = serviceCardsSequency + 1
            #         data.append([partsList[j]["vessel"], partsList[j]["request"], partsList[j]["invoiceNo"], partsList[j]["invoiceDate"], partsList[j]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[j]["currency"]])
                    
            #         balanceTotal = balanceTotal + partsList[j]["totalPrice"]
            
            # # Para miktarını belirtilen formatta gösterme
            # balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
            # # Nokta ile virgülü değiştirme
            # balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            # data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "USD"])
            # table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*15, ((w-60)/100)*12 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
            # table1.setStyle(partsTableStyleLeft)
            
            if usdCount > 0:
            
                data=[["YOUR 'USD' STATEMENT OF ACCOUNT IS AS SHOWN BELOW"]
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
                            table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight)
                            table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight)
                            tableSpace = tableSpace + 10
                        
                        #her yeni vessel için döngü-end
                        data = []
                        tableStyleControlKey = tableStyleControlKey + 1
                        previous_vessel = current_vessel
                        
            ##########usd talo-end##########
            
            ##########eur talo##########
            if eurCount > 0:
            
                data=[["YOUR 'EUR' STATEMENT OF ACCOUNT IS AS SHOWN BELOW"]
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
                            table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                            table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                            tableSpace = tableSpace + 10
                        
                        #her yeni vessel için döngü-end
                        data = []
                        tableStyleControlKey = tableStyleControlKey + 1
                        previous_vessel = current_vessel
                        
            ##########eur talo-end##########
            
            ##########try talo##########
            if tryCount > 0:
            
                data=[["YOUR 'TRY' STATEMENT OF ACCOUNT IS AS SHOWN BELOW"]
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
                            table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                            table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                            tableSpace = tableSpace + 10
                        
                        #her yeni vessel için döngü-end
                        data = []
                        tableStyleControlKey = tableStyleControlKey + 1
                        previous_vessel = current_vessel
                        
            ##########try talo-end##########
            
            ##########rub talo##########
            if rubCount > 0:
            
                data=[["YOUR 'RUB' STATEMENT OF ACCOUNT IS AS SHOWN BELOW"]
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
                            table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                            table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                            tableSpace = tableSpace + 10
                        
                        #her yeni vessel için döngü-end
                        data = []
                        tableStyleControlKey = tableStyleControlKey + 1
                        previous_vessel = current_vessel
                        
            ##########rub talo-end##########
            
            ##########gbp talo##########
            if gbpCount > 0:
            
                data=[["YOUR 'GBP' STATEMENT OF ACCOUNT IS AS SHOWN BELOW"]
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
                            table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                            table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                            tableSpace = tableSpace + 10
                        
                        #her yeni vessel için döngü-end
                        data = []
                        tableStyleControlKey = tableStyleControlKey + 1
                        previous_vessel = current_vessel
                        
            ##########gbp talo-end##########
            
            #####over credit alanı#####
            if company.credit > 0:
                tableTotalRowHeightt = tableTotalRowHeight if tableTotalRowHeight else 0
                p.setFillColor(HexColor("#000"))
                p.setFont('Inter', 6)
                p.drawString(30, th-125-tableTotalRowHeightt-extraLineHeight-15, f"Note: This reflects an overpayment of {round_price(company.credit)} {company.currency.code} or unapplied payments.")
            #####over credit alanı-end#####

            ######sayfa altı########
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

def soaIncomingPdf(companyId, sourceCompanyId):
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
            
        company = Company.objects.filter(id = companyId).first()
        incomingInvoices = IncomingInvoice.objects.filter(seller = company, payed = False).order_by('incomingInvoiceDate')
        if incomingInvoices:
            items = []
        else:
            items = [{"purchaseOrder":"",
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
        for incomingInvoice in incomingInvoices:
            if incomingInvoice.purchaseOrder:
                purchaseOrder = incomingInvoice.purchaseOrder.purchaseOrderNo
            else:
                purchaseOrder = ""
            if incomingInvoice.theRequest:
                project = incomingInvoice.theRequest.requestNo
            else:
                project = ""
                
            items.append({"purchaseOrder":purchaseOrder,
                        "request":project,
                        "invoiceNo":incomingInvoice.incomingInvoiceNo,
                        "invoiceDate":incomingInvoice.incomingInvoiceDate.strftime("%d.%m.%Y"),
                        "dueDate":incomingInvoice.paymentDate.strftime("%d.%m.%Y"),
                        "totalPrice":incomingInvoice.totalPrice,
                        "paidPrice":incomingInvoice.paidPrice,
                        "balance":"",
                        "currency":incomingInvoice.currency.code
            })
            if incomingInvoice.currency.code == "USD":
                usdCount = usdCount + 1
                currencyList.append("USD")
            elif incomingInvoice.currency.code == "EUR":
                eurCount = eurCount + 1
                currencyList.append("EUR")
            elif incomingInvoice.currency.code == "GBP":
                gbpCount = gbpCount + 1
                currencyList.append("GBP")
            elif incomingInvoice.currency.code == "QAR":
                qarCount = qarCount + 1
                currencyList.append("QAR")
            elif incomingInvoice.currency.code == "RUB":
                rubCount = rubCount + 1
                currencyList.append("RUB")
            elif incomingInvoice.currency.code == "JPY":
                jpyCount = jpyCount + 1
                currencyList.append("JPY")
            elif incomingInvoice.currency.code == "TRY":
                tryCount = tryCount + 1
                currencyList.append("TRY")
                
        currencyList = list(set(currencyList))
        if len(currencyList) > 1:
            extraLineHeight = 14 * (len(currencyList) - 1)
            
        #standart ayar
        buffer = io.BytesIO()
        
        #dosyanın kaydedileceği konum
        folderPath = os.path.join(os.getcwd(), "media", "docs", str(sourceCompany.id), "account", "soa", "documents")
        
        #dosyanın kaydedileceği klasör oluşmamışsa onu oluşturur
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        
        #font ayarları
        rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
        pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
        
        #standart ayar
        p = canvas.Canvas(folderPath + "/" + str(company.id) + "-incoming.pdf", pagesize = A4)
        
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
        
        #####sol üst tablo#####
        #company
        p.setFillColor(HexColor("#000"))
        p.setFont('Inter-Bold', 6)
        p.drawString(35, h-100, "COMPANY : ")
        p.setFont('Inter', 6)
        
        #tek satırlık metinde yazı belirli bir uzunluğu geçince \n ekler
        newCompanyName = ""
        for i in range(0, len(company.name), 65):
            chunk = company.name[i:i+65]
            if len(chunk) < 65:
                newCompanyName += chunk
            else:
                space_index = chunk.rfind('')
                if space_index != -1:
                    newCompanyName += chunk[:space_index] + '\n'
                    if space_index + 1 < len(chunk):
                        newCompanyName += chunk[space_index+1:]
                else:
                    newCompanyName += chunk
        #alt satır komutu
        lines = newCompanyName.replace("\r\n", "\n")
        lines = lines.split('\n')
        line_height = 10  # İsteğe bağlı, satır yüksekliği
        current_y = h-100

        for line in lines:
            p.drawString(80, current_y, line)
            current_y = current_y - line_height
        #####company with multiple lines-end#####
        
        #####address with multiple lines#####
        #alt satır komutu
        # lines = company.address.replace("\r\n", "\n")
        # lines = lines.split('\n')
        # line_height = 8  # İsteğe bağlı, satır yüksekliği
        # current_y = current_y

        # for line in lines:
        #     p.drawString(35, current_y, line)
        #     current_y = current_y - line_height
        #####address with multiple lines-end#####

        
        p.setFont('Inter', 6)
        data=[("")]
        table = Table(data, colWidths=w/2-35, rowHeights=(tableRowHeight*2)+extraLineHeight)
        table.setStyle(TableStyle([
                                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                                ]))
        
        table.wrapOn(p, 30, h-115-extraLineHeight)
        table.drawOn(p, 30, h-115-extraLineHeight)
        #####sol üst tablo-end#####
        
        #####sağ üst tablo1#####
        if company.creditPeriod > 0:
            periodType = "DAYS"
        else:
            periodType = "DAY"
        # Para miktarını belirtilen formatta gösterme
        totalCredit = Decimal(str(company.credit)) + Decimal(str(company.creditLimit))
        creditLimitFixed = "{:,.2f}".format(round(totalCredit,2))
        # Nokta ile virgülü değiştirme
        creditLimitFixed = creditLimitFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        data=[["CREDIT LIMIT", str(creditLimitFixed) + " " + str(company.currency.code)],
            ["CREDIT PERIOD", str(company.creditPeriod) + " " + periodType]
            ]
        table = Table(data, colWidths=[((w/2-35)/2/2)-(5/2),((w/2-35)/2/2)-(5/2)], rowHeights=tableRowHeight+(extraLineHeight/2))
        table.setStyle(tableLeftStyleAmount)
        
        table.wrapOn(p, w/2+5, h-115-extraLineHeight)
        table.drawOn(p, w/2+5, h-115-extraLineHeight)
        #####sağ üst tablo1-end#####
        
        #####sağ üst tablo2#####
        totalAmountText = ""
        totalDueAmountText = ""
        for key, currency in enumerate(currencyList):
            incomingInvoicess = IncomingInvoice.objects.filter(seller = company, currency__code = currency)
            incomingInvoiceAmountTotal = 0
            incomingInvoiceDueAmountTotal = 0
            for incomingInvoicee in incomingInvoicess:
                incomingInvoiceAmountTotal = incomingInvoiceAmountTotal + (incomingInvoicee.totalPrice - incomingInvoicee.paidPrice)
                if incomingInvoicee.paymentDate < timezone.now().date():
                    incomingInvoiceDueAmountTotal = incomingInvoiceDueAmountTotal + (incomingInvoicee.totalPrice - incomingInvoicee.paidPrice)
            # Para miktarını belirtilen formatta gösterme
            incomingInvoiceAmountTotalFixed = "{:,.2f}".format(round(incomingInvoiceAmountTotal,2))
            incomingInvoiceDueAmountTotalFixed = "{:,.2f}".format(round(incomingInvoiceDueAmountTotal,2))
            # Nokta ile virgülü değiştirme
            incomingInvoiceAmountTotalFixed = incomingInvoiceAmountTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            incomingInvoiceDueAmountTotalFixed = incomingInvoiceDueAmountTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            keyCount = key + 1
            if keyCount == len(currencyList):
                totalAmountText = totalAmountText + str(incomingInvoiceAmountTotalFixed) + " " + str(currency)
                totalDueAmountText = totalDueAmountText + str(incomingInvoiceDueAmountTotalFixed) + " " + str(currency)
            else:
                totalAmountText = totalAmountText + str(incomingInvoiceAmountTotalFixed) + " " + str(currency) + "\n"
                totalDueAmountText = totalDueAmountText + str(incomingInvoiceDueAmountTotalFixed) + " " + str(currency) + "\n"
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
                th = h+50
            else:
                th = h
                
            #####parts tablo#####
            
            partsTableStyleLeftZero = TableStyle([('INNERGRID', (0,2), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
                                    ('INNERGRID', (0,-1), (-1,-1), 0.25, colors.white),
                                    ('BOX', (0,0), (-1,-2), 0.25, "rgba(0,56,101,0.65)"),
                                    ('FONT', (0, 0), (-1, -1), 'Inter', 6),
                                    ('FONT', (0, 0), (-1, 1), 'Inter-Bold', 6),
                                    ('FONT', (0, -1), (-1, -1), 'Inter-Bold', 6),
                                    ('ALIGN', (0, 0), (-1, -1), "LEFT"),
                                    ('ALIGN', (5, 0), (-1, -1), "RIGHT"),
                                    ('TEXTCOLOR',(0,1), (-1,1), colors.white),
                                    #('TEXTCOLOR',(0,2), (-1,2), colors.white),
                                    #('BACKGROUND',(0,0), (-1,0), "#009999"),
                                    ('BACKGROUND',(0,0), (-1,0), "rgba(0,56,101,0.40)"),
                                    ('BACKGROUND',(0,1), (-1,1), "#003865"),
                                    #('BACKGROUND',(0,2), (-1,2), "#003865"),
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
            
            ##########usd talo##########
            
            # data.append(["Vessel", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Currency"])
            # rowLengths = []
            # projectsList = []
            # for j in range(len(partsList)):
            #     if partsList[j]["currency"] == "USD":
            #         projectsList.append(partsList[j])
                    
            #         # Para miktarını belirtilen formatta gösterme
            #         totalPriceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"],2))
            #         paidPriceFixed = "{:,.2f}".format(round(partsList[j]["paidPrice"],2))
            #         balanceFixed = "{:,.2f}".format(round(partsList[j]["totalPrice"] - partsList[j]["paidPrice"],2))
            #         # Nokta ile virgülü değiştirme
            #         totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            #         paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            #         balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            #         rowLengths.append(partsList[j])
                    
            #         serviceCardsSequency = serviceCardsSequency + 1
            #         data.append([partsList[j]["vessel"], partsList[j]["request"], partsList[j]["invoiceNo"], partsList[j]["invoiceDate"], partsList[j]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[j]["currency"]])
                    
            #         balanceTotal = balanceTotal + partsList[j]["totalPrice"]
            
            # # Para miktarını belirtilen formatta gösterme
            # balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
            # # Nokta ile virgülü değiştirme
            # balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
            
            # data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "USD"])
            # table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*15, ((w-60)/100)*12 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
            # table1.setStyle(partsTableStyleLeft)
            
            if usdCount > 0:
            
                data=[["OUR 'USD' STATEMENT OF ACCOUNT IS AS SHOWN BELOW"],
                    ["Purchase Order No", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"]
                    ]
                
                tableStyleControlKey = 0
                rowLengths = []
                projectsList = []
                balanceTotal = 0
                for k in range(len(partsList)):
                    #her yeni vessel için döngü
                    if partsList[k]["currency"] == "USD":
                        projectsList.append(partsList[k])
                        
                        # Para miktarını belirtilen formatta gösterme
                        totalPriceFixed = "{:,.2f}".format(round(partsList[k]["totalPrice"],2))
                        paidPriceFixed = "{:,.2f}".format(round(partsList[k]["paidPrice"],2))
                        balanceFixed = "{:,.2f}".format(round(partsList[k]["totalPrice"] - partsList[k]["paidPrice"],2))
                        # Nokta ile virgülü değiştirme
                        totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        rowLengths.append(partsList[k])
                        
                        serviceCardsSequency = serviceCardsSequency + 1
                        data.append([str(partsList[k]["purchaseOrder"]), partsList[k]["request"], partsList[k]["invoiceNo"], partsList[k]["invoiceDate"], partsList[k]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[k]["currency"]])
                        
                        balanceTotal = balanceTotal + (partsList[k]["totalPrice"] - partsList[k]["paidPrice"])
                # Para miktarını belirtilen formatta gösterme
                balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
                # Nokta ile virgülü değiştirme
                balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "USD"])
                table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])

                table1.setStyle(partsTableStyleLeftZero)
        
                
                table1.wrapOn(p, 30, -99999999)
                table1.drawOn(p, 30, -99999999)
                #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
                table1TotalRowHeight = sum(table1._rowHeights)
                if len(projectsList) > 0:
                    tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                    table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight)
                    table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight)
                    tableSpace = tableSpace + 10
                
                #her yeni vessel için döngü-end
                data = []
                tableStyleControlKey = tableStyleControlKey + 1
                        
            ##########usd talo-end##########
            
            ##########eur talo##########
            if eurCount > 0:
            
                data=[["OUR 'EUR' STATEMENT OF ACCOUNT IS AS SHOWN BELOW"],
                    ["Purchase Order No", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"]
                    ]
                
                tableStyleControlKey = 0
                rowLengths = []
                projectsList = []
                balanceTotal = 0
                for k in range(len(partsList)):
                    #her yeni vessel için döngü
                    if partsList[k]["currency"] == "EUR":
                        projectsList.append(partsList[k])
                        
                        # Para miktarını belirtilen formatta gösterme
                        totalPriceFixed = "{:,.2f}".format(round(partsList[k]["totalPrice"],2))
                        paidPriceFixed = "{:,.2f}".format(round(partsList[k]["paidPrice"],2))
                        balanceFixed = "{:,.2f}".format(round(partsList[k]["totalPrice"] - partsList[k]["paidPrice"],2))
                        # Nokta ile virgülü değiştirme
                        totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        rowLengths.append(partsList[k])
                        
                        serviceCardsSequency = serviceCardsSequency + 1
                        data.append([str(partsList[k]["purchaseOrder"]), partsList[k]["request"], partsList[k]["invoiceNo"], partsList[k]["invoiceDate"], partsList[k]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[k]["currency"]])
                        
                        balanceTotal = balanceTotal + (partsList[k]["totalPrice"] - partsList[k]["paidPrice"])
                
                # Para miktarını belirtilen formatta gösterme
                balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
                # Nokta ile virgülü değiştirme
                balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "EUR"])
                table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
                
                table1.setStyle(partsTableStyleLeftZero)
        
                
                table1.wrapOn(p, 30, -99999999)
                table1.drawOn(p, 30, -99999999)
                #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
                table1TotalRowHeight = sum(table1._rowHeights)
                if len(projectsList) > 0:
                    tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                    table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                    table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                    tableSpace = tableSpace + 10
                
                #her yeni vessel için döngü-end
                data = []
                tableStyleControlKey = tableStyleControlKey + 1
                        
            ##########eur talo-end##########
            
            ##########try talo##########
            if tryCount > 0:
            
                data=[["OUR 'TRY' STATEMENT OF ACCOUNT IS AS SHOWN BELOW"],
                    ["Purchase Order No", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"]
                    ]
                
                tableStyleControlKey = 0
                rowLengths = []
                projectsList = []
                balanceTotal = 0
                for k in range(len(partsList)):
                    #her yeni vessel için döngü
                    if partsList[k]["currency"] == "TRY":
                        projectsList.append(partsList[k])
                        
                        # Para miktarını belirtilen formatta gösterme
                        totalPriceFixed = "{:,.2f}".format(round(partsList[k]["totalPrice"],2))
                        paidPriceFixed = "{:,.2f}".format(round(partsList[k]["paidPrice"],2))
                        balanceFixed = "{:,.2f}".format(round(partsList[k]["totalPrice"] - partsList[k]["paidPrice"],2))
                        # Nokta ile virgülü değiştirme
                        totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        rowLengths.append(partsList[k])
                        
                        serviceCardsSequency = serviceCardsSequency + 1
                        data.append([str(partsList[k]["purchaseOrder"]), partsList[k]["request"], partsList[k]["invoiceNo"], partsList[k]["invoiceDate"], partsList[k]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[k]["currency"]])
                        
                        balanceTotal = balanceTotal + (partsList[k]["totalPrice"] - partsList[k]["paidPrice"])
                
                # Para miktarını belirtilen formatta gösterme
                balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
                # Nokta ile virgülü değiştirme
                balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "TRY"])
                table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
                
                table1.setStyle(partsTableStyleLeftZero)
        
                
                table1.wrapOn(p, 30, -99999999)
                table1.drawOn(p, 30, -99999999)
                #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
                table1TotalRowHeight = sum(table1._rowHeights)
                if len(projectsList) > 0:
                    tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                    table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                    table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                    tableSpace = tableSpace + 10
                
                #her yeni vessel için döngü-end
                data = []
                tableStyleControlKey = tableStyleControlKey + 1
                        
            ##########try talo-end##########
            
            ##########rub talo##########
            if rubCount > 0:
            
                data=[["OUR 'RUB' STATEMENT OF ACCOUNT IS AS SHOWN BELOW"],
                    ["Purchase Order No", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"]
                    ]
                
                tableStyleControlKey = 0
                rowLengths = []
                projectsList = []
                balanceTotal = 0
                for k in range(len(partsList)):
                    #her yeni vessel için döngü
                    if partsList[k]["currency"] == "RUB":
                        projectsList.append(partsList[k])
                        
                        # Para miktarını belirtilen formatta gösterme
                        totalPriceFixed = "{:,.2f}".format(round(partsList[k]["totalPrice"],2))
                        paidPriceFixed = "{:,.2f}".format(round(partsList[k]["paidPrice"],2))
                        balanceFixed = "{:,.2f}".format(round(partsList[k]["totalPrice"] - partsList[k]["paidPrice"],2))
                        # Nokta ile virgülü değiştirme
                        totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        rowLengths.append(partsList[k])
                        
                        serviceCardsSequency = serviceCardsSequency + 1
                        data.append([str(partsList[k]["purchaseOrder"]), partsList[k]["request"], partsList[k]["invoiceNo"], partsList[k]["invoiceDate"], partsList[k]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[k]["currency"]])
                        
                        balanceTotal = balanceTotal + (partsList[k]["totalPrice"] - partsList[k]["paidPrice"])
                
                # Para miktarını belirtilen formatta gösterme
                balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
                # Nokta ile virgülü değiştirme
                balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "RUB"])
                table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
                
                table1.setStyle(partsTableStyleLeftZero)
        
                
                table1.wrapOn(p, 30, -99999999)
                table1.drawOn(p, 30, -99999999)
                #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
                table1TotalRowHeight = sum(table1._rowHeights)
                if len(projectsList) > 0:
                    tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                    table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                    table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                    tableSpace = tableSpace + 10
                
                #her yeni vessel için döngü-end
                data = []
                tableStyleControlKey = tableStyleControlKey + 1
                        
            ##########rub talo-end##########
            
            ##########gbp talo##########
            if gbpCount > 0:
            
                data=[["OUR 'GBP' STATEMENT OF ACCOUNT IS AS SHOWN BELOW"],
                    ["Purchase Order No", "Project No", "Invoice No", "Invoice Date", "Due Date", "Invoice Amount", "Total Payment", "Balance", "Curr"]
                    ]
                
                tableStyleControlKey = 0
                rowLengths = []
                projectsList = []
                balanceTotal = 0
                for k in range(len(partsList)):
                    #her yeni vessel için döngü
                    if partsList[k]["currency"] == "GBP":
                        projectsList.append(partsList[k])
                        
                        # Para miktarını belirtilen formatta gösterme
                        totalPriceFixed = "{:,.2f}".format(round(partsList[k]["totalPrice"],2))
                        paidPriceFixed = "{:,.2f}".format(round(partsList[k]["paidPrice"],2))
                        balanceFixed = "{:,.2f}".format(round(partsList[k]["totalPrice"] - partsList[k]["paidPrice"],2))
                        # Nokta ile virgülü değiştirme
                        totalPriceFixed = totalPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        paidPriceFixed = paidPriceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        balanceFixed = balanceFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                        rowLengths.append(partsList[k])
                        
                        serviceCardsSequency = serviceCardsSequency + 1
                        data.append([str(partsList[k]["purchaseOrder"]), partsList[k]["request"], partsList[k]["invoiceNo"], partsList[k]["invoiceDate"], partsList[k]["dueDate"], str(totalPriceFixed), str(paidPriceFixed), str(balanceFixed), partsList[k]["currency"]])
                        
                        balanceTotal = balanceTotal + (partsList[k]["totalPrice"] - partsList[k]["paidPrice"])
                
                # Para miktarını belirtilen formatta gösterme
                balanceTotalFixed = "{:,.2f}".format(round(balanceTotal,2))
                # Nokta ile virgülü değiştirme
                balanceTotalFixed = balanceTotalFixed.replace(',', 'temp').replace('.', ',').replace('temp', '.')
                
                data.append(["", "", "", "", "", "","", str(balanceTotalFixed), "GBP"])
                table1 = Table(data, colWidths=[((w-60)/100)*18 , ((w-60)/100)*13, ((w-60)/100)*14 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10 , ((w-60)/100)*10, ((w-60)/100)*10, ((w-60)/100)*5])
                
                table1.setStyle(partsTableStyleLeftZero)
        
                
                table1.wrapOn(p, 30, -99999999)
                table1.drawOn(p, 30, -99999999)
                #table.drawOn(p, 30, th-235-((((sum(rowLengths)*6)+(len(items)*10))-i)+15))
                table1TotalRowHeight = sum(table1._rowHeights)
                if len(projectsList) > 0:
                    tableTotalRowHeight = tableTotalRowHeight + sum(table1._rowHeights)
                    table1.wrapOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                    table1.drawOn(p, 30, th-125-tableTotalRowHeight-extraLineHeight-5)
                    tableSpace = tableSpace + 10
                
                #her yeni vessel için döngü-end
                data = []
                tableStyleControlKey = tableStyleControlKey + 1
                        
            ##########gbp talo-end##########
            
            
            ######sayfa altı########
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
        logger.info(e)
 
