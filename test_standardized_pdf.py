#!/usr/bin/env python
"""
Test script for the standardized PDF analytics report template
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.append('/Users/judeibardaloza/Desktop/medisync')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.http import HttpResponse
from backend.analytics.views import (
    get_hospital_information, 
    get_custom_styles, 
    create_standardized_pdf_template,
    add_standardized_header,
    add_analytics_dashboard,
    add_standardized_footer
)

def test_pdf_generation():
    """Test the standardized PDF generation functionality"""
    print("Testing standardized PDF generation...")
    
    try:
        # Create a mock response object
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="test_analytics_report.pdf"'
        
        # Mock user info for testing
        mock_user = type('MockUser', (), {
            'full_name': 'Dr. John Smith',
            'role': 'Doctor',
            'email': 'john.smith@hospital.com'
        })()
        
        # Test hospital information retrieval
        hospital_info = get_hospital_information(mock_user)
        print(f"✓ Hospital info retrieved: {hospital_info['name']}")
        
        # Test custom styles
        styles = get_custom_styles()
        print(f"✓ Custom styles created: {len(styles.byName)} styles available")
        
        # Test user info structure
        user_info = {
            'name': mock_user.full_name,
            'role': 'Doctor',
            'department': 'Cardiology'
        }
        
        # Test PDF template creation
        doc = create_standardized_pdf_template(response, hospital_info, user_info)
        print("✓ PDF template created successfully")
        
        # Test story creation with all sections
        story = []
        
        # Test header
        add_standardized_header(story, hospital_info, user_info, "Analytics Report", styles)
        print("✓ Header section added")
        
        # Test analytics dashboard with mock data
        mock_analytics_data = {
            'patient_demographics': {
                'total_patients': 150,
                'age_distribution': {'18-30': 25, '31-50': 40, '51-70': 35}
            },
            'health_trends': {
                'common_conditions': ['Hypertension', 'Diabetes', 'Heart Disease']
            },
            'illness_prediction': {
                'risk_factors': ['Age', 'BMI', 'Blood Pressure', 'Cholesterol']
            }
        }
        
        add_analytics_dashboard(story, mock_analytics_data, user_info, styles)
        print("✓ Analytics dashboard added")
        
        # Test footer
        add_standardized_footer(story, styles)
        print("✓ Footer section added")
        
        # Build the PDF
        doc.build(story)
        print("✓ PDF built successfully")
        
        # Save test PDF to file
        with open('/Users/judeibardaloza/Desktop/medisync/test_analytics_report.pdf', 'wb') as f:
            f.write(response.content)
        
        print("✓ Test PDF saved as 'test_analytics_report.pdf'")
        print("\n🎉 All tests passed! Standardized PDF template is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during PDF generation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_nurse_pdf():
    """Test PDF generation for nurse role"""
    print("\nTesting nurse-specific PDF generation...")
    
    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="test_nurse_analytics_report.pdf"'
        
        # Mock nurse user
        mock_nurse = type('MockUser', (), {
            'full_name': 'Nurse Jane Doe',
            'role': 'Nurse',
            'email': 'jane.doe@hospital.com'
        })()
        
        hospital_info = get_hospital_information(mock_nurse)
        styles = get_custom_styles()
        
        user_info = {
            'name': mock_nurse.full_name,
            'role': 'Nurse',
            'department': 'Emergency'
        }
        
        doc = create_standardized_pdf_template(response, hospital_info, user_info)
        story = []
        
        add_standardized_header(story, hospital_info, user_info, "Analytics Report", styles)
        
        # Mock nurse-specific analytics data
        mock_nurse_data = {
            'patient_demographics': {
                'total_patients': 75
            },
            'medication_analysis': {
                'total_medications': 200,
                'medication_categories': {'Antibiotics': 50, 'Pain Relief': 75, 'Cardiac': 75}
            },
            'volume_prediction': {
                'predicted_volume': 85
            }
        }
        
        add_analytics_dashboard(story, mock_nurse_data, user_info, styles)
        add_standardized_footer(story, styles)
        
        doc.build(story)
        
        with open('/Users/judeibardaloza/Desktop/medisync/test_nurse_analytics_report.pdf', 'wb') as f:
            f.write(response.content)
        
        print("✓ Nurse PDF test completed successfully")
        print("✓ Test PDF saved as 'test_nurse_analytics_report.pdf'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during nurse PDF test: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("STANDARDIZED PDF ANALYTICS REPORT TEST")
    print("=" * 60)
    
    # Test doctor PDF
    doctor_success = test_pdf_generation()
    
    # Test nurse PDF
    nurse_success = test_nurse_pdf()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Doctor PDF Test: {'✓ PASSED' if doctor_success else '❌ FAILED'}")
    print(f"Nurse PDF Test: {'✓ PASSED' if nurse_success else '❌ FAILED'}")
    
    if doctor_success and nurse_success:
        print("\n🎉 ALL TESTS PASSED! The standardized PDF template is ready for production.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")