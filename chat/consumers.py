import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.api.serializer import ChatSerializer
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
            image_url = text_data_json.get('image_url')
            sender_id = text_data_json.get('sender', {}).get('id')
            recipient_id = text_data_json.get('receiver', {}).get('id')

            if (not message and not image_url) or sender_id is None or recipient_id is None:
                print("Invalid message format:", text_data_json)
                return

            thread_name = f"{min(sender_id, recipient_id)}_{max(sender_id, recipient_id)}"
            chat_message = await self.save_chat_message(message, sender_id, recipient_id, image_url, thread_name)

            messages = await self.get_messages(sender_id, recipient_id)
        
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'messages': messages,
                    'sender_id': sender_id,
                    'message': message,
                    'image_url': image_url
                }
            )

    async def chat_message(self, event):
        messages = event.get('messages', [])
        sender_id = event.get('sender_id')
        message = event.get('message')
        image_url = event.get('image_url')

        await self.send(text_data=json.dumps({
            'messages': messages,
            'sender': {'id': sender_id},
            'message': message,
            'image_url': image_url
        }))

    @database_sync_to_async
    def save_chat_message(self, message, sender_id, recipient_id, image_url, thread_name):
        return Chat.objects.create(
            message=message,
            sender_id=sender_id,
            receiver_id=recipient_id,
            image_url=image_url,
            thread_name=thread_name
        )

    @database_sync_to_async
    def get_messages(self, sender_id, recipient_id):
        
        thread_name = f"{min(sender_id, recipient_id)}_{max(sender_id, recipient_id)}"
        messages = Chat.objects.filter(thread_name=thread_name).order_by('date')
        return ChatSerializer(messages, many=True).data

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