from django.core.management.base import BaseCommand
from django.utils import timezone
from backend.analytics.models import AnalyticsResult
import json
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populate database with mock analytics results for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing analytics results before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            AnalyticsResult.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing analytics results'))

        # Create mock analytics results
        self.create_patient_demographics()
        self.create_illness_prediction()
        self.create_health_trends()
        self.create_surge_prediction()

        self.stdout.write(
            self.style.SUCCESS('Successfully created mock analytics results!')
        )

    def create_patient_demographics(self):
        """Create patient demographics analytics result"""
        demographics_data = {
            'age_distribution': {
                '0-18': random.randint(20, 50),
                '19-35': random.randint(30, 80),
                '36-50': random.randint(25, 60),
                '51-65': random.randint(15, 40),
                '65+': random.randint(10, 30)
            },
            'gender_proportions': {
                'Male': random.randint(40, 60),
                'Female': random.randint(40, 60)
            },
            'total_patients': random.randint(100, 500),
            'average_age': round(random.uniform(25, 65), 1)
        }

        AnalyticsResult.objects.create(
            analysis_type='patient_demographics',
            status='completed',
            results=demographics_data,
            created_at=timezone.now() - timedelta(hours=1)
        )

    def create_illness_prediction(self):
        """Create illness prediction analytics result"""
        prediction_data = {
            'association_result': 'Strong positive association found between age and chronic conditions',
            'chi_square_statistic': round(random.uniform(15.0, 45.0), 2),
            'p_value': round(random.uniform(0.001, 0.05), 4),
            'confidence_level': 95,
            'significant_factors': [
                'Age (p < 0.001)',
                'Family history (p < 0.01)',
                'Lifestyle factors (p < 0.05)'
            ]
        }

        AnalyticsResult.objects.create(
            analysis_type='illness_prediction',
            status='completed',
            results=prediction_data,
            created_at=timezone.now() - timedelta(hours=2)
        )

    def create_health_trends(self):
        """Create health trends analytics result"""
        conditions = [
            'Hypertension', 'Diabetes', 'Heart Disease', 'Asthma', 'Arthritis',
            'Depression', 'Anxiety', 'Obesity', 'High Cholesterol', 'Migraine'
        ]
        
        trends_data = {
            'top_illnesses_by_week': [
                {
                    'medical_condition': condition,
                    'count': random.randint(5, 25),
                    'week': f'Week {i+1}'
                }
                for i, condition in enumerate(conditions[:5])
            ],
            'trend_analysis': {
                'increasing_conditions': ['Diabetes', 'Hypertension', 'Depression'],
                'decreasing_conditions': ['Asthma', 'Migraine'],
                'stable_conditions': ['Heart Disease', 'Arthritis']
            },
            'seasonal_patterns': {
                'winter': ['Flu', 'Cold', 'Depression'],
                'summer': ['Heat stroke', 'Dehydration', 'Sunburn'],
                'spring': ['Allergies', 'Asthma'],
                'fall': ['Seasonal depression', 'Flu']
            }
        }

        AnalyticsResult.objects.create(
            analysis_type='patient_health_trends',
            status='completed',
            results=trends_data,
            created_at=timezone.now() - timedelta(hours=3)
        )

    def create_surge_prediction(self):
        """Create surge prediction analytics result"""
        base_date = datetime.now()
        forecast_data = {
            'forecasted_monthly_cases': [
                {
                    'date': (base_date + timedelta(days=30*i)).strftime('%Y-%m'),
                    'total_cases': random.randint(50, 200),
                    'confidence_interval': {
                        'lower': random.randint(30, 100),
                        'upper': random.randint(100, 300)
                    }
                }
                for i in range(1, 4)
            ],
            'risk_factors': [
                'Seasonal flu outbreak',
                'Increased emergency visits',
                'Staff shortage periods'
            ],
            'recommendations': [
                'Increase staffing during peak months',
                'Stock additional emergency supplies',
                'Implement surge capacity protocols'
            ],
            'model_accuracy': round(random.uniform(85, 95), 1)
        }

        AnalyticsResult.objects.create(
            analysis_type='illness_surge_prediction',
            status='completed',
            results=forecast_data,
            created_at=timezone.now() - timedelta(hours=4)
        )
