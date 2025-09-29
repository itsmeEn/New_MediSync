from django.urls import path
from . import views

urlpatterns = [
    # Dashboard statistics
    path('dashboard/stats/', views.doctor_dashboard_stats, name='doctor_dashboard_stats'),
    path('appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('queue/patients/', views.doctor_queue_patients, name='doctor_queue_patients'),
    path('notifications/', views.doctor_notifications, name='doctor_notifications'),
    # path('pending-assessments/', views.doctor_pending_assessments, name='doctor_pending_assessments'),
    
    # Appointment management
    path('blocked-dates/', views.doctor_blocked_dates, name='doctor_blocked_dates'),
    path('block-date/', views.doctor_block_date, name='doctor_block_date'),
    path('create-appointment/', views.doctor_create_appointment, name='doctor_create_appointment'),
    
    # Messaging endpoints
    path('messaging/conversations/', views.get_conversations, name='get_conversations'),
    path('messaging/conversations/create/', views.create_conversation, name='create_conversation'),
    path('messaging/conversations/<int:conversation_id>/messages/', views.get_messages, name='get_messages'),
    path('messaging/conversations/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('messaging/messages/<int:message_id>/react/', views.add_reaction, name='add_reaction'),
    path('messaging/available-users/', views.get_available_users, name='get_available_users'),
    
    # Message notification endpoints
    path('messaging/notifications/', views.get_message_notifications, name='get_message_notifications'),
    path('messaging/notifications/<int:notification_id>/mark-sent/', views.mark_notification_as_sent, name='mark_notification_as_sent'),
    path('messaging/messages/<int:message_id>/mark-read/', views.mark_message_as_read, name='mark_message_as_read'),
    
    # Medicine inventory endpoints
    path('medicine-inventory/', views.get_medicine_inventory, name='get_medicine_inventory'),
    path('medicine-inventory/add/', views.add_medicine, name='add_medicine'),
    path('medicine-inventory/<int:medicine_id>/update/', views.update_medicine, name='update_medicine'),
    path('medicine-inventory/<int:medicine_id>/delete/', views.delete_medicine, name='delete_medicine'),
    
    # Nurse queue endpoints
    path('nurse/queue/patients/', views.nurse_queue_patients, name='nurse_queue_patients'),
    
    # Doctor selection endpoints
    path('available-doctors/', views.get_available_doctors, name='get_available_doctors'),
    path('assign-patient/', views.assign_patient_to_doctor, name='assign_patient_to_doctor'),
    
    # Doctor assignment endpoints
    path('doctor/assignments/', views.get_doctor_assignments, name='get_doctor_assignments'),
    path('doctor/assignments/<int:assignment_id>/accept/', views.accept_assignment, name='accept_assignment'),
    path('doctor/assignments/<int:assignment_id>/consultation-notes/', views.consultation_notes, name='consultation_notes'),
]
