from django.utils.translation import gettext as _

import os
import pyodbc
import logging
import icu

from card.models import Company, Billing, Currency, City, Country
from card.utils import *

#####company#####
def company_update_from(data):
        companyId = data["id"]
        
        company = Company.objects.filter(id=int(companyId)).first()
        company.name = data["name"]
        availableCurrencies = ["0","1","2","8","12","121","123"]
        currencyDict = {"0" : 102, "1" : 106, "2" : 33, "8" : 52, "121" : 83, "123" : 85}
        if str(data["doviz"]) in availableCurrencies:
            currency = Currency.objects.select_related().filter(id = currencyDict[str(data["doviz"])]).first()
            company.currency = currency
        if str(data["doviz1"]) in availableCurrencies:
            currency2 = Currency.objects.select_related().filter(id = currencyDict[str(data["doviz1"])]).first()
            company.currency2 = currency2
        if str(data["doviz2"]) in availableCurrencies:
            currency3 = Currency.objects.select_related().filter(id = currencyDict[str(data["doviz2"])]).first()
            company.currency3 = currency3
        company.address = data["adres"]
        
        sehir = locale_lower(data["sehir"], 'tr_TR')
        if isinstance(sehir, icu.UnicodeString):
            sehir = str(sehir[1:])

        ulke = locale_lower(data["ulke"], 'tr_TR')
        if isinstance(ulke, icu.UnicodeString):
            ulke = str(ulke[1:])

        city = City.objects.filter(name__icontains = sehir).first()
        country = Country.objects.filter(formal_name__icontains = ulke).first()

        if city:
            company.city = city

        if country:
            company.country = country
        
        company.save()
#####company-end#####

#####billing#####
def billing_update_from(data):
        billingId = data["id"]
        
        billing = Billing.objects.filter(id=int(billingId)).first()
        billing.name = data["name"]
        availableCurrencies = ["0","1","2","8","12","121","123"]
        currencyDict = {"0" : 102, "1" : 106, "2" : 33, "8" : 52, "121" : 83, "123" : 85}
        if str(data["doviz"]) in availableCurrencies:
            currency = Currency.objects.select_related().filter(id = currencyDict[str(data["doviz"])]).first()
            billing.currency = currency
        if str(data["doviz1"]) in availableCurrencies:
            currency2 = Currency.objects.select_related().filter(id = currencyDict[str(data["doviz1"])]).first()
            billing.currency2 = currency2
        if str(data["doviz2"]) in availableCurrencies:
            currency3 = Currency.objects.select_related().filter(id = currencyDict[str(data["doviz2"])]).first()
            billing.currency3 = currency3
        billing.address = data["adres"]
        billing.save()
#####billing-end#####

def update_from_mikro(event):
    SERVER = os.getenv("MIKRO_SERVER","")
    DATABASE = event["message"]["mikroDBName"]
    USERNAME = os.getenv("MIKRO_USERNAME","")
    PASSWORD = os.getenv("MIKRO_PASSWORD","")
    
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
    logger = logging.getLogger("django")
    
    cariKod = event["message"]["cariKod"]
    cariName = event["message"]["cariName"]
    companyId = event["message"]["companyId"]
    try:
        with pyodbc.connect(connectionString, timeout = 5) as conn:
            
            tabloGoruntulemeDetay = f"""
            SELECT cari_kod,cari_unvan1,cari_Guid,cari_doviz_cinsi,cari_doviz_cinsi1,cari_doviz_cinsi2
            FROM CARI_HESAPLAR
            WHERE cari_kod = '{cariKod}';
            """

            SQL_QUERY = tabloGoruntulemeDetay
                
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)

            records = cursor.fetchall()
            row_to_list = []
            for r in records:
                row_to_list = [elem for elem in r]
            
            external_data = []
            
            #####Adres Getir#####
            try:
                DATABASE = event["message"]["mikroDBName"]
                connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
                conn = pyodbc.connect(connectionString)
                SQL_QUERY_EVRAK_TIP = """
                SELECT adr_cari_kod, adr_ulke, adr_il, adr_cadde, adr_sokak
                FROM CARI_HESAP_ADRESLERI;
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
            
            for r in records:
                
                external_data.append({
                    "id" : companyId,
                    "kod" : r.cari_kod,
                    "name" : r.cari_unvan1,
                    "guid" : r.cari_Guid,
                    "doviz" : r.cari_doviz_cinsi,
                    "doviz1" : r.cari_doviz_cinsi1,
                    "doviz2" : r.cari_doviz_cinsi2,
                    "adres" : adresDict.get(str(r.cari_kod)+"-adres"),
                    "sehir" : adresDict.get(str(r.cari_kod)+"-sehir"),
                    "ulke" : adresDict.get(str(r.cari_kod)+"-ulke"),
                })
            response = {"status" : "success", "data" : external_data[0]}
            
            return response
        
    except Exception as e:
        response = {"status" : "fail", "data" : {}}
            
        return response
    
def update_to_mikro(event):
    SERVER = os.getenv("MIKRO_SERVER","")
    DATABASE = event["message"]["mikroDBName"]
    USERNAME = os.getenv("MIKRO_USERNAME","")
    PASSWORD = os.getenv("MIKRO_PASSWORD","")
    
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
    logger = logging.getLogger("django")
    
    cariKod = event["message"]["cariKod"]
    cariName = event["message"]["cariName"]
    companyId = event["message"]["companyId"]
    adres = event["message"]["adres"]
    sehir = adres["city"]
    ulke = adres["country"]
    cadde = ""
    sokak = ""
    if len(adres["address"]) > 50:
        cadde = str(adres["address"][:50])
        sokak = str(adres["address"][50:100])
    else:
        cadde = adres["address"]
    
    try:
        with pyodbc.connect(connectionString, timeout = 5) as conn:

            tabloGoruntulemeDetay = f"""
            UPDATE CARI_HESAPLAR
            SET cari_unvan1 = '{cariName}'
            WHERE cari_kod = '{cariKod}';
            """

            SQL_QUERY = tabloGoruntulemeDetay
            
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)
            
            SQL_QUERY_HESAP_ADRESLERI = f"""
                UPDATE CARI_HESAP_ADRESLERI
                SET adr_cadde = '{cadde}',adr_sokak = '{sokak}', adr_il = '{sehir}', adr_ulke = '{ulke}'
                WHERE adr_cari_kod = '{cariKod}';
                """
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY_HESAP_ADRESLERI)
            

            
            response = {"status" : "success", "data" : {"id" : companyId}}
            
            return response
    except Exception as e:
        response = {"status" : "fail", "data" : {}}
            
        return response


