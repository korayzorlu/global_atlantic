import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import FileResponse

class QuotationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'quotation_room'
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

    async def create_excel(self, event):
        await self.send(text_data=json.dumps({ 'message': event['message'] }))