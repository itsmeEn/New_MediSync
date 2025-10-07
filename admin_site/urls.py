from django.urls import path
from . import views

urlpatterns = [
    # Root admin URL - redirect to dashboard stats
    path('', views.admin_overview, name='admin_overview'),
    
    # CSRF Token
    path('csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    
    # Authentication
    path('login/', views.admin_login, name='admin_login'),
    path('register/', views.admin_register, name='admin_register'),
    path('verify-email/', views.verify_admin_email, name='verify_admin_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification_email'),
    path('token/refresh/', views.admin_token_refresh, name='admin_token_refresh'),
    
    # Dashboard
    path('dashboard/stats/', views.admin_dashboard_stats, name='admin_dashboard_stats'),
    
    # Verification Management
    path('verifications/', views.verification_requests_list, name='verification_requests_list'),
    path('verifications/<int:verification_id>/accept/', views.accept_verification, name='accept_verification'),
    path('verifications/<int:verification_id>/decline/', views.decline_verification, name='decline_verification'),
    path('verifications/<int:verification_id>/archive/', views.archive_verification, name='archive_verification'),
    path('verifications/<int:verification_id>/update/', views.update_verification, name='update_verification'),
    path('verifications/<int:verification_id>/document/', views.serve_verification_document, name='serve_verification_document'),
    
    # System Logs (Super Admin Only)
    path('logs/', views.system_logs, name='system_logs'),
]
