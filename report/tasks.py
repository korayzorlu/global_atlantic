from celery import shared_task
from core.celery import app
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.utils import timezone

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

from datetime import datetime
import requests as rs
import xmltodict
import json

from .pdfs.order_pdfs import *

from card.models import Currency

@shared_task
def sendMailDailyFinancialReport():
    startDate = datetime.today().date()
    endDate = datetime.today().date()
    
    financialReportForMailPdf(startDate, endDate)
    
    today = datetime.today().date().strftime("%d.%m.%Y")
        
    def send_outlook_email(subject, message, from_email, recipient_list, attachments=None):
        email = EmailMessage(
            subject,
            message,
            from_email,
            recipient_list,
        )
        if attachments:
            for attachment in attachments:
                email.attach(attachment['name'], attachment['content'], attachment['mimetype'])
        email.send(fail_silently=False)
        #send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
    subject = 'Daily Financial Report'
    message = f'The daily financial report dated {today} is attached.'
    from_email = 'ESMS - Michoapp <reporting@esmarinesolutions.com>'
    #recipient_list = ['koray.zorlu@novutechnologies.com']
    recipient_list = ['semih.ege@echoesgroup.com','onur.coban@esmarinesolutions.com','koray.zorlu@novutechnologies.com']
    
    today = datetime.today().date().strftime('%d_%m_%Y')
    
    with open(f'./media/report/financial_report/documents/financial_report_{today}.pdf', 'rb') as f:
        attachments = [
            {
                'name': f'financial_report_{today}.pdf',
                'content': f.read(),
                'mimetype': 'application/pdf'
            }
        ]

    send_outlook_email(subject, message, from_email, recipient_list, attachments)
    
@shared_task
def sendMailDailyFinancialReportTest():
    startDate = datetime.today().date()
    endDate = datetime.today().date()
    
    financialReportForMailPdf(startDate, endDate)
    
    today = datetime.today().date().strftime("%d.%m.%Y")
        
    def send_outlook_email(subject, message, from_email, recipient_list, attachments=None):
        email = EmailMessage(
            subject,
            message,
            from_email,
            recipient_list,
        )
        if attachments:
            for attachment in attachments:
                email.attach(attachment['name'], attachment['content'], attachment['mimetype'])
        email.send(fail_silently=False)
        #send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
    subject = 'Daily Financial Report'
    message = f'The daily financial report dated {today} is attached.'
    from_email = 'ESMS - Michoapp <reporting@esmarinesolutions.com>'
    recipient_list = ['koray.zorlu@novutechnologies.com']
    
    today = datetime.today().date().strftime('%d_%m_%Y')
    
    with open(f'./media/report/financial_report/documents/financial_report_{today}.pdf', 'rb') as f:
        attachments = [
            {
                'name': f'financial_report_{today}.pdf',
                'content': f.read(),
                'mimetype': 'application/pdf'
            }
        ]
        
    send_outlook_email(subject, message, from_email, recipient_list, attachments)
    
@shared_task
def financialReportPdfInTask(request,startDate,endDate,sourceCompanyId):
    financialReportPdf(request,startDate,endDate,sourceCompanyId)