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

from card.models import Currency

@shared_task
def exchangeUpdate():
    if rs.get("https://www.tcmb.gov.tr/kurlar/today.xml").status_code == 200:
        ratesSource = rs.get("https://www.tcmb.gov.tr/kurlar/today.xml").content
        rates = xmltodict.parse(ratesSource)
        jsonRates = json.dumps(rates)
        with open("card/fixtures/exchange-rates.json", "w") as f:
            f.write(jsonRates)
        
        ratesDate = rates["Tarih_Date"]["@Tarih"]
        rates = rates["Tarih_Date"]["Currency"]
        
        rates_usd = next((rate for rate in rates if rate['@Kod'] == 'USD'), None)
        rates_eur = next((rate for rate in rates if rate['@Kod'] == 'EUR'), None)
        rates_gbp = next((rate for rate in rates if rate['@Kod'] == 'GBP'), None)
        rates_qar = next((rate for rate in rates if rate['@Kod'] == 'QAR'), None)
        rates_rub = next((rate for rate in rates if rate['@Kod'] == 'RUB'), None)
        rates_jpy = next((rate for rate in rates if rate['@Kod'] == 'JPY'), None)
        
        trl = Currency.objects.get(code = "TRY")
        usd = Currency.objects.get(code = "USD")
        eur = Currency.objects.get(code = "EUR")
        gbp = Currency.objects.get(code = "GBP")
        qar = Currency.objects.get(code = "QAR")
        rub = Currency.objects.get(code = "RUB")
        jpy = Currency.objects.get(code = "JPY")
        
        trl.baseCurrency = "try"
        trl.forexBuying = 1.00
        trl.forexSelling = 1.00
        trl.banknoteBuying = 1.00
        trl.banknoteBuying = 1.00
        trl.rateUSD = rates_usd["ForexBuying"]
        trl.rateOther = None
        trl.rateDate = timezone.now().date()
        trl.tcmbRateDate = ratesDate
        trl.save()
        
        usd.baseCurrency = "try"
        usd.forexBuying = rates_usd["ForexBuying"]
        usd.forexSelling = rates_usd["ForexSelling"]
        usd.banknoteBuying = rates_usd["BanknoteBuying"]
        usd.banknoteBuying = rates_usd["BanknoteSelling"]
        usd.rateUSD = None
        usd.rateOther = None
        usd.rateDate = timezone.now().date()
        usd.tcmbRateDate = ratesDate
        usd.save()
        
        eur.baseCurrency = "try"
        eur.forexBuying = rates_eur["ForexBuying"]
        eur.forexSelling = rates_eur["ForexSelling"]
        eur.banknoteBuying = rates_eur["BanknoteBuying"]
        eur.banknoteBuying = rates_eur["BanknoteSelling"]
        eur.rateUSD = None
        eur.rateOther = rates_eur["CrossRateOther"]
        eur.rateDate = timezone.now().date()
        eur.tcmbRateDate = ratesDate
        eur.save()
        
        gbp.baseCurrency = "try"
        gbp.forexBuying = rates_gbp["ForexBuying"]
        gbp.forexSelling = rates_gbp["ForexSelling"]
        gbp.banknoteBuying = rates_gbp["BanknoteBuying"]
        gbp.banknoteBuying = rates_gbp["BanknoteSelling"]
        gbp.rateUSD = None
        gbp.rateOther = rates_gbp["CrossRateOther"]
        gbp.rateDate = timezone.now().date()
        gbp.tcmbRateDate = ratesDate
        gbp.save()
        
        qar.baseCurrency = "try"
        qar.forexBuying = rates_qar["ForexBuying"]
        qar.forexSelling = rates_qar["ForexSelling"]
        qar.banknoteBuying = rates_qar["BanknoteBuying"]
        qar.banknoteBuying = rates_qar["BanknoteSelling"]
        qar.rateUSD = rates_qar["CrossRateUSD"]
        qar.rateOther = None
        qar.rateDate = timezone.now().date()
        qar.tcmbRateDate = ratesDate
        qar.save()
        
        rub.baseCurrency = "try"
        rub.forexBuying = rates_rub["ForexBuying"]
        rub.forexSelling = rates_rub["ForexSelling"]
        rub.banknoteBuying = rates_rub["BanknoteBuying"]
        rub.banknoteBuying = rates_rub["BanknoteSelling"]
        rub.rateUSD = rates_rub["CrossRateUSD"]
        rub.rateOther = None
        rub.rateDate = timezone.now().date()
        rub.tcmbRateDate = ratesDate
        rub.save()
        
        jpy.baseCurrency = "try"
        jpy.forexBuying = round(float(rates_jpy["ForexBuying"]) / 100, 4)
        jpy.forexSelling = round(float(rates_jpy["ForexSelling"]) / 100, 4)
        jpy.banknoteBuying = round(float(rates_jpy["BanknoteBuying"]) / 100, 4)
        jpy.banknoteBuying = round(float(rates_jpy["BanknoteSelling"]) / 100, 4)
        jpy.rateUSD = rates_jpy["CrossRateUSD"]
        jpy.rateOther = None
        jpy.rateDate = timezone.now().date()
        jpy.tcmbRateDate = ratesDate
        jpy.save()