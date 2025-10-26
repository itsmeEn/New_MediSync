from django.apps import AppConfig


class AdminSiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.admin_site'
    verbose_name = 'Admin Site'
