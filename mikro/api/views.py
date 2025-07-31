from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet
from django.http import JsonResponse
from django.views.generic.list import MultipleObjectMixin
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.views import APIView
from rest_framework_datatables.filters import DatatablesFilterBackend
#from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend as DFDatatablesFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet, EditorModelMixin
from rest_framework.viewsets import ModelViewSet

# from django_filters import FilterSet, ChoiceFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, ChoiceFilter, CharFilter, MultipleChoiceFilter
from drf_multiple_model.views import ObjectMultipleModelAPIView, FlatMultipleModelAPIView

from mikro.api.serializers import *

import os
import pyodbc
import json
import time
from datetime import datetime

import logging

from decouple import config, Csv

from dotenv import load_dotenv
load_dotenv()

class QueryListAPIView(generics.ListAPIView):
    def get_queryset(self):
        if self.request.GET.get('format', None) == 'datatables':
            self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend, SearchFilter)
            return super().get_queryset()
        queryset = self.queryset
        # check the start index is integer
        try:
            start = self.request.GET.get('start')
            start = int(start) if start else None
        # else make it None
        except ValueError:
            start = None

        # check the end index is integer
        try:
            end = self.request.GET.get('end')
            end = int(end) if end else None
        # else make it None
        except ValueError:
            end = None

        # skip filters and sorting if they are not exists in the model to ensure security
        accepted_filters = {}
        # loop fields of the model
        for field in queryset.model._meta.get_fields():
            # if field exists in request, accept it
            if field.name in dict(self.request.GET):
                accepted_filters[field.name] = dict(self.request.GET)[field.name]
            # if field exists in sorting parameter's value, accept it

        filters = {}

        for key, value in accepted_filters.items():
            if any(val in value for val in EMPTY_VALUES):
                if queryset.model._meta.get_field(key).null:
                    filters[key + '__isnull'] = True
                else:
                    filters[key + '__exact'] = ''
            else:
                filters[key + '__in'] = value
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all().filter(**filters)[start:end]
        return queryset

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            elif self.request.GET.get('format', None) == 'datatables':
                self._paginator = self.pagination_class()
            else:
                self._paginator = None
        return self._paginator
  

class KullanicilarList(generics.ListAPIView):
    serializer_class = KullanicilarListSerializer
    queryset = []
    
    def list(self, request, *args, **kwargs):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        
        logger = logging.getLogger("django")
        try:
            conn = pyodbc.connect(connectionString)
        
            tabloGoruntulemeDetay = """
            SELECT User_name, User_LongName FROM KULLANICILAR;
            """

            SQL_QUERY = tabloGoruntulemeDetay

            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)

            records = cursor.fetchall()
            for r in records:
                row_to_list = [elem for elem in r]
            
            external_data = []
            id = 1
            
            for r in records:
                row_to_list = [elem for elem in r]
                external_data.append({
                    "id" : id,
                    "username" : row_to_list[0],
                    "name" : row_to_list[1]
                })
                
                id = id + 1
        except Exception as e:
            logger.exception(e)
            external_data = []
        
        data_format = request.query_params.get('format', None)
        
        if data_format == 'datatables':
            filter_backends = (DatatablesFilterBackend)
            data = {
                "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
                "recordsTotal": len(external_data),  # Toplam kayıt sayısı
                "recordsFiltered": len(external_data),  # Filtre sonrası kayıt sayısı
                "data": external_data  # Gösterilecek veri
            }
            
            return Response(data)
        
        serializer = self.get_serializer(external_data, many=True)
        return Response(serializer.data)
    
    # def get_queryset(self):
    #     if self.request.GET.get('format', None) == 'datatables':
    #         self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend, SearchFilter)
    #         return super().get_queryset()
    #     queryset = self.queryset
    
class StokBirimleriList(generics.ListAPIView):
    serializer_class = StokBirimleriListSerializer
    queryset = []
    
    def list(self, request, *args, **kwargs):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        logger = logging.getLogger("django")
        try:
            conn = pyodbc.connect(connectionString)
            
            tabloGoruntulemeDetay = """
            SELECT unit_ismi FROM STOK_BIRIMLERI;
            """

            SQL_QUERY = tabloGoruntulemeDetay

            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)

            records = cursor.fetchall()
            for r in records:
                row_to_list = [elem for elem in r]
            
            external_data = []
            id = 1
            
            for r in records:
                row_to_list = [elem for elem in r]
                external_data.append({
                    "id" : id,
                    "unit" : row_to_list[0]
                })
                
                id = id + 1
        except Exception as e:
            logger.exception(e)
            external_data = []
        
        data_format = request.query_params.get('format', None)
        
        if data_format == 'datatables':
            filter_backends = (DatatablesFilterBackend)
            data = {
                "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
                "recordsTotal": len(external_data),  # Toplam kayıt sayısı
                "recordsFiltered": len(external_data),  # Filtre sonrası kayıt sayısı
                "data": external_data  # Gösterilecek veri
            }
            
            return Response(data)
        
        serializer = self.get_serializer(external_data, many=True)
        return Response(serializer.data)
    
    # def get_queryset(self):
    #     if self.request.GET.get('format', None) == 'datatables':
    #         self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend, SearchFilter)
    #         return super().get_queryset()
    #     queryset = self.queryset

class KurIsimleriList(generics.ListAPIView):
    serializer_class = KurIsimleriListSerializer
    queryset = []
    
    def list(self, request, *args, **kwargs):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        logger = logging.getLogger("django")
        try:
            conn = pyodbc.connect(connectionString)
            
            tabloGoruntulemeDetay = """
            SELECT Kur_adi,Kur_No,Kur_sembol
            FROM KUR_ISIMLERI
            ORDER BY Kur_sembol ASC;
            """

            SQL_QUERY = tabloGoruntulemeDetay

            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)

            records = cursor.fetchall()
            for r in records:
                row_to_list = [elem for elem in r]
            
            external_data = []
            id = 1
            
            for r in records:
                row_to_list = [elem for elem in r]
                external_data.append({
                    "id" : id,
                    "kurNo" : r.Kur_No,
                    "kurAdi" : r.Kur_adi,
                    "kurSembol" : r.Kur_sembol
                })
                
                id = id + 1
        except Exception as e:
            logger.exception(e)
            external_data = []
        
        data_format = request.query_params.get('format', None)
        
        if data_format == 'datatables':
            filter_backends = (DatatablesFilterBackend)
            data = {
                "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
                "recordsTotal": len(external_data),  # Toplam kayıt sayısı
                "recordsFiltered": len(external_data),  # Filtre sonrası kayıt sayısı
                "data": external_data  # Gösterilecek veri
            }
            
            return Response(data)
        
        serializer = self.get_serializer(external_data, many=True)
        return Response(serializer.data)

class CariHesaplarList(generics.ListAPIView):
    serializer_class = CariHesaplarListSerializer
    queryset = []
    
    def list(self, request, *args, **kwargs):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = self.request.user.profile.sourceCompany.mikroDBName
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        logger = logging.getLogger("django")
        try:
            conn = pyodbc.connect(connectionString)
        
            tabloGoruntulemeDetay = """
            SELECT cari_kod, cari_unvan1, cari_unvan2,
            cari_vdaire_adi, cari_vdaire_no, cari_fatura_adres_no,
            cari_doviz_cinsi,cari_doviz_cinsi1,cari_doviz_cinsi2
            FROM CARI_HESAPLAR;
            """

            SQL_QUERY = tabloGoruntulemeDetay

            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)

            records = cursor.fetchall()
            for r in records:
                row_to_list = [elem for elem in r]
            
            external_data = []
            id = 1
            
            #####Adres Getir#####
            try:
                DATABASE = self.request.user.profile.sourceCompany.mikroDBName
                connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
                conn = pyodbc.connect(connectionString)
                SQL_QUERY_EVRAK_TIP = """
                SELECT adr_cari_kod, adr_ulke, adr_il, adr_cadde, adr_sokak FROM CARI_HESAP_ADRESLERI;
                """
                cursor = conn.cursor()
                cursor.execute(SQL_QUERY_EVRAK_TIP)
                adresRecords = cursor.fetchall()
                adresDict = {}
                for adresRecord in adresRecords:
                    row_to_list_adres = [elem for elem in adresRecord]
                    adresDict[str(row_to_list_adres[0])+"-ulke"] = row_to_list_adres[1]
                    adresDict[str(row_to_list_adres[0])+"-sehir"] = row_to_list_adres[2]
                    adresDict[str(row_to_list_adres[0])+"-adres"] = row_to_list_adres[3] + " " + row_to_list_adres[4]
            except Exception as e:
                logger.exception(e)
                adresDict = {}
            #####Adres Getir-end#####
            
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
                row_to_list = [elem for elem in r]
                external_data.append({
                    "id" : id,
                    "kod" : row_to_list[0],
                    "unvan1" : row_to_list[1],
                    "unvan2" : row_to_list[2],
                    "vDaireAdi" : row_to_list[3],
                    "vDaireNo" : row_to_list[4],
                    "ulke" : adresDict.get(str(row_to_list[0])+"-ulke"),
                    "sehir" : adresDict.get(str(row_to_list[0])+"-sehir"),
                    "adres" : adresDict.get(str(row_to_list[0])+"-adres"),
                    "doviz" : dovizDict.get(str(row_to_list[6])),
                    "doviz1" : dovizDict.get(str(row_to_list[7])),
                    "doviz2" : dovizDict.get(str(row_to_list[8])),
                })
                
                id = id + 1
        except Exception as e:
            logger.exception(e)
            external_data = []
        
        data_format = request.query_params.get('format', None)
        
        if data_format == 'datatables':
            filter_backends = (DatatablesFilterBackend)
            data = {
                "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
                "recordsTotal": len(external_data),  # Toplam kayıt sayısı
                "recordsFiltered": len(external_data),  # Filtre sonrası kayıt sayısı
                "data": external_data  # Gösterilecek veri
            }
            
            return Response(data)
        serializer = self.get_serializer(external_data, many=True)
        return Response(serializer.data)
    
    # def get_queryset(self):
    #     if self.request.GET.get('format', None) == 'datatables':
    #         self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend, SearchFilter)
    #         return super().get_queryset()
    #     queryset = self.queryset

class CariHesapAdresleriList(generics.ListAPIView):
    serializer_class = CariHesapAdresleriListSerializer
    queryset = []
    
    def list(self, request, *args, **kwargs):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = self.request.user.profile.sourceCompany.mikroDBName
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        logger = logging.getLogger("django")
        try:
            conn = pyodbc.connect(connectionString)
        
            tabloGoruntulemeDetay = """
            SELECT adr_cari_kod,adr_mahalle,adr_cadde,adr_sokak,adr_ilce,adr_il,adr_ulke,adr_posta_kodu
            FROM CARI_HESAP_ADRESLERI;
            """

            SQL_QUERY = tabloGoruntulemeDetay

            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)

            records = cursor.fetchall()
            for r in records:
                row_to_list = [elem for elem in r]
            
            external_data = []
            id = 1
            
            for r in records:
                row_to_list = [elem for elem in r]
                external_data.append({
                    "id" : id,
                    "kod" : r.adr_cari_kod,
                    "mahalle" : r.adr_mahalle,
                    "cadde" : r.adr_cadde,
                    "sokak" : r.adr_sokak,
                    "postaKodu" : r.adr_posta_kodu,
                    "ilce" : r.adr_ilce,
                    "il" : r.adr_il,
                    "ulke" : r.adr_ulke,
                })
                
                id = id + 1
        except Exception as e:
            logger.exception(e)
            external_data = []
        
        data_format = request.query_params.get('format', None)
        
        if data_format == 'datatables':
            filter_backends = (DatatablesFilterBackend)
            data = {
                "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
                "recordsTotal": len(external_data),  # Toplam kayıt sayısı
                "recordsFiltered": len(external_data),  # Filtre sonrası kayıt sayısı
                "data": external_data  # Gösterilecek veri
            }
            
            return Response(data)
        serializer = self.get_serializer(external_data, many=True)
        return Response(serializer.data)
    
    # def get_queryset(self):
    #     if self.request.GET.get('format', None) == 'datatables':
    #         self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend, SearchFilter)
    #         return super().get_queryset()
    #     queryset = self.queryset


# class CariHesapHareketleriList(generics.ListAPIView):
#     serializer_class = CariHesapHareketleriListSerializer
#     pagination_class = PageNumberPagination
#     queryset = []
    
#     def list(self, request, *args, **kwargs):
#         SERVER = os.getenv("MIKRO_SERVER","")
#         DATABASE = "MikroDB_V16_ESMS"
#         USERNAME = os.getenv("MIKRO_USERNAME","")
#         PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
#         connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
#         logger = logging.getLogger("django")
#         try:
#             conn = pyodbc.connect(connectionString)
            
#             SQL_QUERY = """
#             SELECT cha_create_date,cha_kod,cha_evrak_tip,cha_belge_no,cha_d_cins,cha_meblag,cha_aratoplam,cha_ft_iskonto1,cha_ft_iskonto2,cha_ft_iskonto3,
#             cha_ft_iskonto4,cha_ft_iskonto5,cha_ft_iskonto6,cha_vergi1,cha_vergi2,cha_vergi3,cha_vergi4,cha_vergi5,cha_vergi6,cha_vergi7,cha_vergi8,cha_vergi9,
#             cha_vergi10
#             FROM CARI_HESAP_HAREKETLERI
#             WHERE cha_evrak_tip = 0 OR cha_evrak_tip = 63
#             ORDER BY cha_create_date DESC;
#             """

#             cursor = conn.cursor()
#             cursor.execute(SQL_QUERY)
            
#             records = cursor.fetchall()
#             # for r in records:
                
#             #     row_to_list = [elem for elem in r]
            
#             external_data = []
            
#             id = 1
            
#             #####Cari Getir#####
#             try:
#                 DATABASE = "MikroDB_V16_ESMS"
#                 connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
#                 conn = pyodbc.connect(connectionString)
#                 SQL_QUERY_CARI = """
#                 SELECT cari_kod,cari_unvan1 FROM CARI_HESAPLAR;
#                 """
#                 cursor = conn.cursor()
#                 cursor.execute(SQL_QUERY_CARI)
#                 cariRecords = cursor.fetchall()
#                 cariDict = {}
#                 for cariRecord in cariRecords:
#                     row_to_list_evrak_tip = [elem for elem in cariRecord]
#                     cariDict[str(row_to_list_evrak_tip[0])] = row_to_list_evrak_tip[1]
#             except Exception as e:
#                 logger.exception(e)
#                 cariDict = {}
#             #####Cari Getir-end#####
            
#             #####Evrak Tip Getir#####
#             try:
#                 DATABASE = "MikroDB_V16"
#                 connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
#                 conn = pyodbc.connect(connectionString)
#                 SQL_QUERY_EVRAK_TIP = """
#                 SELECT yit_sub_id, yit_isim2 FROM YARDIMCI_ISIM_TABLOSU
#                 WHERE yit_language = 'T' AND yit_tip_no = 0;
#                 """
#                 cursor = conn.cursor()
#                 cursor.execute(SQL_QUERY_EVRAK_TIP)
#                 evrakTipRecords = cursor.fetchall()
#                 evrakTipDict = {}
#                 for evrakTipRecord in evrakTipRecords:
#                     row_to_list_evrak_tip = [elem for elem in evrakTipRecord]
#                     evrakTipDict[str(row_to_list_evrak_tip[0])] = row_to_list_evrak_tip[1]
#             except Exception as e:
#                 logger.exception(e)
#                 evrakTipDict = {}
#             #####Evrak Tip Getir-end#####
            
#             #####Doviz Getir#####
#             try:
#                 DATABASE = "MikroDB_V16"
#                 connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
#                 conn = pyodbc.connect(connectionString)
#                 SQL_QUERY_EVRAK_TIP = """
#                 SELECT Kur_No, Kur_sembol FROM KUR_ISIMLERI;
#                 """
#                 cursor = conn.cursor()
#                 cursor.execute(SQL_QUERY_EVRAK_TIP)
#                 dovizRecords = cursor.fetchall()
#                 dovizDict = {}
#                 for dovizRecord in dovizRecords:
#                     row_to_list_doviz = [elem for elem in dovizRecord]
#                     dovizDict[str(row_to_list_doviz[0])] = row_to_list_doviz[1]
#             except Exception as e:
#                 logger.exception(e)
#                 dovizDict = {}
#             #####Doviz Getir-end#####
            
#             evrakTipJSON = open("mikro/fixtures/evrak_tip.json")
#             evrakTip = json.load(evrakTipJSON)
            
#             for r in records:
#                 row_to_list = [elem for elem in r]
                
#                 iskonto = r.cha_ft_iskonto1 + r.cha_ft_iskonto2 + r.cha_ft_iskonto3 + r.cha_ft_iskonto4 + r.cha_ft_iskonto5 + r.cha_ft_iskonto6
#                 vergi = r.cha_vergi1 + r.cha_vergi2 + r.cha_vergi3 + r.cha_vergi4 + r.cha_vergi5 + r.cha_vergi6 + r.cha_vergi7 + r.cha_vergi8 + r.cha_vergi9 + r.cha_vergi10
                
#                 external_data.append({
#                     "id" : id,
#                     "tarih" : r.cha_create_date.strftime("%d.%m.%Y %H:%M:%S"),
#                     "kod" : r.cha_kod,
#                     "cari" : cariDict.get(str(r.cha_kod)),
#                     "evrakTip" : evrakTipDict.get(str(r.cha_evrak_tip)),
#                     "belgeNo" : r.cha_belge_no,
#                     "doviz" : dovizDict.get(str(r.cha_d_cins)),
#                     "meblag" : r.cha_meblag,
#                     "araToplam" : r.cha_aratoplam,
#                     "iskonto" : iskonto,
#                     "vergi" : vergi,
#                 })
                
#                 id = id + 1
#         except Exception as e:
#             logger.exception(e)
#             external_data = []
        
#         data_format = request.query_params.get('format', None)
        
#         if data_format == 'datatables':
#             filter_backends = (DatatablesFilterBackend)
#             data = {
#                 "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
#                 "recordsTotal": len(external_data),  # Toplam kayıt sayısı
#                 "recordsFiltered": len(external_data),  # Filtre sonrası kayıt sayısı
#                 "data": external_data  # Gösterilecek veri
#             }
            
#             return Response(data)
#         serializer = self.get_serializer(external_data, many=True)
#         return Response(serializer.data)

class CariHesapHareketleriList(EditorModelMixin, ModelViewSet, QueryListAPIView):
    """
    Returns all cities
    Use GET parameters to filter queryset
    """
    
    serializer_class = CariHesapHareketleriListSerializer
    filter_backends = [OrderingFilter,DjangoFilterBackend,SearchFilter]
    filterset_fields = {
                        'cari': ['exact','in', 'isnull']
    }
    search_fields = ['cari']
    ordering_fields = '__all__'
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """
        Optionally restricts the returned requests to a given user,
        by filtering against a `username` query parameter in the URL.
        """

        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = self.request.user.profile.sourceCompany.mikroDBName
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        logger = logging.getLogger("django")
        try:
            conn = pyodbc.connect(connectionString)
            
            SQL_QUERY = """
            SELECT cha_create_date,cha_kod,cha_evrak_tip,cha_belge_no,cha_d_cins,cha_meblag,cha_aratoplam,cha_ft_iskonto1,cha_ft_iskonto2,cha_ft_iskonto3,
            cha_ft_iskonto4,cha_ft_iskonto5,cha_ft_iskonto6,cha_vergi1,cha_vergi2,cha_vergi3,cha_vergi4,cha_vergi5,cha_vergi6,cha_vergi7,cha_vergi8,
            cha_vergi9,cha_vergi10,cha_d_kur,cha_projekodu
            FROM CARI_HESAP_HAREKETLERI
            WHERE cha_evrak_tip = 0 OR cha_evrak_tip = 63
            ORDER BY cha_create_date DESC;
            """

            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)
            
            records = cursor.fetchall()
            # for r in records:
                
            #     row_to_list = [elem for elem in r]
            
            external_data = []
            
            id = 1
            
            #####Cari Getir#####
            try:
                DATABASE = self.request.user.profile.sourceCompany.mikroDBName
                connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
                conn = pyodbc.connect(connectionString)
                SQL_QUERY_CARI = """
                SELECT cari_kod,cari_unvan1 FROM CARI_HESAPLAR;
                """
                cursor = conn.cursor()
                cursor.execute(SQL_QUERY_CARI)
                cariRecords = cursor.fetchall()
                cariDict = {}
                for cariRecord in cariRecords:
                    row_to_list_evrak_tip = [elem for elem in cariRecord]
                    cariDict[str(row_to_list_evrak_tip[0])] = row_to_list_evrak_tip[1]
            except Exception as e:
                logger.exception(e)
                cariDict = {}
            #####Cari Getir-end#####
            
            #####Evrak Tip Getir#####
            try:
                DATABASE = "MikroDB_V16"
                connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
                conn = pyodbc.connect(connectionString)
                SQL_QUERY_EVRAK_TIP = """
                SELECT yit_sub_id, yit_isim2 FROM YARDIMCI_ISIM_TABLOSU
                WHERE yit_language = 'T' AND yit_tip_no = 0;
                """
                cursor = conn.cursor()
                cursor.execute(SQL_QUERY_EVRAK_TIP)
                evrakTipRecords = cursor.fetchall()
                evrakTipDict = {}
                for evrakTipRecord in evrakTipRecords:
                    row_to_list_evrak_tip = [elem for elem in evrakTipRecord]
                    evrakTipDict[str(row_to_list_evrak_tip[0])] = row_to_list_evrak_tip[1]
            except Exception as e:
                logger.exception(e)
                evrakTipDict = {}
            #####Evrak Tip Getir-end#####
            
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
            
            evrakTipJSON = open("mikro/fixtures/evrak_tip.json")
            evrakTip = json.load(evrakTipJSON)
            
            for r in records:
                row_to_list = [elem for elem in r]
                
                iskonto = sum([r.cha_ft_iskonto1,r.cha_ft_iskonto2,r.cha_ft_iskonto3,r.cha_ft_iskonto4,r.cha_ft_iskonto5,r.cha_ft_iskonto6])
                vergi = sum([r.cha_vergi1,r.cha_vergi2,r.cha_vergi3,r.cha_vergi4,r.cha_vergi5,r.cha_vergi6,r.cha_vergi7,r.cha_vergi8,r.cha_vergi9,r.cha_vergi10])
                
                external_data.append({
                    "id" : id,
                    "tarih" : r.cha_create_date.strftime("%d.%m.%Y %H:%M:%S"),
                    "kod" : r.cha_kod,
                    "cari" : cariDict.get(str(r.cha_kod)),
                    "evrakTip" : evrakTipDict.get(str(r.cha_evrak_tip)),
                    "belgeNo" : r.cha_belge_no,
                    "doviz" : dovizDict.get(str(r.cha_d_cins)),
                    "meblag" : r.cha_meblag,
                    "araToplam" : r.cha_aratoplam,
                    "iskonto" : iskonto,
                    "vergi" : vergi,
                    "kur" : r.cha_d_kur,
                    "proje" : r.cha_projekodu,
                })
                
                id = id + 1
            return external_data
        except Exception as e:
            logger.exception(e)
            return []
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        query = request.query_params.get('search[value]', None)
        
        if query:
            queryset = [item for item in queryset if item['cari'] and query.lower() in item['cari'].lower()]
            #queryset = [item for item in queryset if query.lower() in item['cari'].lower()]

        
        
        data_format = request.query_params.get('format', None)
        
        if data_format == 'datatables':
            draw = int(request.GET.get('draw', 1))
            start = int(request.GET.get('start', 0))
            length = int(request.GET.get('length', 200))

            filtered_data = queryset[start:start+length]
            
            data = {
                "draw": draw,
                "recordsTotal": len(queryset),
                "recordsFiltered": len(queryset),
                "data": filtered_data
            }
            
            return Response(data)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
   

class StoklarList(generics.ListAPIView):
    serializer_class = CariHesaplarListSerializer
    queryset = []
    
    def list(self, request, *args, **kwargs):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = self.request.user.profile.sourceCompany.mikroDBName
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        logger = logging.getLogger("django")
        try:
            conn = pyodbc.connect(connectionString)
        
            tabloGoruntulemeDetay = """
            SELECT sto_kod,sto_isim,sto_yabanci_isim,sto_kisa_ismi,sto_birim1_ad FROM STOKLAR;
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
                row_to_list = [elem for elem in r]
                external_data.append({
                    "id" : id,
                    "kod" : row_to_list[0],
                    "isim" : row_to_list[1],
                    "yabanci_isim" : row_to_list[2],
                    "kisa_ismi" : row_to_list[3],
                    "birim1_ad" : row_to_list[4]
                })
                
                id = id + 1
        except Exception as e:
            logger.exception(e)
            external_data = []
        
        data_format = request.query_params.get('format', None)
        
        if data_format == 'datatables':
            filter_backends = (DatatablesFilterBackend)
            data = {
                "draw": int(self.request.GET.get('draw', 1)),  # Müşteri tarafından gönderilen çizim sayısı
                "recordsTotal": len(external_data),  # Toplam kayıt sayısı
                "recordsFiltered": len(external_data),  # Filtre sonrası kayıt sayısı
                "data": external_data  # Gösterilecek veri
            }
            
            return Response(data)
        serializer = self.get_serializer(external_data, many=True)
        return Response(serializer.data)
    
    # def get_queryset(self):
    #     if self.request.GET.get('format', None) == 'datatables':
    #         self.filter_backends = (OrderingFilter, DatatablesFilterBackend, DjangoFilterBackend, SearchFilter)
    #         return super().get_queryset()
    #     queryset = self.queryset
