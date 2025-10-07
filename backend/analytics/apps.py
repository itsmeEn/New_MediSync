from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.analytics'
    
    def ready(self):
        # Import signal handlers when the app is ready
        import backend.analytics.signals
