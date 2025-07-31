from django.core.management.base import BaseCommand, CommandError

import os
import pyodbc

import pandas as pd

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None


    def handle(self, *args, **options):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16_ESMS_TEST"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        
        try:
            with pyodbc.connect(connectionString, timeout = 5) as conn:
                
                tabloGoruntulemeDetay = f"""
                SELECT
                cari_kod, cari_unvan1, cari_unvan2,
                cari_vdaire_adi, cari_fatura_adres_no, cari_sevk_adres_no,
                cari_doviz_cinsi, cari_doviz_cinsi1, cari_doviz_cinsi2
                FROM CARI_HESAPLAR
                ORDER BY cari_unvan1;
                """

                SQL_QUERY = tabloGoruntulemeDetay
                
                cursor = conn.cursor()
                
                cursor.execute(SQL_QUERY)

                records = cursor.fetchall()
                
                for r in records:
                    row_to_list = [elem for elem in r]
                
                external_data = []
                
                #####Adres Getir#####
                try:
                    DATABASE = "MikroDB_V16_ESMS_TEST"
                    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
                    conn = pyodbc.connect(connectionString)
                    SQL_QUERY_EVRAK_TIP = """
                    SELECT adr_adres_no, adr_ulke FROM CARI_HESAP_ADRESLERI;
                    """
                    cursor = conn.cursor()
                    cursor.execute(SQL_QUERY_EVRAK_TIP)
                    adresRecords = cursor.fetchall()
                    adresDict = {}
                    for adresRecord in adresRecords:
                        row_to_list_adres = [elem for elem in adresRecord]
                        adresDict[str(row_to_list_adres[0])] = row_to_list_adres[1]
                except Exception as e:
                    print(e)
                    adresDict = {}
                #####Adres Getir-end#####
                
                for r in records:
                    row_to_list = [elem for elem in r]
                    
                    external_data.append({
                        "cari_kod" : row_to_list[0],
                        "cari_unvan1" : row_to_list[1],
                        "cari_unvan2" : row_to_list[2],
                        "cari_vdaire_adi" : row_to_list[3],
                        "adres" : adresDict.get(str(row_to_list[4])),
                        "cari_sevk_adres_no" : row_to_list[5],
                        "cari_doviz_cinsi" : row_to_list[6],
                        "cari_doviz_cinsi1" : row_to_list[7],
                        "cari_doviz_cinsi2" : row_to_list[8]
                    })
                #print(json.dumps(external_data, indent=4, ensure_ascii=False))
                
                for data in external_data:
                    if data["cari_unvan2"] != "":
                        print("eski: " + data["cari_unvan2"])
                
                        try:
                            with pyodbc.connect(connectionString, timeout = 5) as conn:
                                
                                tabloGoruntulemeDetay = f"""
                                UPDATE CARI_HESAPLAR
                                SET cari_unvan2 = ''
                                WHERE cari_kod = '{data["cari_kod"]}';
                                """

                                SQL_QUERY = tabloGoruntulemeDetay
                                
                                cursor = conn.cursor()
                                cursor.execute(SQL_QUERY)
                        except Exception as e:
                            print(e)
                        
        except Exception as e:
            print(e)