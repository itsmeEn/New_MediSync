from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # API endpoints for authentication
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API endpoints for user profiles
    path('profile/', views.get_user_profile, name='get_user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    # Removed: deprecated profile picture upload endpoint
    
    # Verification endpoints
    path('verification/upload/', views.upload_verification_document, name='upload_verification_document'),
    path('verification/verify-now/', views.verify_now, name='verify_now'),
    
    # Password reset endpoints
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password, name='reset_password'),
    
    # Two-Factor Authentication endpoints
    path('2fa/enable/', views.enable_2fa, name='enable_2fa'),
    path('2fa/verify/', views.verify_2fa, name='verify_2fa'),
    path('2fa/disable/', views.disable_2fa, name='disable_2fa'),
    path('2fa/login/verify/', views.verify_2fa_login, name='verify_2fa_login'),
    
    # Patient management endpoints
    path('doctor/patients/', views.get_doctor_patients, name='get_doctor_patients'),
    path('nurse/patients/', views.get_nurse_patients, name='get_nurse_patients'),
    
]