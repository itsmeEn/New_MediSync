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
    path('profile/update/picture/', views.update_profile_picture, name='update_profile_picture'),
    
    # Verification endpoints
    path('verification/upload/', views.upload_verification_document, name='upload_verification_document'),
    path('verification/verify-now/', views.verify_now, name='verify_now'),
    
    # Password reset endpoints
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password, name='reset_password'),
    
    # Patient management endpoints
    path('doctor/patients/', views.get_doctor_patients, name='get_doctor_patients'),
    path('nurse/patients/', views.get_nurse_patients, name='get_nurse_patients'),
    
]