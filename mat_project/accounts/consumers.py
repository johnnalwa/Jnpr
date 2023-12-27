# management/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        message = event['message']

        # Send the notification to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message,
        }))
