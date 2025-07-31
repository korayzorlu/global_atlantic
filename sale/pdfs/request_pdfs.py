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

def requestPdf(request):
    buffer = io.BytesIO()
    
    folderPath = os.path.join(os.getcwd(), "media", "temp_pdf")
    
    if os.path.exists(folderPath):
        shutil.rmtree(folderPath)
    
    os.makedirs(folderPath, exist_ok = True)
    
    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
    pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
    
    p = canvas.Canvas(folderPath + "/" + request.requestNo + ".pdf", pagesize = A4)
    
    w, h = A4
    
    ystart = 800
    
    esmsImg = Image.open(os.path.join(os.getcwd(), "static", "images", "esms-logo2.jpg"))
    
    p.drawInlineImage(esmsImg, 30, ystart-10, width=102,height=40)
    
    p.setFont('Inter-Bold', 8)
    p.drawString(450, ystart+10, "DATE")
    p.setFont('Inter', 8)
    p.drawString(480, ystart+10, ":" + str(request.requestDate.strftime("%d.%m.%Y")))
    
    p.setFont('Inter', 20)
    p.setFillColor(HexColor("#922724"))
    p.drawCentredString(w/2, ystart-60, "REQUEST")
    
    p.setFillColor(HexColor("#000"))
    
    ######sayfa altı########
    p.setStrokeColor(HexColor("#808080"))
    p.line(30, 100, 560, 100)
    p.setFont('Inter-Bold', 8)
    p.drawString(30, 90, "ESMS DENİZCİLİK ENERJİ TAAHHÜT MÜHENDİSLİK SANAYİ VE TİC. A.Ş.")
    p.drawString(30, 80, "Office")
    p.setFont('Inter', 8)
    p.drawString(60, 80, "Aydıntepe Mah. Sahil Bulvarı Cad. Denizciler Ticaret Merkezi")
    p.drawString(60, 70, "No:126 57/C P.K. 34947 Tuzla İstanbul TR")
    p.setFont('Inter-Bold', 8)
    p.drawString(30, 60, "Tel")
    p.setFont('Inter', 8)
    p.drawString(60, 60, "+90 (216) 330 82 46")
    p.setFont('Inter-Bold', 8)
    p.drawString(30, 50, "Fax")
    p.setFont('Inter', 8)
    p.drawString(60, 50, "+90 (216) 330 74 06")
    
    p.setFont('Inter-Bold', 8)
    p.drawString(310, 80, "Workshop")
    p.setFont('Inter', 8)
    p.drawString(360, 80, "Aydıntepe Mah. Sahilyolu Cad. No:124 Tuzla, İstanbul,")
    p.drawString(360, 70, "TURKEY")
    p.setFont('Inter-Bold', 8)
    p.drawString(310, 60, "Tel")
    p.setFont('Inter', 8)
    p.drawString(360, 60, "+90 (216) 494 16 11")
    p.setFont('Inter-Bold', 8)
    p.drawString(310, 50, "Fax")
    p.setFont('Inter', 8)
    p.drawString(360, 50, "+90 (216) 494 13 21")
    
    p.line(30, 40, 560, 40)
    p.setFont('Inter-Bold', 8)
    p.drawString(30, 30, request.project.user.first_name + " " + request.project.user.last_name + " / " + request.project.user.profile.position)
    p.setFont('Inter-Bold', 8)
    p.drawString(310, 30, "Document Date: " + str(datetime.today().date().strftime("%d.%m.%Y")))
     ######sayfa altı-end########
    
    p.save()
    