import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Chat
from channels.db import database_sync_to_async

class TextConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        sender_id, recipient_id = self.room_name.split('_')

        # Creating room
        self.room_group_name = f"chat_{min(sender_id, recipient_id)}_{max(sender_id, recipient_id)}"

        # Join the room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        # Leave the room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await super().disconnect(code)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'mark_as_read':
            await self.mark_message_as_read(text_data)
        else:
            message = text_data_json.get('message')
            sender_id = text_data_json.get('sender', {}).get('id')
            recipient_id = text_data_json.get('receiver', {}).get('id')

            if not message or sender_id is None or recipient_id is None:
                print("Invalid message format:", text_data_json)
                return

            chat_message = await self.save_chat_message(message, sender_id, recipient_id)

            messages = await self.get_messages(sender_id, recipient_id)
        
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'messages': messages,
                    'sender_id': sender_id,
                    'message': message
                }
            )

    async def mark_message_as_read(self, text_data):
        data = json.loads(text_data)
        message_id = data.get('message_id')
        if message_id:
            await self.mark_as_read(message_id)

    @database_sync_to_async
    def mark_as_read(self, message_id):
        try:
            chat_message = Chat.objects.get(id=message_id)
            chat_message.mark_as_read()
        except Chat.DoesNotExist:
            pass



    async def chat_message(self, event):
        messages = event.get('messages', [])
        sender_id = event.get('sender_id')
        message = event.get('message')

        await self.send(text_data=json.dumps({
            'messages': messages,
            'sender': {'id': sender_id},
            'message': message
        }))


    @database_sync_to_async
    def save_chat_message(self, message, sender_id, recipient_id):
        return Chat.objects.create(message=message, sender_id=sender_id, receiver_id=recipient_id)

    @database_sync_to_async
    def mark_as_read(self, chat_message):
        chat_message.mark_as_read()

    @database_sync_to_async
    def get_messages(self, sender, recipient_id):
        from .models import Chat
        from chat.api.serializer import ChatSerializer

        messages = []
        for instance in Chat.objects.filter(sender__in=[sender, recipient_id], receiver__in=[sender, recipient_id]):
            messages.append(ChatSerializer(instance).data)

        return messages


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'notification_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification_message',
                'message': message
            }
        )

    # Receive message from room group
    async def notification_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))