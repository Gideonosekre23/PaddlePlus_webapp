from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
import json
from .models import Bikes, BikeHardware
from asgiref.sync import sync_to_async

class GPSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.serial_number = self.scope['url_route']['kwargs']['serial_number']
        self.bike = await Bikes.objects.select_related('hardware').aget(
            hardware__serial_number=self.serial_number,
            hardware__is_assigned=True
        )
        self.group_name = f"bike_{self.bike.id}"
        
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
        
        if 'latitude' in data and 'longitude' in data:
            await self.handle_location_update(data)
        
        if 'battery_level' in data:
            await self.handle_status_update(data)
            
        await self.send(json.dumps({
            'message': 'Update received'
        }))

    async def handle_location_update(self, data):
        self.bike.hardware.latitude = data['latitude']
        self.bike.hardware.longitude = data['longitude']
        self.bike.hardware.last_location_update = timezone.now()
        await sync_to_async(self.bike.hardware.save)()
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'location_update',
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'timestamp': timezone.now().isoformat()
            }
        )

    async def handle_status_update(self, data):
        await sync_to_async(self.bike.hardware.update_status)(
            battery_level=data.get('battery_level')
        )
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'status_update',
                'battery_level': data.get('battery_level'),
                'last_ping': timezone.now().isoformat()
            }
        )

    async def location_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def status_update(self, event):
        await self.send(text_data=json.dumps(event))
