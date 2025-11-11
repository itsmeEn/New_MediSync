#!/usr/bin/env python
"""
Test script to simulate the actual API call to get_available_doctors
"""
import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.operations.views import get_available_doctors
from backend.users.models import PatientProfile

User = get_user_model()

def test_api_endpoint():
    """Test the actual get_available_doctors API endpoint"""
    print("=== Testing get_available_doctors API Endpoint ===")
    
    # Get a patient user to simulate the request
    patient_user = User.objects.filter(role='patient').first()
    if not patient_user:
        print("No patient user found!")
        return
    
    print(f"Using patient: {patient_user.full_name}")
    print(f"Patient verification status: {patient_user.verification_status}")
    
    # Check patient profile
    try:
        patient_profile = PatientProfile.objects.get(user=patient_user)
        print(f"Patient hospital: {patient_profile.hospital}")
    except PatientProfile.DoesNotExist:
        print("Patient profile not found!")
        return
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/operations/get-available-doctors/', {
        'department': 'general-medicine'
    })
    request.user = patient_user
    
    # Call the API
    try:
        response = get_available_doctors(request)
        print(f"\nAPI Response Status: {response.status_code}")
        print(f"Response Data: {response.data}")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    test_api_endpoint()