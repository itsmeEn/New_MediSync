import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, MessageNotification, Conversation, QueueStatus, QueueSchedule
from .serializers import MessageSerializer, MessageNotificationSerializer, QueueStatusSerializer, QueueScheduleSerializer

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


class QueueStatusConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time queue status updates
    """
    
    async def connect(self):
        self.department = self.scope['url_route']['kwargs'].get('department', 'general')
        self.user_id = self.scope['url_route']['kwargs'].get('user_id')
        
        # Join department-specific group for queue updates
        self.queue_group_name = f'queue_{self.department}'
        await self.channel_layer.group_add(
            self.queue_group_name,
            self.channel_name
        )
        
        # Join user-specific group for personal notifications
        if self.user_id:
            self.user_group_name = f'queue_user_{self.user_id}'
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
        
        await self.accept()
        
        # Send current queue status
        await self.send_current_queue_status()

    async def disconnect(self, close_code):
        # Leave groups
        await self.channel_layer.group_discard(
            self.queue_group_name,
            self.channel_name
        )
        
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'get_queue_status':
                await self.send_current_queue_status()
            elif message_type == 'get_queue_schedule':
                await self.send_current_queue_schedule()
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def queue_status_update(self, event):
        """Send queue status update to WebSocket"""
        status_data = event['status']
        await self.send(text_data=json.dumps({
            'type': 'queue_status_update',
            'status': status_data
        }))

    async def queue_schedule_update(self, event):
        """Send queue schedule update to WebSocket"""
        schedule_data = event['schedule']
        await self.send(text_data=json.dumps({
            'type': 'queue_schedule_update',
            'schedule': schedule_data
        }))

    async def queue_notification(self, event):
        """Send queue notification to WebSocket"""
        notification_data = event['notification']
        await self.send(text_data=json.dumps({
            'type': 'queue_notification',
            'notification': notification_data
        }))
        
        # Mark notification as delivered if notification_id is provided
        notification_id = notification_data.get('notification_id')
        if notification_id:
            await self.mark_notification_delivered(notification_id)

    async def queue_position_update(self, event):
        """Send queue position update to WebSocket"""
        position_data = event['position']
        await self.send(text_data=json.dumps({
            'type': 'queue_position_update',
            'position': position_data
        }))

    @database_sync_to_async
    def mark_notification_delivered(self, notification_id):
        """Mark a notification as delivered"""
        try:
            from .models import Notification
            from django.utils import timezone
            
            notification = Notification.objects.get(id=notification_id)
            notification.delivery_status = Notification.DELIVERY_DELIVERED
            notification.delivered_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
        except Exception:
            return False
    
    @database_sync_to_async
    def get_current_queue_status(self):
        """Get current queue status for department"""
        try:
            status = QueueStatus.objects.get(department=self.department)
            return QueueStatusSerializer(status).data
        except QueueStatus.DoesNotExist:
            return None

    @database_sync_to_async
    def get_current_queue_schedule(self):
        """Get current queue schedule for department"""
        from django.utils import timezone
        
        schedules = QueueSchedule.objects.filter(
            department=self.department,
            is_active=True,
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).order_by('start_time')
        
        return QueueScheduleSerializer(schedules, many=True).data

    async def send_current_queue_status(self):
        """Send current queue status to WebSocket"""
        status = await self.get_current_queue_status()
        if status:
            await self.send(text_data=json.dumps({
                'type': 'queue_status',
                'status': status
            }))

    async def send_current_queue_schedule(self):
        """Send current queue schedule to WebSocket"""
        schedules = await self.get_current_queue_schedule()
        await self.send(text_data=json.dumps({
            'type': 'queue_schedule',
            'schedules': schedules
        }))
