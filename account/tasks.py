from celery import shared_task
from celery.result import AsyncResult
from core.celery import app
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.db.models import Count
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
import io
import shutil
from django.utils import timezone
from datetime import datetime
import json
import random
import string
import time

from .pdfs.send_invoice_pdfs import *
from .pdfs.incoming_invoice_pdfs import *
from .pdfs.soa_pdfs import *

from .models import SendInvoice
from card.models import Company
from source.models import Company as SourceCompany

def sendAlert(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "send_alert",
            "message": message,
            "location" : location
        }
    )

@shared_task(bind=True)
def add(self, seconds):
    return seconds

@shared_task
def sendInvoicePdfTask(sourceCompanyId, invoiceId, base_url,elementTag):
    sendInvoicePdf(sourceCompanyId, invoiceId, base_url,elementTag)

@shared_task
def incomingInvoicePdfTask(sourceCompanyId, invoiceId, base_url,elementTag):
    incomingInvoicePdf(sourceCompanyId, invoiceId, base_url,elementTag)

@shared_task
def soaPdfTask(companyId, sourceCompanyId):
    
    soaPdf(companyId, sourceCompanyId)
    soaIncomingPdf(companyId, sourceCompanyId)
