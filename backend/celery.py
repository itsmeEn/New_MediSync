import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('medisync')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'run-scheduled-analytics': {
        'task': 'backend.analytics.tasks.run_scheduled_analytics',
        'schedule': 3600.0,  # Run every hour
    },
    'cleanup-old-analytics': {
        'task': 'backend.analytics.tasks.cleanup_old_analytics',
        'schedule': 86400.0,  # Run daily
    },
    'refresh-analytics-cache': {
        'task': 'backend.analytics.tasks.refresh_analytics_cache',
        'schedule': 1800.0,  # Run every 30 minutes
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
