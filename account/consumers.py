import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

import pyodbc
from decouple import config, Csv

import os
from dotenv import load_dotenv
load_dotenv()

from django.core.asgi import get_asgi_application
# Django ayarlarını başlat
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

# Django modellerine erişmek için gerekli yapılandırma
import django
django.setup()

from .models import Payment

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()

#     def disconnect(self, close_code):
#         pass

#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         self.send(text_data=json.dumps({"message": message}))
        
class PaymentAddConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"payment_add"
    
        # # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        
        await self.accept()
        # Bağlantı kontrol döngüsünü başlat
        #asyncio.create_task(self.check_connection_periodically())
        #await self.check_connection()


    async def disconnect(self, close_code):
        pass
    
    # Receive message from room group
    async def check_currencies(self,event):
        await self.send(text_data=json.dumps({
            'status': 'failed',
            'message': 'Payment curr. and bank curr. must be same!'
        }))
    async def success(self,event):
        await self.send(text_data=json.dumps({
            'status': 'success',
            'message': 'Success'
        }))

        