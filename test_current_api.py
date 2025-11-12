#!/usr/bin/env python
"""
Test script to verify the current get_available_doctors API behavior
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db.models import Q
from backend.users.models import GeneralDoctorProfile

def test_department_filtering():
    """Test the current department filtering logic"""
    print("=== Testing Current Department Filtering Logic ===")
    
    # Get the doctor we know exists
    doctor = GeneralDoctorProfile.objects.filter(
        user__full_name="Eucliffe Strauss"
    ).first()
    
    if doctor:
        print(f"Found doctor: {doctor.user.full_name}")
        print(f"Specialization: {doctor.specialization}")
        print(f"Hospital: {doctor.user.hospital_name}")
        print(f"Verification Status: {doctor.user.verification_status}")
        print(f"Is Active: {doctor.user.is_active}")
        print(f"Available for Consultation: {doctor.available_for_consultation}")
    else:
        print("Doctor not found!")
        return
    
    print("\n=== Testing Department Filter Logic ===")
    
    # Test the current filtering logic from get_available_doctors
    department = "general-medicine"
    dept_slug = str(department).strip().lower()
    
    # Department mapping from the current code
    dept_map = {
        'general-medicine': ['general', 'internal medicine', 'primary care'],
        'cardiology': ['cardiology', 'cardiologist'],
        'dermatology': ['dermatology', 'dermatologist'],
        'orthopedics': ['orthopedics', 'orthopaedic', 'orthopedic'],
        'pediatrics': ['pediatrics', 'pediatrician'],
        'gynecology': ['gynecology', 'obstetrics', 'ob-gyn', 'obgyn'],
        'neurology': ['neurology', 'neurologist'],
        'oncology': ['oncology', 'oncologist'],
        'optometrist': ['optometry', 'optometrist', 'eye care', 'ophthalmology', 'ophthalmologist'],
        'emergency-medicine': ['emergency', 'emergency medicine']
    }
    
    keywords = dept_map.get(dept_slug, [])
    print(f"Department slug: {dept_slug}")
    print(f"Keywords: {keywords}")
    
    # Build the same Q object as in the current code
    q = Q(
        specialization__iexact=dept_slug
    ) | Q(
        specialization__icontains=dept_slug
    ) | Q(
        specialization__icontains=dept_slug.replace('-', ' ')
    ) | Q(
        specialization__icontains=dept_slug.replace('-', '_')
    )
    for kw in keywords:
        q |= Q(specialization__icontains=kw)
    
    print(f"\nBuilt Q object: {q}")
    
    # Test the filter
    doctors_query = GeneralDoctorProfile.objects.filter(
        user__verification_status='approved',
        user__is_active=True,
        available_for_consultation=True
    ).filter(q)
    
    print(f"\nFiltered doctors count: {doctors_query.count()}")
    for doc in doctors_query:
        print(f"- {doc.user.full_name}: {doc.specialization}")

if __name__ == "__main__":
    test_department_filtering()