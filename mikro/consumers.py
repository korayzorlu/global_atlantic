import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

import pyodbc
from decouple import config, Csv
import json

import os
from dotenv import load_dotenv
load_dotenv()

from django.core.asgi import get_asgi_application
# Django ayarlarını başlat
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

# Django modellerine erişmek için gerekli yapılandırma
import django
django.setup()

from card.models import Company

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()

#     def disconnect(self, close_code):
#         pass

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         self.send(text_data=json.dumps({"message": message}))
        
class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["cari_kod"]
        self.room_group_name = f"mikro_status"
    
        # # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        
        await self.accept()
        # Bağlantı kontrol döngüsünü başlat
        #asyncio.create_task(self.check_connection_periodically())
        await self.check_connection()
        
        #await self.test()


    async def disconnect(self, close_code):
        pass
    
    # async def check_connection_periodically(self):
    #     while True:
    #         await self.check_connection()
    #         # Her 5 saniyede bir kontrol et
    #         await asyncio.sleep(5)

    # Receive message from room group
    async def check_connection(self):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16_ESMS_TEST"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        
        try:
            with pyodbc.connect(connectionString, timeout = 5) as conn:
                cariKod = self.scope["url_route"]["kwargs"]["cari_kod"].replace("_",".")
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
                print(external_data)
                
                # Bağlantı başarılı ise:
                if len(external_data) > 0:
                    await self.send(text_data=json.dumps({
                        'status': 'connected',
                        'message': 'Connected to Mikro'
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'status': 'not_found',
                        'message': 'Not found in Mikro'
                    }))
        except Exception as e:
            print(e)
            # Bağlantı başarısız ise:
            await self.send(text_data=json.dumps({
                'status': 'not_connected',
                'message': 'Failed to connect to Mikro!'
            }))
            
    async def check_connection_signal(self, event):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16_ESMS_TEST"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        
        try:
            with pyodbc.connect(connectionString, timeout = 5) as conn:
                cariKod = event["cariKod"]
                print(cariKod)
                tabloGoruntulemeDetay = f"""
                SELECT cari_unvan1 FROM CARI_HESAPLAR
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
                print(external_data)
                
                # Bağlantı başarılı ise:
                if len(external_data) > 0:
                    await self.send(text_data=json.dumps({
                        'status': 'connected',
                        'message': 'Connected to Mikro'
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'status': 'not_found',
                        'message': 'Not found in Mikro'
                    }))
        except Exception as e:
            print(e)
            # Bağlantı başarısız ise:
            await self.send(text_data=json.dumps({
                'status': 'not_connected',
                'message': 'Failed to connect to Mikro!'
            }))
            
    async def send_update(self, event):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16_ESMS_TEST"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        
        try:
            with pyodbc.connect(connectionString, timeout = 5) as conn:
                cariKod = event["cariKod"]
                cariName = event["cariName"]
                print(cariName)
                tabloGoruntulemeDetay = f"""
                UPDATE CARI_HESAPLAR
                SET cari_unvan1 = '{cariName}'
                WHERE cari_kod = '{cariKod}';
                """

                SQL_QUERY = tabloGoruntulemeDetay
                
                cursor = conn.cursor()
                cursor.execute(SQL_QUERY)
                
                await self.send(text_data=json.dumps({
                    'status': 'success',
                    'message': 'Updated in Mikro'
                }))
        except Exception as e:
            print(e)
            # Bağlantı başarısız ise:
            await self.send(text_data=json.dumps({
                'status': 'not_connected',
                'message': 'Failed to connect to Mikro!'
            }))
            
    @sync_to_async        
    def company_update(self, id, name):
        companyId = id
        
        company = Company.objects.filter(id=int(companyId)).first()
        company.name = name
        company.save()
            
    async def get_update(self, event):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16_ESMS_TEST"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        
        cariKod = event["cariKod"]
        cariName = event["cariName"]
        companyId = event["companyId"]
        
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
                print(external_data)
                
                await self.company_update(id=companyId,name=row_to_list[1])
                
                await self.send(text_data=json.dumps({
                    'status': 'success',
                    'message': 'Updated from Mikro',
                    'process': 'reload'
                }))
            
        except Exception as e:
            print(e)
            # Bağlantı başarısız ise:
            await self.send(text_data=json.dumps({
                'status': 'not_connected',
                'message': 'Failed to connect to Mikro!',
                'process': 'not_reload'
            }))

    @sync_to_async        
    def company_match(self, id, guid):
        companyId = id
        
        company = Company.objects.filter(id=int(companyId)).first()
        company.mikroGuid = guid
        company.save()
            
    async def match(self, event):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16_ESMS_TEST"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        
        cariKod = event["cariKod"]
        cariName = event["cariName"]
        companyId = event["companyId"]
        
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
                print(external_data)
                
                await self.company_match(id=companyId,guid=row_to_list[2])
                
                await self.send(text_data=json.dumps({
                    'status': 'success',
                    'message': 'Matched with Mikro',
                    'process': 'reload'
                }))
            
        except Exception as e:
            print(e)
            # Bağlantı başarısız ise:
            await self.send(text_data=json.dumps({
                'status': 'not_connected',
                'message': 'Failed to connect to Mikro!',
                'process': 'not_reload'
            }))
            
    async def check_part_connection(self):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16_ESMS_TEST"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        
        try:
            with pyodbc.connect(connectionString, timeout = 5) as conn:
                cariKod = self.scope["url_route"]["kwargs"]["cari_kod"].replace("_",".")
                print(cariKod)
                tabloGoruntulemeDetay = f"""
                SELECT TOP (1000) sto_kod, sto_isim, sto_kisa_ismi, sto_sat_cari_kod,sto_cins,sto_birim1_ad,sto_birim2_ad FROM STOKLAR;
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
                        "kod" : row_to_list[0],
                        "isim" : row_to_list[1],
                        "kisa_ismi" : row_to_list[2],
                        "sat_cari_kod" : row_to_list[3],
                        "cins" : row_to_list[4],
                        "birim1_ad" : row_to_list[5],
                        "birim2_ad" : row_to_list[6]
                    })
                print(json.dumps(external_data, indent=4))
                
                # Bağlantı başarılı ise:
                if len(external_data) > 0:
                    await self.send(text_data=json.dumps({
                        'status': 'connected',
                        'message': 'Connected to Mikro'
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'status': 'not_found',
                        'message': 'Not found in Mikro'
                    }))
        except Exception as e:
            print(e)
            # Bağlantı başarısız ise:
            await self.send(text_data=json.dumps({
                'status': 'not_connected',
                'message': 'Failed to connect to Mikro!'
            }))
    
    async def test(self):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16_ESMS_TEST"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        
        try:
            with pyodbc.connect(connectionString, timeout = 5) as conn:
                cariKod = self.scope["url_route"]["kwargs"]["cari_kod"].replace("_",".")
                
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
                    if data["cari_unvan2"] == "." or data["cari_unvan2"] == ",":
                        print(data["cari_unvan2"])
                
                # try:
                #     with pyodbc.connect(connectionString, timeout = 5) as conn:
                        
                #         tabloGoruntulemeDetay = f"""
                #         UPDATE CARI_HESAPLAR
                #         SET cari_unvan1 = '{cariName}'
                #         WHERE cari_kod = '{cariKod}';
                #         """

                #         SQL_QUERY = tabloGoruntulemeDetay
                        
                #         cursor = conn.cursor()
                #         cursor.execute(SQL_QUERY)
                        
                #         await self.send(text_data=json.dumps({
                #             'status': 'success',
                #             'message': 'Updated in Mikro'
                #         }))
                # except Exception as e:
                #     print(e)
                #     # Bağlantı başarısız ise:
                #     await self.send(text_data=json.dumps({
                #         'status': 'not_connected',
                #         'message': 'Failed to connect to Mikro!'
                #     }))
                
                # Bağlantı başarılı ise:
                if len(external_data) > 0:
                    await self.send(text_data=json.dumps({
                        'status': 'connected',
                        'message': 'Connected to Mikro'
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'status': 'not_found',
                        'message': 'Not found in Mikro'
                    }))
        except Exception as e:
            print(e)
            # Bağlantı başarısız ise:
            await self.send(text_data=json.dumps({
                'status': 'not_connected',
                'message': 'Failed to connect to Mikro!'
            }))
     
    async def test2(self):
        SERVER = os.getenv("MIKRO_SERVER","")
        DATABASE = "MikroDB_V16_ESMS_TEST"
        USERNAME = os.getenv("MIKRO_USERNAME","")
        PASSWORD = os.getenv("MIKRO_PASSWORD","")
        
        connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
        
        try:
            with pyodbc.connect(connectionString, timeout = 5) as conn:
                cariKod = self.scope["url_route"]["kwargs"]["cari_kod"].replace("_",".")
                
                tabloGoruntulemeDetay = f"""
                SELECT
                adr_cari_kod, adr_adres_no, adr_ulke
                FROM CARI_HESAP_ADRESLERI;
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
                        "adr_cari_kod" : row_to_list[0],
                        "adr_adres_no" : row_to_list[1],
                        "adr_ulke" : row_to_list[2]
                    })
                print(json.dumps(external_data, indent=4, ensure_ascii=False))
                
                # Bağlantı başarılı ise:
                if len(external_data) > 0:
                    await self.send(text_data=json.dumps({
                        'status': 'connected',
                        'message': 'Connected to Mikro'
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'status': 'not_found',
                        'message': 'Not found in Mikro'
                    }))
        except Exception as e:
            print(e)
            # Bağlantı başarısız ise:
            await self.send(text_data=json.dumps({
                'status': 'not_connected',
                'message': 'Failed to connect to Mikro!'
            }))

