from django.utils.translation import gettext as _

import os
import pyodbc
import logging

def check_mikro_connection(data):
    SERVER = os.getenv("MIKRO_SERVER","")
    DATABASE = data["mikroDBName"]
    USERNAME = os.getenv("MIKRO_USERNAME","")
    PASSWORD = os.getenv("MIKRO_PASSWORD","")
    
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
    
    try:
        with pyodbc.connect(connectionString, timeout = 5) as conn:
            cariKod = data["cari_kod"].replace("_",".")
            print(cariKod)
            tabloGoruntulemeDetay = f"""
            SELECT cari_unvan1, cari_Guid FROM CARI_HESAPLAR
            WHERE cari_kod = '{cariKod}';
            """

            SQL_QUERY = tabloGoruntulemeDetay
            
            cursor = conn.cursor()
            cursor.execute(SQL_QUERY)

            records = cursor.fetchall()
            for r in records:
                row_to_list = [elem for elem in r]
            
            external_data = []
            
            for r in records:
                row_to_list = [elem for elem in r]
                
                external_data.append({
                    "id" : id,
                    "kod" : row_to_list[0],
                })
            
            if external_data:
                kod = external_data[0]["kod"]
            else:
                kod = ""
            
            response = {"status" : "success", "data" : {"kod":kod}}
            
            return response
    except Exception as e:
        response = {"status" : "fail", "data" : []}
            
        return response
    