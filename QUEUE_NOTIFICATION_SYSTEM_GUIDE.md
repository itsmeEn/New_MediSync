# Patient Queue Notification System - Implementation Guide

## Overview

This document describes the comprehensive patient queue notification system implemented for the healthcare application. The system provides real-time notifications to patients when queues are opened, persistent status management, and automatic queue closing based on schedules.

## Features Implemented

### 1. Real-Time Notification System ✓

When nurses open a queue in their module, the system:
- Automatically creates persistent notification records for ALL patient users in the database
- Sends real-time WebSocket notifications to connected patients
- Tracks delivery status and attempts for each notification
- Provides confirmation of notification delivery

**Implementation Details:**
- Notifications are stored in the `Notification` model with delivery tracking
- WebSocket broadcasting via Django Channels for real-time updates
- Async notification service (`AsyncNotificationService`) for efficient bulk notifications

### 2. Queue Status Updates ✓

The system immediately updates queue status when nurses activate it:
- Updates `QueueStatus.is_open` field to `True`
- Updates status message for patients
- Links to the current schedule
- Creates audit logs for all status changes
- Broadcasts status changes via WebSocket to all connected clients

**Implementation Details:**
- `QueueStatus` model tracks real-time status per department
- `QueueStatusLog` model maintains audit trail
- Status visible to all patients attempting to join

### 3. Persistence Requirements ✓

Queue status persists until scheduled closing time:
- Status maintained in database across server restarts
- Automatic closing based on `QueueSchedule.end_time`
- Manual override support for authorized staff
- Background tasks check and enforce schedule compliance

**Implementation Details:**
- Database-backed persistence via `QueueStatus` model
- Linked to `QueueSchedule` for time-based control
- Celery periodic tasks enforce schedule compliance

### 4. Implementation Requirements ✓

The system includes:
- Real-time synchronization between nurse actions and patient notifications
- WebSocket consumers for live updates
- Comprehensive error handling with logging
- Retry mechanisms for failed notifications
- Delivery confirmation and tracking
- Automated testing suite

## Architecture

### Models

#### `QueueStatus`
- Tracks real-time queue status per department
- Links to active schedule
- Maintains statistics (waiting count, estimated wait time)
- Provides methods for auto-closing

```python
# Key methods:
- update_status_message()  # Updates display message
- should_auto_close()      # Checks if past scheduled time
- auto_close_if_needed()   # Closes queue if needed
```

#### `Notification`
- Stores notification records
- Tracks delivery status (pending, sent, delivered, failed)
- Records delivery attempts and timestamps
- Supports multiple channels (WebSocket, email, SMS, push)

#### `QueueSchedule`
- Defines queue operating hours
- Supports day-of-week scheduling
- Includes manual override capability

#### `QueueStatusLog`
- Audit trail of all queue status changes
- Records who made changes and why
- Timestamps all modifications

### Services

#### `AsyncNotificationService`
Located in `backend/operations/async_services.py`

Key methods:
- `send_notification_to_all_patients()` - Sends notifications to all patient users
- `mark_notification_delivered()` - Confirms delivery
- `retry_failed_notifications()` - Retries failed sends

### WebSocket Consumers

#### `QueueStatusConsumer`
Located in `backend/operations/consumers.py`

Handles real-time communication:
- Connects patients to department-specific channels
- Broadcasts queue status updates
- Sends queue notifications
- Confirms notification delivery

### Periodic Tasks

#### `auto_close_queues`
- Runs every 5 minutes
- Checks all open queues against schedules
- Automatically closes queues past end time
- Broadcasts closure notifications

#### `retry_failed_notifications`
- Runs every 15 minutes
- Retries notifications that failed delivery
- Limited to 3 attempts per notification

#### `update_queue_statistics`
- Runs every 2 minutes
- Updates waiting counts and estimated wait times
- Broadcasts updated statistics

## API Endpoints

### Queue Status Management

**POST /operations/queue/status/**
- Opens or closes a queue
- Requires nurse authentication
- Sends notifications when opening
- Returns notification statistics

Request:
```json
{
  "department": "OPD",
  "is_open": true
}
```

Response:
```json
{
  "message": "Queue opened successfully",
  "status": {
    "id": 1,
    "department": "OPD",
    "is_open": true,
    "total_waiting": 0,
    "status_message": "Queue Open - Ready to Join",
    ...
  },
  "notification_stats": {
    "total_patients_notified": 42,
    "notification_failures": 0
  }
}
```

**GET /operations/queue/status/**
- Retrieves queue status for all departments or specific department
- Available to all authenticated users

**GET /operations/queue/status/logs/**
- Retrieves audit logs of queue status changes
- Useful for analytics and debugging

## WebSocket Connections

### Patient Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/queue/OPD/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'queue_notification') {
    // Handle queue notification
    console.log(data.notification.message);
  } else if (data.type === 'queue_status_update') {
    // Handle status update
    console.log('Queue status:', data.status);
  }
};
```

### Notification Events

**queue_notification**
```json
{
  "type": "queue_notification",
  "notification": {
    "event": "queue_opened",
    "department": "OPD",
    "message": "The OPD queue is now OPEN! You can now join the queue.",
    "timestamp": "2025-10-17T23:00:00Z"
  }
}
```

**queue_status_update**
```json
{
  "type": "queue_status_update",
  "status": {
    "department": "OPD",
    "is_open": true,
    "total_waiting": 5,
    "status_message": "Queue Open - 5 waiting"
  }
}
```

## Management Commands

### Auto-Close Queues
Manually trigger queue auto-closing:

```bash
# Check all queues
python manage.py auto_close_queues

# Check specific department
python manage.py auto_close_queues --department OPD

# Dry run (show what would be closed)
python manage.py auto_close_queues --dry-run
```

## Testing

### Running the Test Suite

```bash
python test_queue_notification_system.py
```

The test suite verifies:
1. ✓ Queue opening sends notifications to all patients
2. ✓ Notifications are persisted in database
3. ✓ Queue status updates correctly
4. ✓ Status persists and can be queried
5. ✓ Automatic queue closing works based on schedule
6. ✓ Notification delivery tracking functions
7. ✓ Error handling and recovery mechanisms

### Test Output

```
============================================================
  Patient Queue Notification System - Test Suite
============================================================

============================================================
Test 1: Queue Opening with Patient Notifications
============================================================

ℹ Creating test patients...
✓ Created 5 test patients
ℹ Opening queue...
✓ Notifications sent: 5
✓ All 5 patients received notifications
✓ Notifications have correct message content
✓ Queue status is OPEN

Results:
  Passed: 15/15
  Failed: 0/15
  Warnings: 0

✓ ALL TESTS PASSED!
```

## Celery Configuration

The periodic tasks are configured in `backend/celery.py`:

```python
app.conf.beat_schedule = {
    'auto-close-queues': {
        'task': 'backend.operations.tasks.auto_close_queues',
        'schedule': 300.0,  # Every 5 minutes
    },
    'retry-failed-notifications': {
        'task': 'backend.operations.tasks.retry_failed_notifications',
        'schedule': 900.0,  # Every 15 minutes
    },
    'update-queue-statistics': {
        'task': 'backend.operations.tasks.update_queue_statistics',
        'schedule': 120.0,  # Every 2 minutes
    },
}
```

### Starting Celery

```bash
# Start Celery worker
celery -A backend worker --loglevel=info

# Start Celery Beat (scheduler)
celery -A backend beat --loglevel=info

# Or combine both
celery -A backend worker --beat --loglevel=info
```

## Error Handling

### Notification Failures
- Failed notifications are marked with `DELIVERY_FAILED` status
- Retry mechanism attempts delivery up to 3 times
- Errors are logged with full stack traces
- System continues operation even if some notifications fail

### Queue Status Errors
- Invalid department requests return 404 errors
- Authorization failures return 403 errors
- Database errors are caught and logged
- WebSocket failures don't affect REST API responses

### Logging
All operations are logged at appropriate levels:
- INFO: Normal operations, notifications sent, queues closed
- WARNING: Retry attempts, WebSocket failures, missing schedules
- ERROR: Database errors, unexpected exceptions

## Database Schema

### Key Tables

**notifications**
- Stores all notification records
- Tracks delivery status and timestamps
- Links to users (patients, doctors, nurses)

**queue_status**
- One record per department
- Tracks real-time queue state
- Links to current schedule

**queue_status_logs**
- Audit trail of status changes
- Records who, what, when, why

**queue_schedules**
- Defines operating hours per department
- Supports recurring schedules
- Enables manual overrides

## Security Considerations

1. **Authorization**: Only nurses can open/close queues
2. **User-Specific Notifications**: Patients only receive their own notifications via WebSocket user groups
3. **Audit Logging**: All status changes are logged with user attribution
4. **Input Validation**: All API inputs are validated before processing

## Performance Considerations

1. **Async Notifications**: Uses asyncio for efficient bulk notification creation
2. **WebSocket Groups**: Department-based groups for efficient broadcasting
3. **Database Indexing**: Indexed fields for fast queries
4. **Celery Tasks**: Background processing doesn't block API responses
5. **Connection Pooling**: Django Channels uses connection pooling for WebSockets

## Troubleshooting

### Notifications Not Sending
1. Check Celery is running: `celery -A backend worker --loglevel=info`
2. Check WebSocket connection in browser console
3. Verify user has 'patient' role
4. Check notification logs: `Notification.objects.filter(delivery_status='failed')`

### Queue Not Auto-Closing
1. Verify Celery Beat is running
2. Check schedule configuration: `QueueSchedule.objects.filter(is_active=True)`
3. Check for manual override: `queue_status.current_schedule.manual_override`
4. Run manual command: `python manage.py auto_close_queues --dry-run`

### WebSocket Connection Issues
1. Check Django Channels is configured correctly
2. Verify ASGI server is running (Daphne/Uvicorn)
3. Check firewall/network settings
4. Verify WebSocket URL format: `ws://host:port/ws/queue/{department}/`

## Future Enhancements

Potential improvements:
1. SMS/Email notification channels
2. Push notifications for mobile apps
3. Priority queue notifications
4. Scheduled queue opening (not just closing)
5. Patient notification preferences
6. Multi-language notification support
7. Notification read receipts
8. Analytics dashboard for notification delivery rates

## Support

For issues or questions:
1. Check the test suite: `python test_queue_notification_system.py`
2. Review logs in `backend/logs/`
3. Check Celery logs for task execution
4. Verify database migrations are applied

## Changelog

### Version 1.0.0 (2025-10-17)
- Initial implementation
- Real-time WebSocket notifications
- Persistent notification storage
- Automatic queue closing
- Delivery tracking and retries
- Comprehensive test suite
- Management commands
- Celery periodic tasks


