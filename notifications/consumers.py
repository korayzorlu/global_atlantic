import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

import os

# Django ayarlarını başlat
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

# Django modellerine erişmek için gerekli yapılandırma
import django
django.setup()

from data.models import Part

# class MainConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["user"]
#         self.group_name = 'public_room'
        
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )

#     async def send_notification(self, event):
#         await self.send(text_data=json.dumps({ 'type': event['type'], 'message': event['message'] }))
