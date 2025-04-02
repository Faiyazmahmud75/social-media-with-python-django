import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from asgiref.sync import sync_to_async
from django.db.models import Count

class ChatConsumer(AsyncWebsocketConsumer):
    active_users = {}  # Track active users in each room

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        current_user = self.scope["user"].username
        room_user = self.room_name
        self.room_group_name = f"chat_{'_'.join(sorted([current_user.lower(), room_user.lower()]))}"
        self.user = self.scope["user"]
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(f"chat_list_{self.user.username}", self.channel_name)
        await self.accept()
        await self.mark_messages_as_read(await self.get_receiver_user())
        await self.set_user_active(self.user.username, self.room_group_name)  # Add user to active users
        await self.send_unread_counts(self.user)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(f"chat_list_{self.user.username}", self.channel_name)
        await self.set_user_inactive(self.user.username, self.room_group_name)  # Remove user from active users

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "message":
            message = data["message"]
            sender = self.scope["user"]
            receiver = await self.get_receiver_user()

            if not receiver:
                print(f"Receiver not found for room: {self.room_group_name}")
                return

            await self.save_message(sender, receiver, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "sender": sender.username,
                    "receiver": receiver.username,
                    "message": message,
                },
            )
            await self.send_unread_counts(receiver)
        elif message_type == "message_read":
            sender_username = data.get("sender")
            sender = await self.get_user(sender_username)
            if sender:
                await self.mark_messages_as_read(sender)
                await self.send_unread_counts(self.user)

        else:
            print(f"Unknown message type: {message_type}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def send_unread_counts(self, user):
        unread_conversations = await self.get_unread_conversation_count(user)
        unread_per_chat = await self.get_unread_per_chat(user)

        # Filter out counts for active users
        filtered_unread_per_chat = []
        for item in unread_per_chat:
            room_group_name = f"chat_{'_'.join(sorted([user.username.lower(), item['username'].lower()]))}"
            if not self.is_user_active(item['username'], room_group_name):
                filtered_unread_per_chat.append(item)

        unread_conversations = len(filtered_unread_per_chat)

        await self.channel_layer.group_send(
            f"chat_list_{user.username}",
            {
                "type": "update_unread_counts",
                "unread_conversations": unread_conversations,
                "unread_per_chat": filtered_unread_per_chat,
            },
        )

    async def update_unread_counts(self, event):
        await self.send(text_data=json.dumps({
            "type": "update_unread_counts",
            "unread_conversations": event["unread_conversations"],
            "unread_per_chat": event["unread_per_chat"],
        }))

    async def set_user_active(self, username, room_group_name):
        if room_group_name not in ChatConsumer.active_users:
            ChatConsumer.active_users[room_group_name] = set()
        ChatConsumer.active_users[room_group_name].add(username)

    async def set_user_inactive(self, username, room_group_name):
        if room_group_name in ChatConsumer.active_users:
            ChatConsumer.active_users[room_group_name].discard(username)

    def is_user_active(self, username, room_group_name):
        return room_group_name in ChatConsumer.active_users and username in ChatConsumer.active_users[room_group_name]

    @sync_to_async
    def save_message(self, sender, receiver, message):
        Message.objects.create(sender=sender, receiver=receiver, content=message, is_read=False)

    @sync_to_async
    def get_receiver_user(self):
        users = self.room_group_name.replace("chat_", "").split('_')
        receiver_username = [user for user in users if user != self.user.username][0]
        return User.objects.get(username=receiver_username)

    @sync_to_async
    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @sync_to_async
    def mark_messages_as_read(self, sender):
        Message.objects.filter(sender=sender, receiver=self.user, is_read=False).update(is_read=True)

    @sync_to_async
    def get_unread_conversation_count(self, user):
        return Message.objects.filter(receiver=user, is_read=False).values("sender").distinct().count()

    @sync_to_async
    def get_unread_per_chat(self, user):
        unread_counts = Message.objects.filter(receiver=user, is_read=False).values('sender').annotate(unread_count=Count('id'))
        user_unread_counts = []
        for item in unread_counts:
            user = User.objects.get(id = item['sender'])
            user_unread_counts.append({'username':user.username, 'unread_count':item['unread_count']})
        return user_unread_counts