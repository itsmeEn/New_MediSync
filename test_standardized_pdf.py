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
    add_analytics_sections_with_visualizations,
    add_ai_interpretation_section,
    add_doctor_signature,
    add_standardized_footer
)
from reportlab.platypus import Paragraph, Spacer, PageBreak

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
        
        # Mock analytics data for sections
        mock_analytics_data = {
            'patient_demographics': {
                'total_patients': 150,
                'age_distribution': {'18-30': 25, '31-50': 40, '51-70': 35},
                'gender_proportions': {'Male': 52, 'Female': 48}
            },
            'health_trends': {
                'top_illnesses_by_week': [
                    {'medical_condition': 'Hypertension', 'count': 42},
                    {'medical_condition': 'Diabetes', 'count': 28},
                    {'medical_condition': 'Heart Disease', 'count': 18}
                ],
                'common_conditions': [
                    {'condition': 'Hypertension'},
                    {'condition': 'Diabetes'},
                    {'condition': 'Heart Disease'}
                ]
            },
            'medication_analysis': {
                'medication_pareto_data': [
                    {'medication': 'Atorvastatin', 'frequency': 120},
                    {'medication': 'Metformin', 'frequency': 95},
                    {'medication': 'Lisinopril', 'frequency': 80}
                ]
            },
            'illness_prediction': {
                'association_result': 'Strong association detected between BMI and hypertension',
                'chi_square_statistic': 27.5,
                'p_value': 0.004
            },
            'volume_prediction': {
                'evaluation_metrics': {'mae': 2.4, 'rmse': 3.1}
            },
            'surge_prediction': {
                'forecasted_monthly_cases': [
                    {'date': '2025-11', 'total_cases': 45},
                    {'date': '2025-12', 'total_cases': 52},
                    {'date': '2026-01', 'total_cases': 49}
                ]
            }
        }
        
        # Overview and sections using new layout
        story.append(Paragraph("Overview:", styles['SectionHeaderNoBorder']))
        story.append(Paragraph(
            "This report provides comprehensive analytics insights for healthcare management. "
            "It integrates patient demographics, health trends, medication patterns, and forecasting "
            "to support evidence-based decisions and improve patient care outcomes.",
            styles['ContentText']
        ))
        
        # New analytics sections and AI recommendations
        add_analytics_sections_with_visualizations(story, mock_analytics_data, styles)
        add_ai_interpretation_section(story, mock_analytics_data, styles)
        
        # Prepared by signature
        add_doctor_signature(story, user_info, styles)
        
        # Footer
        add_standardized_footer(story, styles)
        print("✓ Sections, AI recommendations, signature, and footer added")
        
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
        
        # Mock analytics data for nurse report
        mock_nurse_data = {
            'patient_demographics': {
                'total_patients': 150,
                'age_distribution': {'18-30': 25, '31-50': 40, '51-70': 35},
                'gender_proportions': {'Male': 52, 'Female': 48}
            },
            'health_trends': {
                'top_illnesses_by_week': [
                    {'medical_condition': 'Hypertension', 'count': 42},
                    {'medical_condition': 'Diabetes', 'count': 28},
                    {'medical_condition': 'Heart Disease', 'count': 18}
                ],
                'common_conditions': [
                    {'condition': 'Hypertension'},
                    {'condition': 'Diabetes'},
                    {'condition': 'Heart Disease'}
                ]
            },
            'medication_analysis': {
                'medication_pareto_data': [
                    {'medication': 'Atorvastatin', 'frequency': 120},
                    {'medication': 'Metformin', 'frequency': 95},
                    {'medication': 'Lisinopril', 'frequency': 80}
                ]
            },
            'illness_prediction': {
                'association_result': 'Strong association detected between BMI and hypertension',
                'chi_square_statistic': 27.5,
                'p_value': 0.004
            },
            'volume_prediction': {
                'evaluation_metrics': {'mae': 2.4, 'rmse': 3.1}
            },
            'surge_prediction': {
                'forecasted_monthly_cases': [
                    {'date': '2025-11', 'total_cases': 45},
                    {'date': '2025-12', 'total_cases': 52},
                    {'date': '2026-01', 'total_cases': 49}
                ]
            }
        }
        
        # Overview and sections using new layout
        story.append(Paragraph("Overview:", styles['SectionHeaderNoBorder']))
        story.append(Paragraph(
            "This report summarizes key analytics insights tailored for nursing operations, "
            "including patient demographics, health trend monitoring, medication utilization patterns, "
            "and forecasting insights to support daily clinical decision-making.",
            styles['ContentText']
        ))
        
        # New analytics sections and AI recommendations
        add_analytics_sections_with_visualizations(story, mock_nurse_data, styles)
        add_ai_interpretation_section(story, mock_nurse_data, styles)
        
        # Prepared by signature
        add_doctor_signature(story, user_info, styles)
        
        # Footer
        add_standardized_footer(story, styles)
        print("✓ Nurse sections, AI recommendations, signature, and footer added")
        
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