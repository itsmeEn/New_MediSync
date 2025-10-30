from django.urls import path
from . import views

urlpatterns = [
    # Main analytics endpoints
    path('', views.AnalyticsView.as_view(), name='analytics'),
    path('status/<str:task_id>/', views.get_analytics_status, name='analytics_status'),
    path('history/', views.get_analytics_history, name='analytics_history'),
    path('refresh/', views.trigger_data_refresh, name='trigger_refresh'),
    path('realtime/', views.get_real_time_analytics, name='real_time_analytics'),
    path('stream/', views.analytics_stream, name='analytics_stream'),
    path('performance/', views.system_performance, name='system_performance'),
    path('stress-test/', views.stress_test_analytics, name='stress_test_analytics'),
    
    # Role-specific analytics endpoints
    path('doctor/', views.doctor_analytics, name='doctor_analytics'),
    path('nurse/', views.nurse_analytics, name='nurse_analytics'),
    # AI recommendation endpoints
    path('doctor/recommendations/', views.doctor_recommendations, name='doctor_recommendations'),
    path('nurse/recommendations/', views.nurse_recommendations, name='nurse_recommendations'),
    
    # PDF report generation
    path('pdf/', views.generate_analytics_pdf, name='generate_analytics_pdf'),
]
