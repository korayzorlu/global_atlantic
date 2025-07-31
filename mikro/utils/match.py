from django.utils.translation import gettext as _

import os
import pyodbc
import logging

from card.models import Company, Billing

def company_match(data):
    companyId = data["id"]
    
    if data["type"] == "company":
        company = Company.objects.filter(id=int(companyId)).first()
    elif data["type"] == "billing":
        company = Billing.objects.filter(id=int(companyId)).first()
    company.mikroGuid = data["guid"]
    company.save()

def company_unmatch(data):
    companyId = data["id"]
    
    if data["type"] == "company":
        company = Company.objects.filter(id=int(companyId)).first()
    elif data["type"] == "billing":
        company = Billing.objects.filter(id=int(companyId)).first()
    company.mikroGuid = None
    company.save()

def match_mikro(event):
    SERVER = os.getenv("MIKRO_SERVER","")
    DATABASE = event["message"]["mikroDBName"]
    USERNAME = os.getenv("MIKRO_USERNAME","")
    PASSWORD = os.getenv("MIKRO_PASSWORD","")
    
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
    logger = logging.getLogger("django")
    
    type = event["message"]["type"]
    cariKod = event["message"]["cariKod"]
    cariName = event["message"]["cariName"]
    companyId = event["message"]["companyId"]
    
    try:
        with pyodbc.connect(connectionString, timeout = 5) as conn:
            
            tabloGoruntulemeDetay = f"""
            SELECT cari_kod, cari_unvan1, cari_Guid FROM CARI_HESAPLAR
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
            
            for r in records:
                row_to_list = [elem for elem in r]
                
                external_data.append({
                    "id" : id,
                    "kod" : row_to_list[0],
                    "name" : row_to_list[1],
                    "guid" : row_to_list[2]
                })
            
            if external_data:
                kod = external_data[0]["kod"]
                guid = external_data[0]["guid"]
                name = external_data[0]["name"]
            else:
                kod = ""
                guid = ""
                name = ""
            response = {"status" : "success", "data" : {"type":type,"id" : companyId,"kod":kod, "guid" : guid,"name":name}}
            
            return response
        
    except Exception as e:
        logger.exception(e)
        response = {"status" : "fail", "data" : {"type":type,"id" : companyId}}
            
        return response

def unmatch_mikro(event):
    type = event["message"]["type"]
    companyId = event["message"]["companyId"]
    
    response = {"status" : "success", "data" : {"type":type,"id" : companyId}}
            
    return response

