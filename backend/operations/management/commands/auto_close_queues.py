"""
Management command to automatically close queues based on schedules.
This can be run periodically via cron or Celery.
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from backend.operations.models import QueueStatus, QueueStatusLog
from backend.operations.serializers import QueueStatusSerializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Automatically close queues that are past their scheduled end time'

    def add_arguments(self, parser):
        parser.add_argument(
            '--department',
            type=str,
            help='Specific department to check (optional)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be closed without actually closing',
        )

    def handle(self, *args, **options):
        department = options.get('department')
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(f"Running queue auto-close check at {timezone.now()}")
        
        # Get all open queues or specific department
        if department:
            queues = QueueStatus.objects.filter(department=department, is_open=True)
        else:
            queues = QueueStatus.objects.filter(is_open=True)
        
        closed_count = 0
        checked_count = 0
        
        for queue_status in queues:
            checked_count += 1
            
            # Check if queue should be auto-closed
            if queue_status.should_auto_close():
                self.stdout.write(
                    self.style.WARNING(
                        f"Queue {queue_status.department} should be closed (past end time)"
                    )
                )
                
                if not dry_run:
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
                            additional_notes=f'Queue automatically closed at scheduled time'
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
                                        'message': f"Queue has been automatically closed at scheduled time.",
                                        'timestamp': timezone.now().isoformat()
                                    }
                                }
                            )
                        except Exception as e:
                            logger.warning(f"WebSocket broadcast failed for {queue_status.department}: {str(e)}")
                        
                        closed_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Closed queue {queue_status.department}"
                            )
                        )
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"✗ Failed to close queue {queue_status.department}: {str(e)}"
                            )
                        )
                        logger.error(f"Error closing queue {queue_status.department}: {str(e)}", exc_info=True)
                else:
                    self.stdout.write(
                        self.style.NOTICE(
                            f"[DRY RUN] Would close queue {queue_status.department}"
                        )
                    )
            else:
                self.stdout.write(
                    f"Queue {queue_status.department} is within scheduled hours or has manual override"
                )
        
        # Summary
        summary = f"\nChecked {checked_count} open queue(s)"
        if dry_run:
            summary += f", {closed_count} would be closed"
        else:
            summary += f", closed {closed_count} queue(s)"
        
        self.stdout.write(self.style.SUCCESS(summary))
        
        if not dry_run and closed_count > 0:
            logger.info(f"Auto-close: Closed {closed_count} queue(s) at {timezone.now()}")


