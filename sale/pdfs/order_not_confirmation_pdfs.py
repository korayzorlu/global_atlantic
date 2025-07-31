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


   
def orderNotConfirmationPdf(orderNotConfirmation):
    buffer = io.BytesIO()
    
    folderPath = os.path.join(os.getcwd(), "media", "temp_pdf")
    
    if os.path.exists(folderPath):
        shutil.rmtree(folderPath)
    
    os.makedirs(folderPath, exist_ok = True)
    
    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/static/fonts')
    pdfmetrics.registerFont(TTFont('Inter', 'Inter-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-SemiBold.ttf'))
    
    p = canvas.Canvas(folderPath + "/" + orderNotConfirmation.orderNotConfirmationNo + ".pdf", pagesize = A4)
    
    w, h = A4
    
    ystart = 800
    
    esmsImg = Image.open(os.path.join(os.getcwd(), "media", "companies", "18", "229681054_3982667168525395_753349011554087447_n.jpg"))
    
    p.drawInlineImage(esmsImg, w/2-20, ystart-10, width=40,height=40)

    p.setFont('Inter', 16)
    p.setFillColor(HexColor("#922724"))
    p.drawCentredString(w/2, ystart-40, "NOT CONFIRMED QUOTATION")
    
    p.setLineWidth(0.2)
    p.line(20, ystart-60, 580, ystart-60)
    
    p.setFillColor(HexColor("#000"))
    
    p.setFont('Inter-Bold', 9)
    p.drawString(30, ystart-80, "Customer")
    p.setFont('Inter', 9)
    p.drawString(120, ystart-80, ":" + orderNotConfirmation.quotation.inquiry.theRequest.customer.name)
    
    p.setFont('Inter-Bold', 9)
    p.drawString(30, ystart-90, "Vessel")
    p.setFont('Inter', 9)
    p.drawString(120, ystart-90, ":" + orderNotConfirmation.quotation.inquiry.theRequest.vessel.name)
    
    p.setFont('Inter-Bold', 9)
    p.drawString(30, ystart-110, "Quotation")
    p.setFont('Inter', 9)
    p.drawString(120, ystart-110, ":" + orderNotConfirmation.quotation.quotationNo)
    
    p.setFont('Inter-Bold', 9)
    p.drawString(30, ystart-120, "Not Confirmation")
    p.setFont('Inter', 9)
    p.drawString(120, ystart-120, ":" + orderNotConfirmation.orderNotConfirmationNo)
    
    p.setFont('Inter-Bold', 9)
    p.drawString(30, ystart-160, "Please specify, at the time of the feedback collected, how many days have passed from the time when the proposal was sent?")
    p.setFont('Inter', 9)
    p.drawString(50, ystart-180, str(orderNotConfirmation.delay) + " days")
    
    p.setFont('Inter-Bold', 9)
    p.drawString(30, ystart-220, "Please specify in which way the order process is controlled")
    p.setFont('Inter', 9)
    p.drawString(50, ystart-240, str(orderNotConfirmation.get_orderProcessType_display()))
    
    p.setFont('Inter-Bold', 9)
    p.drawString(30, ystart-280, "Which of the following words would you use to describe customers reaction to you?")
    p.setFont('Inter', 9)
    p.drawString(50, ystart-300, str(orderNotConfirmation.get_customerReaction_display()))
    
    p.setFont('Inter-Bold', 9)
    p.drawString(30, ystart-340, "Is the final decision on the order process made by the customer?")
    p.setFont('Inter', 9)
    p.drawString(50, ystart-360, str(orderNotConfirmation.get_finalDecision_display()))
    
    p.setFont('Inter-Bold', 9)
    p.drawString(30, ystart-400, "Which of the following reasons are stated by customer for not accepting the offer?")
    reasons = orderNotConfirmation.reasons.all()
    ystartx = ystart-400
    for reason in reasons:
        p.setFont('Inter', 9)
        p.drawString(50, ystartx-20, str(reason.name))
        ystartx = ystartx - 20
    
    p.setFont('Inter-Bold', 9)
    p.drawString(30, ystartx - 40, "Do you have any suggestion for future offers regarding to take place and to be more efficient, cost-effective timely?")
    p.setFont('Inter', 9)
    p.drawString(50, ystartx - 60, str(orderNotConfirmation.suggestion))

    p.save()
  