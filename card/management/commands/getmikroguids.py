from django.core.management.base import BaseCommand, CommandError
from card.models import Vessel,Company

import pandas as pd
import os
import pyodbc

class Command(BaseCommand):
    help = 'Exports parts to JSON file'
    
    def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None

    def handle(self, *args, **options):
        companies = Company.objects.filter()

        for company in companies:
            name = company.name
            
            SERVER = os.getenv("MIKRO_SERVER","")
            DATABASE = "MikroDB_V16_ESMS_TEST"
            USERNAME = os.getenv("MIKRO_USERNAME","")
            PASSWORD = os.getenv("MIKRO_PASSWORD","")
            
            connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
            
            try:
                with pyodbc.connect(connectionString, timeout = 5) as conn:
                    print(name)
                    tabloGoruntulemeDetay = f"""
                    SELECT cari_kod, cari_unvan1, cari_Guid FROM CARI_HESAPLAR
                    WHERE cari_unvan1 = '{name}';
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
                    print(external_data)
                    
                    company.hesapKodu = row_to_list[0]
                    company.mikroGuid = row_to_list[2]
                    company.save()
                    
            except Exception as e:
                print(e)