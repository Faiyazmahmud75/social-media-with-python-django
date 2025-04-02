import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
    
        if self.user.is_anonymous:
            print("User is anonymous, closing WebSocket.")
            await self.close()
            return
        
        self.group_name = f"notifications_{self.user.id}"
        print(f"User {self.user.username} connected to {self.group_name}")

        # Join the user's notification group
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()
        print("WebSocket connection accepted for user {self.user.username}.")

        await self.send(text_data=json.dumps({
        'type': 'connection_established',
        'message': 'Connected to notification service'
    }))

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Received data: {data}")  # Debugging
        notification_type = data.get('notification_type')
        sender_id = data.get('sender_id')
        content = data.get('content', '')

        # Fetch sender and create notification
        sender = await database_sync_to_async(User.objects.get)(id=sender_id)
        notification = await database_sync_to_async(self.create_notification)(notification_type, sender, content)

        # Send notification to the receiver's WebSocket group
        await self.channel_layer.group_send(
            f"notifications_{self.user.id}",
            {
                'type': 'send_notification',
                'notification_type': notification.notification_type,
                'sender': sender.username,
                'content': notification.content
            }
        )

    @database_sync_to_async
    def create_notification(self, notification_type, sender, content):
        notification = Notification.objects.create(
            user=self.user, sender=sender, notification_type=notification_type, content=content
        )
        return notification

    async def send_notification(self, event):
        print(f"Sending notification: {event}")
        notification_type = event.get('notification_type', 'general')
        sender = event.get('sender', 'Someone')
        content = event.get('content', '') or event.get('message', ''),
        url = event.get('url', '')
    
        await self.send(text_data=json.dumps({
            'notification_type': notification_type,
            'sender': sender,
            'content': content,
            'url': url,
        }))
