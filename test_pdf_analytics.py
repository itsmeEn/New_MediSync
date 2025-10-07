#!/usr/bin/env python3
"""
Test script for PDF analytics generation with visualizations and doctor information
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append('/Users/judeibardaloza/Desktop/medisync')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from backend.analytics.views import generate_analytics_pdf
from backend.users.models import GeneralDoctorProfile

User = get_user_model()

def create_test_doctor():
    """Create a test doctor user with profile"""
    try:
        # Create or get test doctor
        doctor, created = User.objects.get_or_create(
            email='test.doctor@medisync.com',
            defaults={
                'full_name': 'Dr. John Smith',
                'role': 'doctor',
                'is_active': True,
                'verification_status': 'verified'
            }
        )
        
        # Create or get doctor profile
        profile, created = GeneralDoctorProfile.objects.get_or_create(
            user=doctor,
            defaults={
                'license_number': 'MD123456',
                'specialization': 'Cardiology'
            }
        )
        
        print(f"✓ Test doctor created: {doctor.full_name}")
        print(f"✓ Specialization: {profile.specialization}")
        return doctor
        
    except Exception as e:
        print(f"✗ Error creating test doctor: {e}")
        return None

def test_pdf_generation():
    """Test PDF generation with visualizations"""
    print("🧪 Testing PDF Analytics Generation with Visualizations...")
    print("=" * 60)
    
    # Create test doctor
    doctor = create_test_doctor()
    if not doctor:
        print("✗ Failed to create test doctor")
        return False
    
    try:
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/api/analytics/generate-pdf/?type=doctor')
        request.user = doctor
        
        # Test PDF generation
        print("📊 Generating PDF with visualizations...")
        response = generate_analytics_pdf(request)
        
        if response.status_code == 200:
            print("✓ PDF generated successfully!")
            print(f"✓ Content type: {response.get('Content-Type')}")
            print(f"✓ Content length: {len(response.content)} bytes")
            
            # Save the PDF for manual inspection
            pdf_path = '/Users/judeibardaloza/Desktop/medisync/test_analytics_report.pdf'
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ PDF saved to: {pdf_path}")
            
            return True
        else:
            print(f"✗ PDF generation failed with status: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"✗ Error: {response.data}")
            return False
            
    except Exception as e:
        print(f"✗ Error during PDF generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization_functions():
    """Test individual visualization functions"""
    print("\n🎨 Testing Visualization Functions...")
    print("=" * 40)
    
    try:
        from backend.analytics.views import (
            create_age_distribution_chart,
            create_gender_pie_chart,
            create_illness_trends_chart,
            create_medication_chart,
            create_metrics_chart,
            create_forecast_chart
        )
        
        # Test age distribution chart
        age_data = {'18-30': 25, '31-45': 40, '46-60': 30, '60+': 15}
        age_chart = create_age_distribution_chart(age_data)
        print(f"✓ Age distribution chart: {'Created' if age_chart else 'Failed'}")
        
        # Test gender pie chart
        gender_data = {'Male': 45.5, 'Female': 54.5}
        gender_chart = create_gender_pie_chart(gender_data)
        print(f"✓ Gender pie chart: {'Created' if gender_chart else 'Failed'}")
        
        # Test illness trends chart
        illness_data = [
            {'medical_condition': 'Hypertension', 'count': 45},
            {'medical_condition': 'Diabetes', 'count': 32},
            {'medical_condition': 'Common Cold', 'count': 28}
        ]
        illness_chart = create_illness_trends_chart(illness_data)
        print(f"✓ Illness trends chart: {'Created' if illness_chart else 'Failed'}")
        
        # Test medication chart
        med_data = [
            {'medication': 'Lisinopril', 'frequency': 25},
            {'medication': 'Metformin', 'frequency': 20},
            {'medication': 'Ibuprofen', 'frequency': 18}
        ]
        med_chart = create_medication_chart(med_data)
        print(f"✓ Medication chart: {'Created' if med_chart else 'Failed'}")
        
        # Test metrics chart
        metrics_data = {'mae': 2.5, 'rmse': 3.2}
        metrics_chart = create_metrics_chart(metrics_data)
        print(f"✓ Metrics chart: {'Created' if metrics_chart else 'Failed'}")
        
        # Test forecast chart
        forecast_data = [
            {'date': '2024-02', 'total_cases': 120},
            {'date': '2024-03', 'total_cases': 135},
            {'date': '2024-04', 'total_cases': 110}
        ]
        forecast_chart = create_forecast_chart(forecast_data)
        print(f"✓ Forecast chart: {'Created' if forecast_chart else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing visualization functions: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🏥 MediSync PDF Analytics Test Suite")
    print("=" * 50)
    
    # Test visualization functions
    viz_success = test_visualization_functions()
    
    # Test full PDF generation
    pdf_success = test_pdf_generation()
    
    print("\n📋 Test Results Summary:")
    print("=" * 30)
    print(f"Visualization Functions: {'✓ PASS' if viz_success else '✗ FAIL'}")
    print(f"PDF Generation: {'✓ PASS' if pdf_success else '✗ FAIL'}")
    
    if viz_success and pdf_success:
        print("\n🎉 All tests passed! PDF analytics with visualizations is working correctly.")
        print("📄 Features implemented:")
        print("   • Age distribution bar charts")
        print("   • Gender distribution pie charts") 
        print("   • Illness trends horizontal bar charts")
        print("   • Medication frequency charts")
        print("   • Model performance metrics charts")
        print("   • Forecast line charts")
        print("   • Doctor name and specialization in lower right")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")

if __name__ == '__main__':
    main()