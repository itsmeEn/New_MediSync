from django.core.management.base import BaseCommand
from backend.analytics.models import PatientRecord
from backend.analytics.predictive_analytics import predict_weekly_illness_forecast, predict_monthly_illness_forecast
import pandas as pd

class Command(BaseCommand):
    help = 'Test the new illness prediction functions'

    def handle(self, *args, **options):
        self.stdout.write('Testing illness prediction functions...')
        
        # Get patient data
        patient_queryset = PatientRecord.objects.select_related('patient').all()
        
        if not patient_queryset.exists():
            self.stdout.write(self.style.ERROR('No patient data available for testing'))
            return
        
        # Convert to DataFrame
        df = pd.DataFrame.from_records(patient_queryset.values())
        
        if df.empty:
            self.stdout.write(self.style.ERROR('No data available for testing'))
            return
        
        # Clean and prepare data
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        self.stdout.write('\\n=== WEEKLY ILLNESS FORECAST ===')
        try:
            weekly_results = predict_weekly_illness_forecast(df)
            
            self.stdout.write(f"Total predictions: {weekly_results['summary']['total_predictions']}")
            self.stdout.write(f"High risk illnesses: {weekly_results['summary']['high_risk_illnesses']}")
            self.stdout.write(f"Medium risk illnesses: {weekly_results['summary']['medium_risk_illnesses']}")
            self.stdout.write(f"Low risk illnesses: {weekly_results['summary']['low_risk_illnesses']}")
            
            # Show top 5 predictions
            if weekly_results['weekly_illness_forecast']:
                self.stdout.write('\\nTop 5 Weekly Predictions:')
                for i, prediction in enumerate(weekly_results['weekly_illness_forecast'][:5]):
                    self.stdout.write(f"{i+1}. {prediction['illness']} - Week {prediction['week']} - {prediction['predicted_cases']} cases (Risk: {prediction['risk_level']})")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Weekly forecast error: {str(e)}'))
        
        self.stdout.write('\\n=== MONTHLY ILLNESS FORECAST ===')
        try:
            monthly_results = predict_monthly_illness_forecast(df)
            
            self.stdout.write(f"Total predictions: {monthly_results['summary']['total_predictions']}")
            self.stdout.write(f"Critical risk illnesses: {monthly_results['summary']['critical_risk_illnesses']}")
            self.stdout.write(f"High risk illnesses: {monthly_results['summary']['high_risk_illnesses']}")
            self.stdout.write(f"Medium risk illnesses: {monthly_results['summary']['medium_risk_illnesses']}")
            self.stdout.write(f"Low risk illnesses: {monthly_results['summary']['low_risk_illnesses']}")
            
            # Show top 5 predictions
            if monthly_results['monthly_illness_forecast']:
                self.stdout.write('\\nTop 5 Monthly Predictions:')
                for i, prediction in enumerate(monthly_results['monthly_illness_forecast'][:5]):
                    self.stdout.write(f"{i+1}. {prediction['illness']} - Month {prediction['month']} - {prediction['predicted_cases']} cases (Risk: {prediction['risk_level']}, Trend: {prediction['trend']})")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Monthly forecast error: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('\\nIllness prediction testing completed!'))
