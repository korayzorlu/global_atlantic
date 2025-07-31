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

import os
import pyodbc
import logging

from .forms import *
from .tasks import *
from .pdfs import *

class KullanicilarDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Kullanıcılar")
        elementTag = "kullanicilar"
        elementTagSub = "kullanicilarPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'mikro/kullanicilar/kullanicilar.html', context)


class StokBirimleriDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Stok Birimleri")
        elementTag = "stokBirimleri"
        elementTagSub = "stokBirimleriPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'mikro/stok_birimleri/stok_birimleri.html', context)

class KurIsimleriDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Kur İsimleri")
        elementTag = "kurIsimleri"
        elementTagSub = "kurIsimleriPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'mikro/kur_isimleri/kur_isimleri.html', context)
   

class CariHesaplarDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Cari Hesaplar")
        elementTag = "cariHesaplar"
        elementTagSub = "cariHesaplarPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'mikro/cari_hesaplar/cari_hesaplar.html', context)

class CariHesaplarUpdateView(LoginRequiredMixin, View):
    def get(self, request, cariKod, *args, **kwargs):
        tag = _("Cari Hesaplar Detail")
        elementTag = "cariHesaplar"
        elementTagSub = "cariHesaplarPart"
        elementTagId = cariKod
        
        cariKod = cariKod.replace("_",".")
        
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = request.user.profile.sourceCompany.mikroDBName
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        logger = logging.getLogger("django")
        try:
            conn = pyodbc.connect(connectionString)
        
            tabloGoruntulemeDetay = f"""
            SELECT cari_kod,cari_unvan1,cari_unvan2,cari_hareket_tipi,cari_baglanti_tipi,cari_BagliOrtaklisa_Firma,cari_doviz_cinsi,cari_doviz_cinsi1,
            cari_doviz_cinsi2,cari_muh_kod,cari_muh_kod1,cari_muh_kod2,cari_Ana_cari_kodu,cari_temsilci_kodu,cari_grup_kodu,cari_sektor_kodu,cari_bolge_kodu,
            cari_VergiKimlikNo,cari_vdaire_no,cari_vdaire_adi
            FROM CARI_HESAPLAR
            WHERE cari_kod = '{cariKod}';
            """

            SQL_QUERY = tabloGoruntulemeDetay

            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)

            records = cursor.fetchall()
            for r in records:
                row_to_list = [elem for elem in r]
            
            external_data = []
            id = 1
            
            #####Doviz Getir#####
            try:
                DATABASE = "MikroDB_V16"
                connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
                conn = pyodbc.connect(connectionString)
                SQL_QUERY_EVRAK_TIP = """
                SELECT Kur_No, Kur_sembol FROM KUR_ISIMLERI;
                """
                cursor = conn.cursor()
                cursor.execute(SQL_QUERY_EVRAK_TIP)
                dovizRecords = cursor.fetchall()
                dovizDict = {}
                for dovizRecord in dovizRecords:
                    row_to_list_doviz = [elem for elem in dovizRecord]
                    dovizDict[str(row_to_list_doviz[0])] = row_to_list_doviz[1]
            except Exception as e:
                logger.exception(e)
                dovizDict = {}
            #####Doviz Getir-end#####
            
            for r in records:
                hareketTipi = {"0":"Mal ve Hizmet Alınır ve Satılır",
                               "1":"Mal ve Hizmet Sadece Satılır",
                               "2":"Mal ve Hizmet Sadece Alınır",
                               "3":"Sadece Parasal Hareket Yapılır",
                               "4":"Cari Hareket Yapılmaz"
                               }
                baglantiTipi = {"0":"Müşteri",
                               "1":"Satıcı",
                               "2":"Diğer Cari",
                               "3":"Dağıtıcı",
                               "4":"Bayi",
                               "5":"Hedef Müşteri",
                               "6":"Hedef Bayi",
                               "7":"Alt Bayi",
                               "8":"Bağlı Ortaklık"
                               }
                
                if r.cari_hareket_tipi:
                    hareketTipi = hareketTipi[str(r.cari_hareket_tipi)]
                else:
                    hareketTipi = ""
                    
                if r.cari_baglanti_tipi:
                    baglantiTipi = baglantiTipi[str(r.cari_baglanti_tipi)]
                else:
                    baglantiTipi = ""
                
                external_data.append({
                    "id" : id,
                    "kod" : r.cari_kod,
                    "unvan1" : r.cari_unvan1,
                    "unvan2" : r.cari_unvan2,
                    "hareketTipi" : hareketTipi,
                    "baglantiTipi" : baglantiTipi,
                    "bagliOrtakliFirmaNo" : r.cari_BagliOrtaklisa_Firma,
                    "doviz" : dovizDict.get(str(r.cari_doviz_cinsi)),
                    "doviz1" : dovizDict.get(str(r.cari_doviz_cinsi1)),
                    "doviz2" : dovizDict.get(str(r.cari_doviz_cinsi2)),
                    "muhasebeKodu" : r.cari_muh_kod,
                    "muhasebeKodu1" : r.cari_muh_kod1,
                    "muhasebeKodu2" : r.cari_muh_kod2,
                    "anaCariKodu" : r.cari_Ana_cari_kodu,
                    "temsilciKodu" : r.cari_temsilci_kodu,
                    "grupKodu" : r.cari_grup_kodu,
                    "sektorKodu" : r.cari_sektor_kodu,
                    "bolgeKodu" : r.cari_bolge_kodu,
                    "vkn" : r.cari_VergiKimlikNo,
                    "vergiDairesiNo" : r.cari_vdaire_no,
                    "vergiDairesiAdi" : r.cari_vdaire_adi,
                })
                
                id = id + 1
        except Exception as e:
            logger.exception(e)
            external_data = []
        
        cari = external_data[0]
        
        context = {
                "tag": tag,
                "elementTag" : elementTag,
                "elementTagSub" : elementTagSub,
                "elementTagId" : elementTagId,
                "cari" : cari,
                "sessionKey" : request.session.session_key,
                "user" : request.user,
        }
        return render(request, 'mikro/cari_hesaplar/cari_hesaplar_detail.html', context)


class CariHesapAdresleriDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Cari Hesap Adresleri")
        elementTag = "cariHesapAdresleri"
        elementTagSub = "cariHesapAdresleriPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'mikro/cari_hesap_adresleri/cari_hesap_adresleri.html', context)
  
 
class CariHesapHareketleriDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Cari Hesap Hareketleri")
        elementTag = "cariHesapHareketleri"
        elementTagSub = "cariHesapHareketleriPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'mikro/cari_hesap_hareketleri/cari_hesap_hareketleri.html', context)

class StoklarDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        tag = _("Stoklar")
        elementTag = "stoklar"
        elementTagSub = "stoklarPart"
        
        context = {
                    "tag" : tag,
                    "elementTag" : elementTag,
                    "elementTagSub" : elementTagSub
            }
        
        #sayfa yenildendiğinde html bozukluğunun önüne geçmek için doğrudan dashboard'a gider.
        refererPath = urlparse(request.META.get("HTTP_REFERER")).path
        if str(refererPath) == "b''":
            return redirect("/user/")
        
        return render(request, 'mikro/stoklar/stoklar.html', context)