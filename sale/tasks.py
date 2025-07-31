from celery import shared_task
from core.celery import app
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage, send_mail

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, TableStyle
from reportlab.platypus.tables import Table
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont   
from reportlab import rl_config
from PIL import Image

import os
import pwd
import grp
import io
import shutil
from datetime import datetime
import json
import random
import string


from .models import Inquiry, Quotation, Request, QuotationPart, InquiryPart, QuotationExtra, PurchaseOrder
from data.models import Part
from source.models import Company as SourceCompany
from card.models import EnginePart

from .pdfs.inquiry_pdfs import *
from .pdfs.quotation_pdfs import *
from .pdfs.purchase_order_pdfs import *

@shared_task
def add(aa):
    print(aa)
    
    return "test başarılı yeni"

@shared_task
def companyAdd(company):
    company.save()
    return HttpResponse(status=204)

@shared_task
def sendEmail(item):
    def send_outlook_email(subject, message, from_email, recipient_list):
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
    subject = 'Konu'
    message = 'Merhaba, bu bir test e-postasıdır.'
    from_email = 'armin_koray@hotmail.com'
    recipient_list = ['korayzorllu@gmail.com']

    send_outlook_email(subject, message, from_email, recipient_list)

@shared_task
def documentsJSON():
    documentsJSON = {"data":[]}
    levels = ["project", "inquiry", "quotation", "order_confirmation", "order_not_confirmation", "purchase_order"]
    
    for level in levels:
        start_dir = os.path.join(os.getcwd(), "media", "sale", level)
        #hedef dosyayı başlangıç klasörü içerisinde alt klasörleri de tarayarak arar
        for root, dirs, files in os.walk(start_dir):
            for file in files:
                file_path = os.path.join(root, file).replace(os.getcwd(), "")
                documentsJSON["data"].append({"path" : file_path, "name" : file, "main" : "sale", "level" : level})

    documentsJSON = json.dumps(documentsJSON)
    
    with open(os.path.join(os.getcwd(), "media", "documents.json"), "w") as f:
        f.write(documentsJSON)
    return HttpResponse(status=204)

@shared_task
def inquiryPdfInTask(id,sourceCompanyId):
    inquiryPdf(id,sourceCompanyId)

@shared_task
def quotationPdfInTask(id, sourceCompanyId):
    quotationPdf(id, sourceCompanyId)

@shared_task
def purchaseOrderPdfInTask(id, sourceCompanyId):
    purchaseOrderPdf(id, sourceCompanyId)
    