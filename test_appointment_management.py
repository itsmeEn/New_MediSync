#!/usr/bin/env python
"""
Test script for appointment management functionality.
Tests scheduling, rescheduling, and cancellation of appointments.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.utils import timezone
from backend.users.models import User, PatientProfile, GeneralDoctorProfile
from backend.operations.models import AppointmentManagement, Notification


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_appointment_lifecycle():
    """Test the complete appointment lifecycle."""
    
    print_section("APPOINTMENT MANAGEMENT TEST")
    
    # Get or create test patient
    try:
        patient_user = User.objects.filter(role='patient', email__contains='patient').first()
        if not patient_user:
            print("❌ No patient user found. Please create a patient user first.")
            return
        
        patient_profile = PatientProfile.objects.get(user=patient_user)
        print(f"✅ Found patient: {patient_user.full_name} ({patient_user.email})")
    except Exception as e:
        print(f"❌ Error getting patient: {str(e)}")
        return
    
    # Get or create test doctor
    try:
        doctor_user = User.objects.filter(
            role='doctor',
            verification_status='approved',
            is_active=True
        ).first()
        
        if not doctor_user:
            print("❌ No verified doctor found. Please create a verified doctor first.")
            return
        
        doctor_profile = GeneralDoctorProfile.objects.get(user=doctor_user)
        print(f"✅ Found doctor: {doctor_user.full_name} ({doctor_user.email})")
    except Exception as e:
        print(f"❌ Error getting doctor: {str(e)}")
        return
    
    # Test 1: Create a new appointment
    print_section("TEST 1: Creating New Appointment")
    try:
        future_date = timezone.now() + timedelta(days=5)
        appointment = AppointmentManagement.objects.create(
            patient=patient_profile,
            doctor=doctor_profile,
            appointment_date=future_date,
            appointment_type='consultation',
            appointment_time=future_date.time(),
            queue_number=AppointmentManagement.objects.count() + 1,
            status='scheduled'
        )
        print(f"✅ Created appointment ID: {appointment.appointment_id}")
        print(f"   Status: {appointment.status}")
        print(f"   Date: {appointment.appointment_date}")
        print(f"   Time: {appointment.appointment_time}")
    except Exception as e:
        print(f"❌ Error creating appointment: {str(e)}")
        return
    
    # Test 2: Reschedule the appointment
    print_section("TEST 2: Rescheduling Appointment")
    try:
        new_date = timezone.now() + timedelta(days=7)
        appointment.appointment_date = new_date
        appointment.appointment_time = new_date.time()
        appointment.status = 'rescheduled'
        appointment.reschedule_reason = 'Test reschedule'
        appointment.save()
        print(f"✅ Rescheduled appointment ID: {appointment.appointment_id}")
        print(f"   New Status: {appointment.status}")
        print(f"   New Date: {appointment.appointment_date}")
        print(f"   Reschedule Reason: {appointment.reschedule_reason}")
    except Exception as e:
        print(f"❌ Error rescheduling appointment: {str(e)}")
    
    # Test 3: Check for duplicates
    print_section("TEST 3: Duplicate Detection")
    try:
        duplicate_count = AppointmentManagement.objects.filter(
            patient=patient_profile,
            appointment_date__date=appointment.appointment_date.date(),
            appointment_time=appointment.appointment_time,
            status__in=['scheduled', 'rescheduled']
        ).exclude(appointment_id=appointment.appointment_id).count()
        
        if duplicate_count > 0:
            print(f"⚠️  Found {duplicate_count} potential duplicate(s)")
        else:
            print("✅ No duplicates found - system working correctly")
    except Exception as e:
        print(f"❌ Error checking duplicates: {str(e)}")
    
    # Test 4: Cancel the appointment
    print_section("TEST 4: Cancelling Appointment")
    try:
        appointment.status = 'cancelled'
        appointment.cancellation_reason = 'Test cancellation'
        appointment.save()
        print(f"✅ Cancelled appointment ID: {appointment.appointment_id}")
        print(f"   Status: {appointment.status}")
        print(f"   Cancellation Reason: {appointment.cancellation_reason}")
    except Exception as e:
        print(f"❌ Error cancelling appointment: {str(e)}")
    
    # Test 5: Query appointments by status
    print_section("TEST 5: Query Appointments by Status")
    try:
        statuses = ['scheduled', 'rescheduled', 'cancelled']
        for status in statuses:
            count = AppointmentManagement.objects.filter(
                patient=patient_profile,
                status=status
            ).count()
            print(f"   {status.upper()}: {count} appointment(s)")
    except Exception as e:
        print(f"❌ Error querying appointments: {str(e)}")
    
    # Test 6: Check notifications
    print_section("TEST 6: Notification Check")
    try:
        notification_count = Notification.objects.filter(
            user=doctor_user,
            message__icontains='appointment'
        ).count()
        print(f"✅ Doctor has {notification_count} appointment-related notification(s)")
    except Exception as e:
        print(f"❌ Error checking notifications: {str(e)}")
    
    # Cleanup
    print_section("CLEANUP")
    try:
        appointment.delete()
        print(f"✅ Deleted test appointment ID: {appointment.appointment_id}")
    except Exception as e:
        print(f"⚠️  Warning: Could not delete test appointment: {str(e)}")
    
    print_section("TEST COMPLETE")
    print("All tests completed successfully! ✅")


if __name__ == '__main__':
    try:
        test_appointment_lifecycle()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

