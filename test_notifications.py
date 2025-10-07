#!/usr/bin/env python
"""
Test script to verify doctor notification systems are working correctly.
This script tests:
1. Appointment booking notifications
2. Analytics findings notifications  
3. Message notifications
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to Python path
sys.path.append('/Users/judeibardaloza/Desktop/medisync')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.users.models import User
from backend.operations.models import AppointmentManagement, Notification, Message, Conversation
from backend.analytics.models import AnalyticsResult

def test_appointment_notifications():
    """Test that appointment booking creates notifications for doctors"""
    print("🔍 Testing appointment booking notifications...")
    
    try:
        # Get a doctor user
        doctor = User.objects.filter(role='doctor', is_active=True).first()
        if not doctor:
            print("❌ No active doctor found in database")
            return False
            
        # Count existing notifications
        initial_count = Notification.objects.filter(user=doctor).count()
        
        # Create a new appointment
        appointment = AppointmentManagement.objects.create(
            doctor=doctor,
            patient_name="Test Patient",
            appointment_date=datetime.now().date(),
            appointment_time=datetime.now().time(),
            status='scheduled'
        )
        
        # Check if notification was created
        final_count = Notification.objects.filter(user=doctor).count()
        
        if final_count > initial_count:
            latest_notification = Notification.objects.filter(user=doctor).latest('created_at')
            print(f"✅ Appointment notification created: {latest_notification.title}")
            print(f"   Message: {latest_notification.message}")
            return True
        else:
            print("❌ No notification created for appointment booking")
            return False
            
    except Exception as e:
        print(f"❌ Error testing appointment notifications: {str(e)}")
        return False

def test_analytics_notifications():
    """Test that completed analytics create notifications for doctors"""
    print("\n🔍 Testing analytics findings notifications...")
    
    try:
        # Get all doctors
        doctors = User.objects.filter(role='doctor', is_active=True)
        if not doctors.exists():
            print("❌ No active doctors found in database")
            return False
            
        # Count existing notifications for first doctor
        doctor = doctors.first()
        initial_count = Notification.objects.filter(user=doctor, notification_type='analytics').count()
        
        # Create a completed analytics result
        analytics_result = AnalyticsResult.objects.create(
            analysis_type='patient_health_trends',
            status='completed',
            results={'test': 'data'},
            processed_by=doctor
        )
        
        # Check if notifications were created for all doctors
        final_count = Notification.objects.filter(user=doctor, notification_type='analytics').count()
        
        if final_count > initial_count:
            latest_notification = Notification.objects.filter(
                user=doctor, 
                notification_type='analytics'
            ).latest('created_at')
            print(f"✅ Analytics notification created: {latest_notification.title}")
            print(f"   Message: {latest_notification.message}")
            
            # Check if all doctors got notifications
            total_doctors = doctors.count()
            total_new_notifications = Notification.objects.filter(
                notification_type='analytics',
                title='Analytics Findings Available'
            ).count()
            
            print(f"   Notifications sent to {total_new_notifications} doctors (expected: {total_doctors})")
            return True
        else:
            print("❌ No notification created for analytics completion")
            return False
            
    except Exception as e:
        print(f"❌ Error testing analytics notifications: {str(e)}")
        return False

def test_message_notifications():
    """Test that messages create notifications for recipients"""
    print("\n🔍 Testing message notifications...")
    
    try:
        # Get two users (doctor and nurse)
        doctor = User.objects.filter(role='doctor', is_active=True).first()
        nurse = User.objects.filter(role='nurse', is_active=True).first()
        
        if not doctor or not nurse:
            print("❌ Need both doctor and nurse users for message testing")
            return False
            
        # Create or get conversation
        conversation, created = Conversation.objects.get_or_create(
            defaults={'created_at': datetime.now()}
        )
        conversation.participants.add(doctor, nurse)
        
        # Count existing notifications
        initial_count = Notification.objects.filter(user=nurse).count()
        
        # Create a message from doctor to nurse
        message = Message.objects.create(
            conversation=conversation,
            sender=doctor,
            content="Test message for notification",
            timestamp=datetime.now()
        )
        
        # The signal should create notifications
        final_count = Notification.objects.filter(user=nurse).count()
        
        if final_count > initial_count:
            print("✅ Message notification system is working")
            return True
        else:
            print("❌ No notification created for message")
            return False
            
    except Exception as e:
        print(f"❌ Error testing message notifications: {str(e)}")
        return False

def main():
    """Run all notification tests"""
    print("🚀 Starting Doctor Notification System Tests")
    print("=" * 50)
    
    results = []
    
    # Test appointment notifications
    results.append(test_appointment_notifications())
    
    # Test analytics notifications
    results.append(test_analytics_notifications())
    
    # Test message notifications
    results.append(test_message_notifications())
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Appointment notifications: {'✅ PASS' if results[0] else '❌ FAIL'}")
    print(f"   Analytics notifications: {'✅ PASS' if results[1] else '❌ FAIL'}")
    print(f"   Message notifications: {'✅ PASS' if results[2] else '❌ FAIL'}")
    
    if all(results):
        print("\n🎉 All notification systems are working correctly!")
        return True
    else:
        print(f"\n⚠️  {sum(results)}/3 notification systems are working")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)