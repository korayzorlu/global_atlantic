from celery import shared_task

from core.celery import app

from django.shortcuts import render, HttpResponse, redirect, get_object_or_404

from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import os
import pyodbc
import logging
import json

from .models import Company

def sendAlert(message,location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'public_room',
        {
            "type": "send_alert",
            "message": message,
            "location" : location
        }
    )

@shared_task
def add():
    
    return "test başarılı yeni"

@shared_task
def companyAdd(company):
    company.save()
    return HttpResponse(status=204)

@shared_task
def check_mikro_connection(data):
    data = json.loads(data)
    print(data)
    SERVER = os.getenv("MIKRO_SERVER","")
    DATABASE = "MikroDB_V16_ESMS_TEST"
    USERNAME = os.getenv("MIKRO_USERNAME","")
    PASSWORD = os.getenv("MIKRO_PASSWORD","")
    
    connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Provider=SQLNCLI11;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=MASTER;Data Source=VSRV2;TrustServerCertificate=yes;'
    
    try:
        with pyodbc.connect(connectionString, timeout = 5) as conn:
            cariKod = data["cari_kod"].replace("_",".")
            
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
            
            if kod:
                data = {
                        "status":"secondary",
                        "icon":"circle-check",
                        "message":"Connected to Mikro"
                        }
            else:
                data = {
                        "status":"secondary",
                        "icon":"triangle-exclamation",
                        "message":"Not found in Mikro"
                        }

            sendAlert(data,"default") 
            
    except Exception as e:
        data = {
                "status":"secondary",
                "icon":"triangle-exclamation",
                "message":"Failed to connect to Mikro!"
                }

        sendAlert(data,"default") 

