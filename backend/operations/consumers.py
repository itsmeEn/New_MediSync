import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, MessageNotification, Conversation
from .serializers import MessageSerializer, MessageNotificationSerializer

User = get_user_model()

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'messaging_{self.user_id}'
        
        # Join user group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send any pending notifications
        await self.send_pending_notifications()

    async def disconnect(self, close_code):
        # Leave user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_notification_sent':
                notification_id = text_data_json.get('notification_id')
                await self.mark_notification_as_sent(notification_id)
            elif message_type == 'mark_message_read':
                message_id = text_data_json.get('message_id')
                await self.mark_message_as_read(message_id)
            elif message_type == 'get_notifications':
                await self.send_pending_notifications()
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def new_message(self, event):
        """Send new message to WebSocket"""
        message_data = event['message']
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': message_data
        }))

    async def message_delivered(self, event):
        """Send message delivered notification to WebSocket"""
        message_data = event['message']
        await self.send(text_data=json.dumps({
            'type': 'message_delivered',
            'message': message_data
        }))

    async def message_read(self, event):
        """Send message read notification to WebSocket"""
        message_data = event['message']
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message': message_data
        }))

    async def notification(self, event):
        """Send notification to WebSocket"""
        notification_data = event['notification']
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification_data
        }))

    @database_sync_to_async
    def mark_notification_as_sent(self, notification_id):
        """Mark notification as sent"""
        try:
            notification = MessageNotification.objects.get(
                id=notification_id,
                recipient_id=self.user_id
            )
            notification.is_sent = True
            notification.save()
            return True
        except MessageNotification.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """Mark message as read"""
        try:
            message = Message.objects.get(
                id=message_id,
                conversation__participants__id=self.user_id
            )
            if not message.is_read and message.sender_id != self.user_id:
                message.is_read = True
                message.save()
                
                # Create read notification for sender
                MessageNotification.objects.create(
                    message=message,
                    recipient=message.sender,
                    notification_type='message_read'
                )
                return True
        except Message.DoesNotExist:
            pass
        return False

    @database_sync_to_async
    def get_pending_notifications(self):
        """Get pending notifications for user"""
        notifications = MessageNotification.objects.filter(
            recipient_id=self.user_id,
            is_sent=False
        ).order_by('-created_at')[:20]
        
        return MessageNotificationSerializer(notifications, many=True).data

    async def send_pending_notifications(self):
        """Send pending notifications to WebSocket"""
        notifications = await self.get_pending_notifications()
        
        for notification in notifications:
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': notification
            }))
