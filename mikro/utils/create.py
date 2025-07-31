from django.utils.translation import gettext as _

import os
import pyodbc
import logging

from card.models import Company, Billing, Currency

#####company#####
def company_create(data):
    companyId = data["id"]
    
    if data["type"] == "company":
        company = Company.objects.filter(id=int(companyId)).first()
    elif data["type"] == "billing":
        company = Billing.objects.filter(id=int(companyId)).first()
    company.hesapKodu = data["yeniCariKod"]
    company.mikroGuid = data["yeniGuid"]
    company.save()
        
#####company-end#####

#####billing#####
def billing_create(data):
    billingId = data["id"]
    
    billing = Billing.objects.filter(id=int(billingId)).first()
    billing.hesapKodu = data["yeniCariKod"]
    billing.mikroGuid = data["yeniGuid"]
    billing.save()
#####billing-end#####

def create_mikro(event):
    SERVER = os.getenv("MIKRO_SERVER","")
    DATABASE = event["message"]["mikroDBName"]
    USERNAME = os.getenv("MIKRO_USERNAME","")
    PASSWORD = os.getenv("MIKRO_PASSWORD","")
    
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
    logger = logging.getLogger("django")
    
    type = event["message"]["type"]
    cariBasKod = event["message"]["cariBasKod"]
    cariOrtaKod = event["message"]["cariOrtaKod"]
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

            SQL_QUERY = f"""
            SELECT cari_kod
            FROM CARI_HESAPLAR
            WHERE cari_kod LIKE '{cariBasKod}%' AND SUBSTRING(cari_kod, 5, 2) = '{cariOrtaKod}'
            ORDER BY cari_kod ASC;
            """
            
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)
            
            records = cursor.fetchall()
            external_data = []
            id = 1
            
            for r in records:
                external_data.append({
                    "id" : id,
                    "kod" : r.cari_kod,
                    "sonKod" : int(r.cari_kod[-4:])
                })
                
                id = id + 1

            sonKod = external_data[-1]["sonKod"]
            
            yeniKod = sonKod + 1
            yeniCariKod = str(cariBasKod) + "." + str(cariOrtaKod)+ "." + str(yeniKod).zfill(4)
            
            SQL_QUERY = f"""
            INSERT INTO CARI_HESAPLAR (cari_kod, cari_unvan1, cari_muh_kod)
            VALUES ('{yeniCariKod}', '{cariName}', '{yeniCariKod}')
            """
            
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)


            SQL_QUERY = f"""
            INSERT INTO CARI_HESAP_ADRESLERI (adr_cari_kod, adr_cadde, adr_sokak, adr_il, adr_ulke)
            VALUES ('{yeniCariKod}', '{cadde}', '{sokak}','{sehir}','{ulke}')
            """
            
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)
            
            SQL_QUERY = f"""
            SELECT cari_kod,cari_Guid
            FROM CARI_HESAPLAR
            WHERE cari_kod = '{yeniCariKod}';
            """
            
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)
            
            records = cursor.fetchall()
            external_data = []
            id = 1
            
            for r in records:
                external_data.append({
                    "id" : id,
                    "kod" : r.cari_kod,
                    "guid" : r.cari_Guid
                })
                
                id = id + 1

            yeniGuid = external_data[0]["guid"]
            
            response = {"status" : "success", "data" : {"type":type, "id" : companyId,"yeniCariKod":yeniCariKod,"yeniGuid":yeniGuid}}
            
            return response
    except Exception as e:
        logger.exception(e)
        response = {"status" : "fail", "data" : {"type":type,"id" : companyId}}
            
        return response
