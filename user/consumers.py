import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

import os
import pyodbc
import logging

from mikro.utils.check import *
from mikro.utils.match import *
from mikro.utils.update import *
from mikro.utils.create import *
from sale.utils import *

# Django ayarlarını başlat
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

# Django modellerine erişmek için gerekli yapılandırma
import django
django.setup()

class MainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["user"]
        self.room_group_name = f"private_{self.room_name}"
        self.group_name = 'public_room'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        type = data.get('type')
        if type == 'check_mikro':
            await self.check_mikro(data);
        elif type == 'match_mikro_new':
            await self.match_mikro_new(data);

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({ 'type': event['type'], 'message': event['message'] }))

    async def reload_micho(self, event):
        await self.send(text_data=json.dumps({ 'type': event['type'], 'message': event['message'] }))
    
    async def send_alert(self, event):
        await self.send(text_data=json.dumps({ 'type': event['type'], 'message': event['message'], 'location': event['location']}))
    
    async def send_percent(self, event):
        await self.send(text_data=json.dumps({ 'type': event['type'], 'message': event['message'], 'location': event['location'], 'totalCount': event['totalCount'], 'ready': event['ready'] }))
            
    async def update_detail(self, event):
        await self.send(text_data=json.dumps({ 'type': event['type'], 'message': event['message'], 'location': event['location'] }))
        
    async def send_process(self, event):
        await self.send(text_data=json.dumps({ 'type': event['type'], 'message': event['message'], 'location': event['location'] }))
        
    async def reload_table(self, event):
        await self.send(text_data=json.dumps({ 'type': event['type'], 'message': event['message'], 'location': event['location'] }))
    
    #####MIKRO#####
    @sync_to_async        
    def company_match(self, data):
        company_match(data)
        
    @sync_to_async        
    def company_unmatch(self, data):
        company_unmatch(data)

    @sync_to_async        
    def company_update_from(self, data):
        company_update_from(data)
        
    @sync_to_async        
    def company_create(self, data):
        company_create(data)
        
    @sync_to_async        
    def billing_create(self, data):
        billing_create(data)
        
    @sync_to_async        
    def billing_update_from(self, data):
        billing_update_from(data)
        
    async def check_mikro(self, data):
        
        if data['location'] == "check_mikro_connection":
            response = check_mikro_connection(data)
            
            if response["status"] == "success":
                if response["data"]["kod"]:
                    await self.send_alert({'type': "send_alert", 'location': data['location'], 'message': {'status':'success','icon':'satellite-dish','message':'Connected to Mikro'}})
                else:
                    await self.send_alert({'type': "send_alert", 'location': data['location'], 'message': {'status':'warning','icon':'triangle-exclamation ','message':'Not found in Mikro'}})
            elif response["status"] == "fail":
                await self.send_alert({'type': "send_alert", 'location': data['location'], 'message': {'status':'danger','icon':'triangle-exclamation ','message':'Failed to connect to Mikro!'}})
    
    async def match_mikro_new(self, data):
        if data['location'] == "match_mikro_company":
            response = match_mikro(data)
            
            if response["status"] == "success":
                if response["data"]["guid"]:
                    await self.send(text_data=json.dumps({'type': data['type'], "responseData": response["data"],'data': data['message'], 'location': data['location'], 'status': 'success','message': 'Matched with Mikro','process': 'reload'}))
                else:
                    await self.send(text_data=json.dumps({'type': data['type'], "responseData": response["data"],'data': data['message'], 'location': data['location'], 'status': 'not_found','message': 'Not found in Mikro','process': 'reload'}))
            elif response["status"] == "fail":
                await self.send(text_data=json.dumps({'type': data['type'], "responseData": response["data"],'data': data['message'], 'location': data['location'], 'status': 'not_connected','message': 'Failed to connect to Mikro!','process': 'not_reload'}))
                
    async def match_mikro(self, event):
        if event['location'] == "match_mikro":
            response = match_mikro(event)
            
            if response["status"] == "success":
                await self.company_match(data=response["data"])
                await self.send_alert({'type': "send_alert", 'location': event['location'], 'message': {'status':'success','icon':'circle-check','message':'Matched with Mikro','variable':{'elementTag':event['message']["type"],'elementTagId':response["data"]["id"],'url':'/card/'+event['message']["type"]+'_update/'}}})
            elif response["status"] == "fail":
                await self.send_alert({'type': "send_alert", 'location': event['location'], 'message': {'status':'danger','icon':'triangle-exclamation','message':'Failed to connect to Mikro!','variable':{'elementTag':event['message']["type"],'elementTagId':response["data"]["id"],'url':'/card/'+event['message']["type"]+'_update/'}}})
                
        elif event['location'] == "unmatch_mikro":
            response = unmatch_mikro(event)
            
            await self.company_unmatch(data=response["data"])
            await self.send_alert({'type': "send_alert", 'location': event['location'], 'message': {'status':'success','icon':'circle-check','message':'Match removed with Mikro','variable':{'elementTag':event['message']["type"],'elementTagId':response["data"]["id"],'url':'/card/'+event['message']["type"]+'_update/'}}})
            
    async def update_mikro(self, event):
        if event['location'] == "update_from_mikro_company":
            response = update_from_mikro(event)
            
            if response["status"] == "success":
                await self.company_update_from(data=response["data"])
                await self.send(text_data=json.dumps({'type': event['type'], 'message': event['message'], 'location': event['location'], 'status': 'success','message': 'Updated from Mikro','process': 'reload'}))
            elif response["status"] == "fail":
                await self.send(text_data=json.dumps({'type': event['type'], 'message': event['message'], 'location': event['location'], 'status': 'not_connected','message': 'Failed to connect to Mikro!','process': 'not_reload'}))
        elif event['location'] == "update_to_mikro_company":
            response = update_to_mikro(event)
            
            if response["status"] == "success":
                await self.send(text_data=json.dumps({'type': event['type'], 'message': event['message'], 'location': event['location'], 'status': 'success','message': 'Sent updates to Mikro','process': 'reload'}))
            elif response["status"] == "fail":
                await self.send(text_data=json.dumps({'type': event['type'], 'message': event['message'], 'location': event['location'], 'status': 'not_connected','message': 'Failed to connect to Mikro!','process': 'not_reload'}))
        elif event['location'] == "update_from_mikro_billing":
            response = update_from_mikro(event)
            
            if response["status"] == "success":
                await self.billing_update_from(data=response["data"])
                await self.send(text_data=json.dumps({'type': event['type'], 'message': event['message'], 'location': event['location'], 'status': 'success','message': 'Updated from Mikro','process': 'reload'}))
            elif response["status"] == "fail":
                await self.send(text_data=json.dumps({'type': event['type'], 'message': event['message'], 'location': event['location'], 'status': 'not_connected','message': 'Failed to connect to Mikro!','process': 'not_reload'}))
        elif event['location'] == "update_to_mikro_billing":
            response = update_to_mikro(event)
            
            if response["status"] == "success":
                await self.send(text_data=json.dumps({'type': event['type'], 'message': event['message'], 'location': event['location'], 'status': 'success','message': 'Sent updates to Mikro','process': 'reload'}))
            elif response["status"] == "fail":
                await self.send(text_data=json.dumps({'type': event['type'], 'message': event['message'], 'location': event['location'], 'status': 'not_connected','message': 'Failed to connect to Mikro!','process': 'not_reload'}))
        
    async def create_mikro(self, event):
        if event['location'] == "create_mikro":
            response = create_mikro(event)
            
            if response["status"] == "success":
                await self.company_create(data=response["data"])
                await self.send_alert({'type': "send_alert", 'location': event['location'], 'message': {'status':'success','icon':'circle-check','message':'Created account in Mikro','variable':{'elementTag':event['message']["type"],'elementTagId':response["data"]["id"],'url':'/card/'+event['message']["type"]+'_update/'}}})
            elif response["status"] == "fail":
                await self.send_alert({'type': "send_alert", 'location': event['location'], 'message': {'status':'danger','icon':'triangle-exclamation','message':'Failed to connect to Mikro!','variable':{'elementTag':event['message']["type"],'elementTagId':response["data"]["id"],'url':'/card/'+event['message']["type"]+'_update/'}}})
    #####MIKRO-end#####

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'public_room'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({ 'message': event['message'] }))
        
class ProgressBarConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.temperature = self.scope["url_route"]["kwargs"]["temperature"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "make_cake",
                "message": {
                    "message": "The cake is ready",
                    "progress": "6",
                },
            },
        )

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"alert_{self.room_name}"
    
        # # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        
        await self.accept()
        # Bağlantı kontrol döngüsünü başlat
        #asyncio.create_task(self.check_connection_periodically())
        #await self.check_connection()


    async def disconnect(self, close_code):
        pass
    
    # Receive message from room group
    async def danger(self,event):
        await self.send(text_data=json.dumps({
            'status': 'danger',
            'message': event["message"],
            'process': event["process"]
        }))
    async def success(self,event):
        await self.send(text_data=json.dumps({
            'status': 'success',
            'message': event["message"],
            'process': event["process"]
        }))
    async def close_and_open(self,event):
        await self.send(text_data=json.dumps({
            'status': 'success',
            'message': event["message"],
            'process': event["process"],
            'elementTag': event["elementTag"],
            'elementTagSub': event["elementTagSub"],
            'elementTagId': event["elementTagId"],
            'apiUrl': event["apiUrl"],
            'tabUrl': event["tabUrl"],
            'sessionKey': event["sessionKey"],
            'user': event["user"]
        }))