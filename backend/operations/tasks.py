"""
Celery tasks for operations module.
"""
import logging
from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


@shared_task(name='backend.operations.tasks.auto_close_queues')
def auto_close_queues():
    """
    Periodic task to automatically close queues that are past their scheduled end time.
    Runs every 5 minutes to check and close any queues that should be closed.
    """
    from .models import QueueStatus, QueueStatusLog
    from .serializers import QueueStatusSerializer
    
    logger.info(f"Running auto_close_queues task at {timezone.now()}")
    
    # Get all open queues
    open_queues = QueueStatus.objects.filter(is_open=True)
    
    closed_count = 0
    checked_count = 0
    
    for queue_status in open_queues:
        checked_count += 1
        
        # Check if queue should be auto-closed
        if queue_status.should_auto_close():
            try:
                old_status = queue_status.is_open
                queue_status.is_open = False
                queue_status.update_status_message()
                queue_status.save()
                
                # Log the automatic closure
                QueueStatusLog.objects.create(
                    department=queue_status.department,
                    previous_status=old_status,
                    new_status=False,
                    change_reason='schedule',
                    changed_by=queue_status.last_updated_by,
                    additional_notes=f'Queue automatically closed at scheduled time by system task'
                )
                
                # Broadcast closure via WebSocket
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'queue_{queue_status.department}',
                        {
                            'type': 'queue_status_update',
                            'status': QueueStatusSerializer(queue_status).data,
                            'previous_status': old_status
                        }
                    )
                    async_to_sync(channel_layer.group_send)(
                        f'queue_{queue_status.department}',
                        {
                            'type': 'queue_notification',
                            'notification': {
                                'event': 'queue_closed',
                                'department': queue_status.department,
                                'message': f"The {queue_status.department} queue has been automatically closed at scheduled time.",
                                'timestamp': timezone.now().isoformat()
                            }
                        }
                    )
                except Exception as e:
                    logger.warning(f"WebSocket broadcast failed for {queue_status.department}: {str(e)}")
                
                closed_count += 1
                logger.info(f"Auto-closed queue {queue_status.department}")
                
            except Exception as e:
                logger.error(f"Error auto-closing queue {queue_status.department}: {str(e)}", exc_info=True)
    
    logger.info(f"Auto-close task completed: Checked {checked_count} queues, closed {closed_count}")
    
    return {
        'checked': checked_count,
        'closed': closed_count,
        'timestamp': timezone.now().isoformat()
    }


@shared_task(name='backend.operations.tasks.retry_failed_notifications')
def retry_failed_notifications():
    """
    Periodic task to retry sending failed notifications.
    Runs every 15 minutes to retry notifications that failed delivery.
    """
    from .models import Notification
    from .async_services import AsyncNotificationService
    import asyncio
    
    logger.info(f"Running retry_failed_notifications task at {timezone.now()}")
    
    try:
        # Get notifications that failed but haven't exceeded max attempts
        failed_notifications = Notification.objects.filter(
            delivery_status=Notification.DELIVERY_FAILED,
            delivery_attempts__lt=3
        )
        
        retry_count = 0
        
        for notification in failed_notifications:
            try:
                # Reset to pending for retry
                notification.delivery_status = Notification.DELIVERY_PENDING
                notification.delivery_attempts += 1
                notification.save()
                
                # Try to send via WebSocket again
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'queue_user_{notification.user.id}',
                        {
                            'type': 'queue_notification',
                            'notification': {
                                'event': 'notification_retry',
                                'message': notification.message,
                                'notification_id': notification.id,
                                'timestamp': timezone.now().isoformat()
                            }
                        }
                    )
                    
                    # Mark as sent
                    notification.delivery_status = Notification.DELIVERY_SENT
                    notification.sent_at = timezone.now()
                    notification.save()
                    retry_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to retry notification {notification.id}: {str(e)}")
                    notification.delivery_status = Notification.DELIVERY_FAILED
                    notification.save()
                    
            except Exception as e:
                logger.error(f"Error processing notification {notification.id}: {str(e)}", exc_info=True)
        
        logger.info(f"Retry task completed: Retried {retry_count} notifications")
        
        return {
            'retried': retry_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in retry_failed_notifications task: {str(e)}", exc_info=True)
        return {'error': str(e)}


@shared_task(name='backend.operations.tasks.update_queue_statistics')
def update_queue_statistics():
    """
    Periodic task to update queue statistics and estimated wait times.
    Runs every 2 minutes to keep queue information current.
    """
    from .models import QueueStatus, QueueManagement
    from datetime import timedelta
    
    logger.info(f"Running update_queue_statistics task at {timezone.now()}")
    
    try:
        # Update all open queues
        open_queues = QueueStatus.objects.filter(is_open=True)
        
        for queue_status in open_queues:
            try:
                # Count waiting patients
                waiting_count = QueueManagement.objects.filter(
                    department=queue_status.department,
                    status='waiting'
                ).count()
                
                # Update statistics
                queue_status.total_waiting = waiting_count
                
                # Calculate estimated wait time (5 minutes per patient as baseline)
                if waiting_count > 0:
                    queue_status.estimated_wait_time = timedelta(minutes=5 * waiting_count)
                else:
                    queue_status.estimated_wait_time = None
                
                queue_status.update_status_message()
                queue_status.save()
                
                # Broadcast updated statistics
                try:
                    from .serializers import QueueStatusSerializer
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'queue_{queue_status.department}',
                        {
                            'type': 'queue_status_update',
                            'status': QueueStatusSerializer(queue_status).data
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to broadcast statistics for {queue_status.department}: {str(e)}")
                    
            except Exception as e:
                logger.error(f"Error updating statistics for {queue_status.department}: {str(e)}", exc_info=True)
        
        logger.info(f"Queue statistics updated for {open_queues.count()} queues")
        
        return {
            'updated': open_queues.count(),
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in update_queue_statistics task: {str(e)}", exc_info=True)
        return {'error': str(e)}


