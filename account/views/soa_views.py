from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
# Create your views here.
from django.views import View
from django.contrib import messages
from django.core import serializers
from urllib.parse import urlparse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.middleware.csrf import get_token

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa
from django.template.loader import get_template 
import json
from itertools import chain
import xmltodict
import requests as rs
from django.utils import timezone
from datetime import datetime, timedelta

from ..forms import *
from ..tasks import *
from ..pdfs.soa_pdfs import *

from sale.models import OrderTracking, OrderConfirmation, Collection, CollectionPart, Delivery,Inquiry
from source.models import Company as SourceCompany
from source.models import Bank as SourceBank
from service.models import Offer
from card.models import Current
from data.models import Part

import random
import string
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Border, Side

#####SOA#####

class SOADataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("SOA")
        elementTag = "soa"
        elementTagSub = "soaPart"

        ##### Doviz Guncelleme #####

        trl = Currency.objects.get(code = "TRY")
        usd = Currency.objects.get(code = "USD")
        eur = Currency.objects.get(code = "EUR")
        gbp = Currency.objects.get(code = "GBP")
        qar = Currency.objects.get(code = "QAR")
        rub = Currency.objects.get(code = "RUB")
        jpy = Currency.objects.get(code = "JPY")
        
        # if rs.get("https://www.tcmb.gov.tr/kurlar/today.xml").status_code == 200:
        #     ratesSource = rs.get("https://www.tcmb.gov.tr/kurlar/today.xml").content
        #     rates = xmltodict.parse(ratesSource)
        #     jsonRates = json.dumps(rates)
        #     with open("card/fixtures/exchange-rates.json", "w") as f:
        #         f.write(jsonRates)
            
        #     ratesDate = rates["Tarih_Date"]["@Tarih"]
        #     rates = rates["Tarih_Date"]["Currency"]
            
        #     rates_usd = next((rate for rate in rates if rate['@Kod'] == 'USD'), None)
        #     rates_eur = next((rate for rate in rates if rate['@Kod'] == 'EUR'), None)
        #     rates_gbp = next((rate for rate in rates if rate['@Kod'] == 'GBP'), None)
        #     rates_qar = next((rate for rate in rates if rate['@Kod'] == 'QAR'), None)
        #     rates_rub = next((rate for rate in rates if rate['@Kod'] == 'RUB'), None)
        #     rates_jpy = next((rate for rate in rates if rate['@Kod'] == 'JPY'), None)
            
        #     trl = Currency.objects.get(code = "TRY")
        #     usd = Currency.objects.get(code = "USD")
        #     eur = Currency.objects.get(code = "EUR")
        #     gbp = Currency.objects.get(code = "GBP")
        #     qar = Currency.objects.get(code = "QAR")
        #     rub = Currency.objects.get(code = "RUB")
        #     jpy = Currency.objects.get(code = "JPY")
            
        #     trl.baseCurrency = "try"
        #     trl.forexBuying = 1.00
        #     trl.forexSelling = 1.00
        #     trl.banknoteBuying = 1.00
        #     trl.banknoteBuying = 1.00
        #     trl.rateUSD = rates_usd["ForexBuying"]
        #     trl.rateOther = None
        #     trl.rateDate = timezone.now().date()
        #     trl.tcmbRateDate = ratesDate
        #     trl.save()
            
        #     usd.baseCurrency = "try"
        #     usd.forexBuying = rates_usd["ForexBuying"]
        #     usd.forexSelling = rates_usd["ForexSelling"]
        #     usd.banknoteBuying = rates_usd["BanknoteBuying"]
        #     usd.banknoteBuying = rates_usd["BanknoteSelling"]
        #     usd.rateUSD = None
        #     usd.rateOther = None
        #     usd.rateDate = timezone.now().date()
        #     usd.tcmbRateDate = ratesDate
        #     usd.save()
            
        #     eur.baseCurrency = "try"
        #     eur.forexBuying = rates_eur["ForexBuying"]
        #     eur.forexSelling = rates_eur["ForexSelling"]
        #     eur.banknoteBuying = rates_eur["BanknoteBuying"]
        #     eur.banknoteBuying = rates_eur["BanknoteSelling"]
        #     eur.rateUSD = None
        #     eur.rateOther = rates_eur["CrossRateOther"]
        #     eur.rateDate = timezone.now().date()
        #     eur.tcmbRateDate = ratesDate
        #     eur.save()
            
        #     gbp.baseCurrency = "try"
        #     gbp.forexBuying = rates_gbp["ForexBuying"]
        #     gbp.forexSelling = rates_gbp["ForexSelling"]
        #     gbp.banknoteBuying = rates_gbp["BanknoteBuying"]
        #     gbp.banknoteBuying = rates_gbp["BanknoteSelling"]
        #     gbp.rateUSD = None
        #     gbp.rateOther = rates_gbp["CrossRateOther"]
        #     gbp.rateDate = timezone.now().date()
        #     gbp.tcmbRateDate = ratesDate
        #     gbp.save()
            
        #     qar.baseCurrency = "try"
        #     qar.forexBuying = rates_qar["ForexBuying"]
        #     qar.forexSelling = rates_qar["ForexSelling"]
        #     qar.banknoteBuying = rates_qar["BanknoteBuying"]
        #     qar.banknoteBuying = rates_qar["BanknoteSelling"]
        #     qar.rateUSD = rates_qar["CrossRateUSD"]
        #     qar.rateOther = None
        #     qar.rateDate = timezone.now().date()
        #     qar.tcmbRateDate = ratesDate
        #     qar.save()
            
        #     rub.baseCurrency = "try"
        #     rub.forexBuying = rates_rub["ForexBuying"]
        #     rub.forexSelling = rates_rub["ForexSelling"]
        #     rub.banknoteBuying = rates_rub["BanknoteBuying"]
        #     rub.banknoteBuying = rates_rub["BanknoteSelling"]
        #     rub.rateUSD = rates_rub["CrossRateUSD"]
        #     rub.rateOther = None
        #     rub.rateDate = timezone.now().date()
        #     rub.tcmbRateDate = ratesDate
        #     rub.save()
            
        #     jpy.baseCurrency = "try"
        #     jpy.forexBuying = round(float(rates_jpy["ForexBuying"]) / 100,4)
        #     jpy.forexSelling = round(float(rates_jpy["ForexSelling"]) / 100,4)
        #     jpy.banknoteBuying = round(float(rates_jpy["BanknoteBuying"]) / 100,4)
        #     jpy.banknoteBuying = round(float(rates_jpy["BanknoteSelling"]) / 100,4)
        #     jpy.rateUSD = rates_jpy["CrossRateUSD"]
        #     jpy.rateOther = None
        #     jpy.rateDate = timezone.now().date()
        #     jpy.tcmbRateDate = ratesDate
        #     jpy.save()
        
        ##### Doviz Guncelleme-end #####

        #sum(sendInvoiceUSD.totalPrice for sendInvoiceUSD in sendInvoicesUSD)

        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "usd" : usd,
                    "eur" : eur,
                    "gbp" : gbp,
                    "qar" : qar,
                    "rub" : rub,
                    "jpy" : jpy,
                    # "ratesDate" : ratesDate,
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/soa.html', context)
    
class SOAUpdateViewEx(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("SOA")
        elementTag = "soa"
        elementTagSub = "soaPart"
        elementTagId = id
        
        company = Company.objects.get(id = id)

        ratesSource = rs.get("https://www.tcmb.gov.tr/kurlar/today.xml").content
        rates = xmltodict.parse(ratesSource)
        rates = rates["Tarih_Date"]["Currency"]
        
        usd = next((rate for rate in rates if rate['@Kod'] == 'USD'), None)
        eur = next((rate for rate in rates if rate['@Kod'] == 'EUR'), None)
        gbp = next((rate for rate in rates if rate['@Kod'] == 'GBP'), None)
        aud = next((rate for rate in rates if rate['@Kod'] == 'AUD'), None)
        cad = next((rate for rate in rates if rate['@Kod'] == 'CAD'), None)
        jpy = next((rate for rate in rates if rate['@Kod'] == 'JPY'), None)
        
        exchange = {"usd_fb" : usd['ForexBuying'],
                        "eur_fb" : eur['ForexBuying'],
                        "gbp_fb" : gbp['ForexBuying'],
                        "aud_fb" : aud['ForexBuying'],
                        "cad_fb" : cad['ForexBuying'],
                        "jpy_fb" : jpy['ForexBuying'],
                        "usd_fs" : usd['ForexSelling'],
                        "eur_fs" : eur['ForexSelling'],
                        "gbp_fs" : gbp['ForexSelling'],
                        "aud_fs" : aud['ForexSelling'],
                        "cad_fs" : cad['ForexSelling'],
                        "jpy_fs" : jpy['ForexSelling']
                        }
        
        #current-usd
        currentsUSD = Current.objects.filter(currency = 106, company = company)
        currentsUSDDebtTotal = 0
        currentsUSDCreditTotal = 0
        currentsUSDBalanceTotal = 0
        for currentUSD in currentsUSD:
            currentsUSDDebtTotal = currentsUSDDebtTotal + currentUSD.debt
            currentsUSDCreditTotal = currentsUSDCreditTotal + currentUSD.credit
        currentsUSDBalanceTotal = currentsUSDDebtTotal - currentsUSDCreditTotal
        
        #current-eur
        currentsEUR = Current.objects.filter(currency = 33, company = company)
        currentsEURDebtTotal = 0
        currentsEURCreditTotal = 0
        for currentEUR in currentsEUR:
            currentsEURDebtTotal = currentsEURDebtTotal + currentEUR.debt
            currentsEURCreditTotal = currentsEURCreditTotal + currentEUR.credit
        currentsEURBalanceTotal = currentsEURDebtTotal - currentsEURCreditTotal
        
        #current-gbp
        currentsGBP = Current.objects.filter(currency = 105, company = company)
        currentsGBPDebtTotal = 0
        currentsGBPCreditTotal = 0
        for currentGBP in currentsGBP:
            currentsGBPDebtTotal = currentsGBPDebtTotal + currentGBP.debt
            currentsGBPCreditTotal = currentsGBPCreditTotal + currentGBP.credit
        currentsGBPBalanceTotal = currentsGBPDebtTotal - currentsGBPCreditTotal
        
        #current-aud
        currentsAUD = Current.objects.filter(currency = 5, company = company)
        currentsAUDDebtTotal = 0
        currentsAUDCreditTotal = 0
        for currentAUD in currentsAUD:
            currentsAUDDebtTotal = currentsAUDDebtTotal + currentAUD.debt
            currentsAUDCreditTotal = currentsAUDCreditTotal + currentAUD.credit
        currentsAUDBalanceTotal = currentsAUDDebtTotal - currentsAUDCreditTotal
        
        #current-jpy
        currentsJPY = Current.objects.filter(currency = 52, company = company)
        currentsJPYDebtTotal = 0
        currentsJPYCreditTotal = 0
        for currentJPY in currentsJPY:
            currentsJPYDebtTotal = currentsJPYDebtTotal + currentJPY.debt
            currentsJPYCreditTotal = currentsJPYCreditTotal + currentJPY.credit
        currentsJPYBalanceTotal = currentsJPYDebtTotal - currentsJPYCreditTotal
        
        #current-cny
        currentsCNY = Current.objects.filter(currency = 22, company = company)
        currentsCNYDebtTotal = 0
        currentsCNYCreditTotal = 0
        for currentCNY in currentsCNY:
            currentsCNYDebtTotal = currentsCNYDebtTotal + currentCNY.debt
            currentsCNYCreditTotal = currentsCNYCreditTotal + currentCNY.credit
        currentsCNYBalanceTotal = currentsCNYDebtTotal - currentsCNYCreditTotal
        
        #current-cad
        currentsCAD = Current.objects.filter(currency = 19, company = company)
        currentsCADDebtTotal = 0
        currentsCADCreditTotal = 0
        for currentCAD in currentsCAD:
            currentsCADDebtTotal = currentsCADDebtTotal + currentCAD.debt
            currentsCADCreditTotal = currentsCADCreditTotal + currentCAD.credit
        currentsCADBalanceTotal = currentsCADDebtTotal - currentsCADCreditTotal
        
        #current-try
        currentsTRY = Current.objects.filter(currency = 102, company = company)
        currentsTRYDebtTotal = 0
        currentsTRYCreditTotal = 0
        for currentTRY in currentsTRY:
            currentsTRYDebtTotal = currentsTRYDebtTotal + currentTRY.debt
            currentsTRYCreditTotal = currentsTRYCreditTotal + currentTRY.credit
        currentsTRYBalanceTotal = currentsTRYDebtTotal - currentsTRYCreditTotal

        
        
        soaPdf()
        soaIncomingPdf()
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "elementTagId" : elementTagId,
                    "company" : company,
                    "exchange" : exchange,
                    "currentsUSDDebtTotal" : currentsUSDDebtTotal,
                    "currentsUSDCreditTotal" : currentsUSDCreditTotal,
                    "currentsUSDBalanceTotal" : currentsUSDBalanceTotal,
                    "currentsEURDebtTotal" : currentsEURDebtTotal,
                    "currentsEURCreditTotal" : currentsEURCreditTotal,
                    "currentsEURBalanceTotal" : currentsEURBalanceTotal,
                    "currentsGBPDebtTotal" : currentsGBPDebtTotal,
                    "currentsGBPCreditTotal" : currentsGBPCreditTotal,
                    "currentsGBPBalanceTotal" : currentsGBPBalanceTotal,
                    "currentsAUDDebtTotal" : currentsAUDDebtTotal,
                    "currentsAUDCreditTotal" : currentsAUDCreditTotal,
                    "currentsAUDBalanceTotal" : currentsAUDBalanceTotal,
                    "currentsJPYDebtTotal" : currentsJPYDebtTotal,
                    "currentsJPYCreditTotal" : currentsJPYCreditTotal,
                    "currentsJPYBalanceTotal" : currentsJPYBalanceTotal,
                    "currentsCNYDebtTotal" : currentsCNYDebtTotal,
                    "currentsCNYCreditTotal" : currentsCNYCreditTotal,
                    "currentsCNYBalanceTotal" : currentsCNYBalanceTotal,
                    "currentsCADDebtTotal" : currentsCADDebtTotal,
                    "currentsCADCreditTotal" : currentsCADCreditTotal,
                    "currentsCADBalanceTotal" : currentsCADBalanceTotal,
                    "currentsTRYDebtTotal" : currentsTRYDebtTotal,
                    "currentsTRYCreditTotal" : currentsTRYCreditTotal,
                    "currentsTRYBalanceTotal" : currentsTRYBalanceTotal
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/soa_detail.html', context)
    
class SOAUpdateView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("SOA")
        elementTag = "soa"
        elementTagSub = "soaPart"
        elementTagId = id
        
        company = Company.objects.get(id = id)
        
        usd = Currency.objects.filter(code = "USD").first()
        eur = Currency.objects.filter(code = "EUR").first()
        gbp = Currency.objects.filter(code = "GBP").first()
        qar = Currency.objects.filter(code = "QAR").first()
        rub = Currency.objects.filter(code = "RUB").first()
        jpy = Currency.objects.filter(code = "JPY").first()
        
        #current-usd
        currentsUSD = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,currency = 106, company = company)
        currentsUSDDebtTotal = 0
        currentsUSDCreditTotal = 0
        currentsUSDBalanceTotal = 0
        for currentUSD in currentsUSD:
            currentsUSDDebtTotal = currentsUSDDebtTotal + currentUSD.debt
            currentsUSDCreditTotal = currentsUSDCreditTotal + currentUSD.credit
        currentsUSDBalanceTotal = currentsUSDDebtTotal - currentsUSDCreditTotal
        
        # Para miktarını belirtilen formatta gösterme
        currentsUSDDebtTotal = "{:,.2f}".format(round(currentsUSDDebtTotal,2))
        currentsUSDCreditTotal = "{:,.2f}".format(round(currentsUSDCreditTotal,2))
        currentsUSDBalanceTotal = "{:,.2f}".format(round(currentsUSDBalanceTotal,2))
        # Nokta ile virgülü değiştirme
        currentsUSDDebtTotal = currentsUSDDebtTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsUSDCreditTotal = currentsUSDCreditTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsUSDBalanceTotal = currentsUSDBalanceTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #current-eur
        currentsEUR = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,currency = 33, company = company)
        currentsEURDebtTotal = 0
        currentsEURCreditTotal = 0
        for currentEUR in currentsEUR:
            currentsEURDebtTotal = currentsEURDebtTotal + currentEUR.debt
            currentsEURCreditTotal = currentsEURCreditTotal + currentEUR.credit
        currentsEURBalanceTotal = currentsEURDebtTotal - currentsEURCreditTotal
        
        # Para miktarını belirtilen formatta gösterme
        currentsEURDebtTotal = "{:,.2f}".format(round(currentsEURDebtTotal,2))
        currentsEURCreditTotal = "{:,.2f}".format(round(currentsEURCreditTotal,2))
        currentsEURBalanceTotal = "{:,.2f}".format(round(currentsEURBalanceTotal,2))
        # Nokta ile virgülü değiştirme
        currentsEURDebtTotal = currentsEURDebtTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsEURCreditTotal = currentsEURCreditTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsEURBalanceTotal = currentsEURBalanceTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #current-gbp
        currentsGBP = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,currency = 105, company = company)
        currentsGBPDebtTotal = 0
        currentsGBPCreditTotal = 0
        for currentGBP in currentsGBP:
            currentsGBPDebtTotal = currentsGBPDebtTotal + currentGBP.debt
            currentsGBPCreditTotal = currentsGBPCreditTotal + currentGBP.credit
        currentsGBPBalanceTotal = currentsGBPDebtTotal - currentsGBPCreditTotal
        
        # Para miktarını belirtilen formatta gösterme
        currentsGBPDebtTotal = "{:,.2f}".format(round(currentsGBPDebtTotal,2))
        currentsGBPCreditTotal = "{:,.2f}".format(round(currentsGBPCreditTotal,2))
        currentsGBPBalanceTotal = "{:,.2f}".format(round(currentsGBPBalanceTotal,2))
        # Nokta ile virgülü değiştirme
        currentsGBPDebtTotal = currentsGBPDebtTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsGBPCreditTotal = currentsGBPCreditTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsGBPBalanceTotal = currentsGBPBalanceTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #current-qar
        currentsQAR = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,currency = 83, company = company)
        currentsQARDebtTotal = 0
        currentsQARCreditTotal = 0
        for currentQAR in currentsQAR:
            currentsQARDebtTotal = currentsQARDebtTotal + currentQAR.debt
            currentsQARCreditTotal = currentsQARCreditTotal + currentQAR.credit
        currentsQARBalanceTotal = currentsQARDebtTotal - currentsQARCreditTotal
        
        # Para miktarını belirtilen formatta gösterme
        currentsQARDebtTotal = "{:,.2f}".format(round(currentsQARDebtTotal,2))
        currentsQARCreditTotal = "{:,.2f}".format(round(currentsQARCreditTotal,2))
        currentsQARBalanceTotal = "{:,.2f}".format(round(currentsQARBalanceTotal,2))
        # Nokta ile virgülü değiştirme
        currentsQARDebtTotal = currentsQARDebtTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsQARCreditTotal = currentsQARCreditTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsQARBalanceTotal = currentsQARBalanceTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #current-qar
        currentsRUB = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,currency = 85, company = company)
        currentsRUBDebtTotal = 0
        currentsRUBCreditTotal = 0
        for currentRUB in currentsRUB:
            currentsRUBDebtTotal = currentsRUBDebtTotal + currentRUB.debt
            currentsRUBCreditTotal = currentsRUBCreditTotal + currentRUB.credit
        currentsRUBBalanceTotal = currentsRUBDebtTotal - currentsRUBCreditTotal
        
        # Para miktarını belirtilen formatta gösterme
        currentsRUBDebtTotal = "{:,.2f}".format(round(currentsRUBDebtTotal,2))
        currentsRUBCreditTotal = "{:,.2f}".format(round(currentsRUBCreditTotal,2))
        currentsRUBBalanceTotal = "{:,.2f}".format(round(currentsRUBBalanceTotal,2))
        # Nokta ile virgülü değiştirme
        currentsRUBDebtTotal = currentsRUBDebtTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsRUBCreditTotal = currentsRUBCreditTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsRUBBalanceTotal = currentsRUBBalanceTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #current-jpy
        currentsJPY = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,currency = 52, company = company)
        currentsJPYDebtTotal = 0
        currentsJPYCreditTotal = 0
        for currentJPY in currentsJPY:
            currentsJPYDebtTotal = currentsJPYDebtTotal + currentJPY.debt
            currentsJPYCreditTotal = currentsJPYCreditTotal + currentJPY.credit
        currentsJPYBalanceTotal = currentsJPYDebtTotal - currentsJPYCreditTotal
        
        # Para miktarını belirtilen formatta gösterme
        currentsJPYDebtTotal = "{:,.2f}".format(round(currentsJPYDebtTotal,2))
        currentsJPYCreditTotal = "{:,.2f}".format(round(currentsJPYCreditTotal,2))
        currentsJPYBalanceTotal = "{:,.2f}".format(round(currentsJPYBalanceTotal,2))
        # Nokta ile virgülü değiştirme
        currentsJPYDebtTotal = currentsJPYDebtTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsJPYCreditTotal = currentsJPYCreditTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsJPYBalanceTotal = currentsJPYBalanceTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #current-try
        currentsTRY = Current.objects.filter(sourceCompany = request.user.profile.sourceCompany,currency = 102, company = company)
        currentsTRYDebtTotal = 0
        currentsTRYCreditTotal = 0
        for currentTRY in currentsTRY:
            currentsTRYDebtTotal = currentsTRYDebtTotal + currentTRY.debt
            currentsTRYCreditTotal = currentsTRYCreditTotal + currentTRY.credit
        currentsTRYBalanceTotal = currentsTRYDebtTotal - currentsTRYCreditTotal
        
        # Para miktarını belirtilen formatta gösterme
        currentsTRYDebtTotal = "{:,.2f}".format(round(currentsTRYDebtTotal,2))
        currentsTRYCreditTotal = "{:,.2f}".format(round(currentsTRYCreditTotal,2))
        currentsTRYBalanceTotal = "{:,.2f}".format(round(currentsTRYBalanceTotal,2))
        # Nokta ile virgülü değiştirme
        currentsTRYDebtTotal = currentsTRYDebtTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsTRYCreditTotal = currentsTRYCreditTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        currentsTRYBalanceTotal = currentsTRYBalanceTotal.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        #soaPdff(company)
        soaPdfTask.delay(company.id, request.user.profile.sourceCompany.id)
        #soaIncomingPdf(company.id)
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub,
                    "elementTagId" : elementTagId,
                    "company" : company,
                    "usd" : usd,
                    "eur" : eur,
                    "gbp" : gbp,
                    "qar" : qar,
                    "rub" : rub,
                    "jpy" : jpy,
                    "currentsUSDDebtTotal" : currentsUSDDebtTotal,
                    "currentsUSDCreditTotal" : currentsUSDCreditTotal,
                    "currentsUSDBalanceTotal" : currentsUSDBalanceTotal,
                    "currentsEURDebtTotal" : currentsEURDebtTotal,
                    "currentsEURCreditTotal" : currentsEURCreditTotal,
                    "currentsEURBalanceTotal" : currentsEURBalanceTotal,
                    "currentsGBPDebtTotal" : currentsGBPDebtTotal,
                    "currentsGBPCreditTotal" : currentsGBPCreditTotal,
                    "currentsGBPBalanceTotal" : currentsGBPBalanceTotal,
                    "currentsQARDebtTotal" : currentsQARDebtTotal,
                    "currentsQARCreditTotal" : currentsQARCreditTotal,
                    "currentsQARBalanceTotal" : currentsQARBalanceTotal,
                    "currentsRUBDebtTotal" : currentsRUBDebtTotal,
                    "currentsRUBCreditTotal" : currentsRUBCreditTotal,
                    "currentsRUBBalanceTotal" : currentsRUBBalanceTotal,
                    "currentsJPYDebtTotal" : currentsJPYDebtTotal,
                    "currentsJPYCreditTotal" : currentsJPYCreditTotal,
                    "currentsJPYBalanceTotal" : currentsJPYBalanceTotal,
                    "currentsTRYDebtTotal" : currentsTRYDebtTotal,
                    "currentsTRYCreditTotal" : currentsTRYCreditTotal,
                    "currentsTRYBalanceTotal" : currentsTRYBalanceTotal
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'account/soa_detail.html', context)
    
class SOAPdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("SOA PDF")
        
        elementTag = "soa"
        elementTagSub = "soaPart"
        elementTagId = str(id) + "-pdf"
        
        company = get_object_or_404(Company, id = id)
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #orderConfirmationPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/soa_pdf.html', context)
    
class SOAIncomingPdfView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        tag = _("SOA Incoming PDF")
        
        elementTag = "soa"
        elementTagSub = "soaPart"
        elementTagId = str(id) + "-incoming-pdf"
        
        company = get_object_or_404(Company, id = id)
        
        characters = string.ascii_letters + string.digits
        version = ''.join(random.choice(characters) for _ in range(10))
        
        #orderConfirmationPdf(quotation)
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "company" : company,
                "version" : version
        }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")

        return render(request, 'account/soa_incoming_pdf.html', context)

