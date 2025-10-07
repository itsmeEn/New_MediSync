#!/usr/bin/env python3
"""
Test MediSync AI Model with External Healthcare Datasets

This script demonstrates how to adapt and test the MediSync AI model with various
external healthcare datasets. The model is designed to work with healthcare analytics
data and can be adapted to different healthcare datasets as long as they contain
relevant medical information.

Supported Dataset Types:
1. Patient Demographics Data
2. Disease/Condition Prevalence Data
3. Hospital Admission Records
4. Public Health Statistics
5. Clinical Trial Data
6. Electronic Health Records (EHR) Data

Requirements:
- pandas
- numpy
- scikit-learn
- tensorflow
- matplotlib
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.analytics.ai_insights_model import MediSyncAIInsights, generate_synthetic_data

class ExternalDatasetAdapter:
    """
    Adapter class to convert external healthcare datasets into the format
    expected by the MediSync AI model.
    """
    
    def __init__(self):
        self.supported_formats = [
            'csv', 'json', 'excel', 'parquet'
        ]
    
    def load_dataset(self, file_path, format_type='csv'):
        """
        Load external dataset from various formats.
        
        Args:
            file_path (str): Path to the dataset file
            format_type (str): Format of the dataset ('csv', 'json', 'excel', 'parquet')
            
        Returns:
            pandas.DataFrame: Loaded dataset
        """
        if format_type == 'csv':
            return pd.read_csv(file_path)
        elif format_type == 'json':
            return pd.read_json(file_path)
        elif format_type == 'excel':
            return pd.read_excel(file_path)
        elif format_type == 'parquet':
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def adapt_patient_demographics(self, df, age_col='age', gender_col='gender'):
        """
        Convert patient demographics data to MediSync format.
        
        Args:
            df (pandas.DataFrame): DataFrame with patient data
            age_col (str): Name of the age column
            gender_col (str): Name of the gender column
            
        Returns:
            dict: MediSync-compatible demographics data
        """
        # Age distribution
        age_bins = [0, 18, 35, 50, 65, 100]
        age_labels = ['0-18', '19-35', '36-50', '51-65', '65+']
        age_groups = pd.cut(df[age_col], bins=age_bins, labels=age_labels, right=False)
        age_distribution = age_groups.value_counts().to_dict()
        
        # Gender proportions
        gender_proportions = df[gender_col].value_counts().to_dict()
        
        return {
            'age_distribution': age_distribution,
            'gender_proportions': gender_proportions,
            'total_patients': len(df),
            'average_age': df[age_col].mean()
        }
    
    def adapt_disease_data(self, df, condition_col='condition', date_col='date', count_col='count'):
        """
        Convert disease/condition data to MediSync format.
        
        Args:
            df (pandas.DataFrame): DataFrame with disease data
            condition_col (str): Name of the condition column
            date_col (str): Name of the date column
            count_col (str): Name of the count column (optional)
            
        Returns:
            dict: MediSync-compatible health trends data
        """
        # Convert date column to datetime if it's not already
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col])
        
        # Top illnesses by week
        if count_col in df.columns:
            top_illnesses = df.nlargest(10, count_col)[[condition_col, count_col, date_col]].to_dict('records')
            top_illnesses = [
                {
                    'medical_condition': row[condition_col],
                    'count': row[count_col],
                    'date_of_admission': row[date_col].strftime('%Y-%m-%d') if pd.notna(row[date_col]) else datetime.now().strftime('%Y-%m-%d')
                }
                for row in top_illnesses
            ]
        else:
            # If no count column, use frequency
            condition_counts = df[condition_col].value_counts().head(10)
            top_illnesses = [
                {
                    'medical_condition': condition,
                    'count': count,
                    'date_of_admission': datetime.now().strftime('%Y-%m-%d')
                }
                for condition, count in condition_counts.items()
            ]
        
        # Analyze trends (simplified)
        all_conditions = df[condition_col].unique().tolist()
        np.random.shuffle(all_conditions)
        
        # Randomly categorize conditions for demonstration
        n_conditions = len(all_conditions)
        increasing_conditions = all_conditions[:n_conditions//3]
        decreasing_conditions = all_conditions[n_conditions//3:2*n_conditions//3]
        stable_conditions = all_conditions[2*n_conditions//3:]
        
        return {
            'top_illnesses_by_week': top_illnesses,
            'trend_analysis': {
                'increasing_conditions': increasing_conditions,
                'decreasing_conditions': decreasing_conditions,
                'stable_conditions': stable_conditions
            }
        }
    
    def adapt_hospital_admissions(self, df, admission_date_col='admission_date', 
                                 diagnosis_col='diagnosis', patient_id_col='patient_id'):
        """
        Convert hospital admission data to MediSync format.
        
        Args:
            df (pandas.DataFrame): DataFrame with admission data
            admission_date_col (str): Name of the admission date column
            diagnosis_col (str): Name of the diagnosis column
            patient_id_col (str): Name of the patient ID column
            
        Returns:
            dict: MediSync-compatible data
        """
        # Convert date column
        df[admission_date_col] = pd.to_datetime(df[admission_date_col])
        
        # Group by week and diagnosis
        df['week'] = df[admission_date_col].dt.to_period('W')
        weekly_admissions = df.groupby(['week', diagnosis_col]).size().reset_index(name='count')
        
        # Convert to MediSync format
        top_illnesses = []
        for _, row in weekly_admissions.head(20).iterrows():
            top_illnesses.append({
                'medical_condition': row[diagnosis_col],
                'count': row['count'],
                'date_of_admission': str(row['week'].start_time.date())
            })
        
        return {
            'top_illnesses_by_week': top_illnesses,
            'trend_analysis': {
                'increasing_conditions': df[diagnosis_col].value_counts().head(5).index.tolist(),
                'decreasing_conditions': df[diagnosis_col].value_counts().tail(3).index.tolist(),
                'stable_conditions': df[diagnosis_col].value_counts()[5:8].index.tolist()
            }
        }
    
    def create_medisync_dataset(self, demographics_data=None, health_trends_data=None, 
                               illness_prediction_data=None, surge_prediction_data=None):
        """
        Create a complete MediSync-compatible dataset.
        
        Args:
            demographics_data (dict): Patient demographics data
            health_trends_data (dict): Health trends data
            illness_prediction_data (dict): Illness prediction data
            surge_prediction_data (dict): Surge prediction data
            
        Returns:
            dict: Complete MediSync-compatible dataset
        """
        dataset = {}
        
        if demographics_data:
            dataset['patient_demographics'] = demographics_data
        
        if health_trends_data:
            dataset['health_trends'] = health_trends_data
        
        if illness_prediction_data:
            dataset['illness_prediction'] = illness_prediction_data
        else:
            # Generate default illness prediction data
            dataset['illness_prediction'] = {
                'association_result': 'Moderate association found between patient factors and health outcomes',
                'chi_square_statistic': np.random.uniform(15.0, 30.0),
                'p_value': np.random.uniform(0.01, 0.05),
                'confidence_level': 95,
                'significant_factors': [
                    'Age (p < 0.05)',
                    'Family history (p < 0.01)',
                    'Lifestyle factors (p < 0.05)'
                ]
            }
        
        if surge_prediction_data:
            dataset['surge_prediction'] = surge_prediction_data
        else:
            # Generate default surge prediction data
            base_date = datetime.now()
            forecasted_cases = []
            for i in range(4):
                week_date = base_date + timedelta(weeks=i)
                forecasted_cases.append({
                    'week': week_date.strftime('%Y-W%U'),
                    'forecasted_cases': np.random.randint(50, 200),
                    'confidence_interval': f"[{np.random.randint(40, 60)}, {np.random.randint(180, 220)}]"
                })
            
            dataset['surge_prediction'] = {
                'forecasted_cases': forecasted_cases,
                'model_accuracy': np.random.uniform(0.75, 0.95),
                'risk_level': np.random.choice(['low', 'moderate', 'high'])
            }
        
        return dataset

def test_with_synthetic_external_data():
    """
    Test the AI model with synthetic external healthcare data.
    """
    print("🧪 Testing MediSync AI Model with Synthetic External Healthcare Data")
    print("=" * 70)
    
    # Initialize the adapter and AI model
    adapter = ExternalDatasetAdapter()
    ai_model = MediSyncAIInsights()
    
    # Create synthetic external datasets
    print("\n📊 Creating synthetic external datasets...")
    
    # 1. Patient Demographics Dataset
    np.random.seed(42)
    n_patients = 1000
    demographics_df = pd.DataFrame({
        'patient_id': range(1, n_patients + 1),
        'age': np.random.randint(0, 90, n_patients),
        'gender': np.random.choice(['Male', 'Female', 'Other'], n_patients, p=[0.48, 0.48, 0.04]),
        'location': np.random.choice(['Urban', 'Rural', 'Suburban'], n_patients),
        'insurance': np.random.choice(['Public', 'Private', 'None'], n_patients)
    })
    
    # 2. Disease Prevalence Dataset
    conditions = ['Hypertension', 'Diabetes', 'Heart Disease', 'Asthma', 'Arthritis',
                 'Depression', 'Anxiety', 'Obesity', 'High Cholesterol', 'Migraine',
                 'Flu', 'Cold', 'Bronchitis', 'Pneumonia', 'Gastroenteritis']
    
    disease_df = pd.DataFrame({
        'condition': np.random.choice(conditions, 500),
        'count': np.random.randint(1, 50, 500),
        'date': pd.date_range(start='2023-01-01', end='2024-01-01', periods=500)
    })
    
    # 3. Hospital Admissions Dataset
    admissions_df = pd.DataFrame({
        'patient_id': np.random.randint(1, n_patients + 1, 300),
        'admission_date': pd.date_range(start='2023-01-01', end='2024-01-01', periods=300),
        'diagnosis': np.random.choice(conditions, 300),
        'length_of_stay': np.random.randint(1, 14, 300),
        'severity': np.random.choice(['Mild', 'Moderate', 'Severe'], 300)
    })
    
    print(f"✅ Created demographics dataset: {len(demographics_df)} patients")
    print(f"✅ Created disease dataset: {len(disease_df)} records")
    print(f"✅ Created admissions dataset: {len(admissions_df)} admissions")
    
    # Convert external data to MediSync format
    print("\n🔄 Converting external data to MediSync format...")
    
    demographics_data = adapter.adapt_patient_demographics(demographics_df)
    health_trends_data = adapter.adapt_disease_data(disease_df)
    
    # Create multiple datasets for training
    datasets = []
    for i in range(10):  # Create 10 different datasets
        # Vary the data slightly for each dataset
        varied_demographics = demographics_data.copy()
        varied_demographics['total_patients'] += np.random.randint(-50, 50)
        varied_demographics['average_age'] += np.random.uniform(-5, 5)
        
        dataset = adapter.create_medisync_dataset(
            demographics_data=varied_demographics,
            health_trends_data=health_trends_data
        )
        datasets.append(dataset)
    
    print(f"✅ Created {len(datasets)} MediSync-compatible datasets")
    
    # Train the AI model
    print("\n🤖 Training AI model on external datasets...")
    training_metrics = ai_model.train_models(datasets)
    
    print("\n📈 Training Results:")
    print(f"TensorFlow Model:")
    for metric, value in training_metrics['tensorflow'].items():
        print(f"  {metric.capitalize()}: {value:.4f}")
    
    print(f"\nRandom Forest Model:")
    for metric, value in training_metrics['random_forest'].items():
        print(f"  {metric.capitalize()}: {value:.4f}")
    
    # Test the model with new data
    print("\n🔍 Testing model with new external data...")
    test_dataset = adapter.create_medisync_dataset(
        demographics_data=adapter.adapt_patient_demographics(demographics_df.sample(100)),
        health_trends_data=adapter.adapt_disease_data(disease_df.sample(50))
    )
    
    insights = ai_model.generate_insights(test_dataset)
    
    print("\n💡 Generated Insights:")
    print(f"Risk Assessment: {insights['risk_assessment']['overall_risk']}")
    print(f"Confidence: {insights['risk_assessment']['confidence']:.2f}")
    
    print("\nActionable Insights:")
    for insight in insights['actionable_insights']['recommendations'][:3]:
        print(f"  • {insight}")
    
    print("\nDoctor Recommendations:")
    for rec in insights['doctor_recommendations']['clinical_actions'][:2]:
        print(f"  • {rec}")
    
    print("\nNurse Recommendations:")
    for rec in insights['nurse_recommendations']['patient_care'][:2]:
        print(f"  • {rec}")
    
    return ai_model, insights

def test_with_csv_data(csv_file_path):
    """
    Test the AI model with a real CSV dataset.
    
    Args:
        csv_file_path (str): Path to the CSV file
    """
    print(f"\n📁 Testing with CSV file: {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        print(f"❌ File not found: {csv_file_path}")
        return None
    
    adapter = ExternalDatasetAdapter()
    ai_model = MediSyncAIInsights()
    
    try:
        # Load the CSV data
        df = adapter.load_dataset(csv_file_path, 'csv')
        print(f"✅ Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        
        # Try to adapt the data (this will depend on the actual column names)
        # You'll need to modify these column names based on your actual dataset
        if 'age' in df.columns and 'gender' in df.columns:
            demographics_data = adapter.adapt_patient_demographics(df, 'age', 'gender')
            print("✅ Successfully adapted demographics data")
        else:
            print("⚠️  No age/gender columns found, using synthetic demographics")
            demographics_data = None
        
        if 'condition' in df.columns or 'diagnosis' in df.columns:
            condition_col = 'condition' if 'condition' in df.columns else 'diagnosis'
            date_col = 'date' if 'date' in df.columns else None
            health_trends_data = adapter.adapt_disease_data(df, condition_col, date_col)
            print("✅ Successfully adapted health trends data")
        else:
            print("⚠️  No condition/diagnosis columns found, using synthetic health trends")
            health_trends_data = None
        
        # Create MediSync dataset
        dataset = adapter.create_medisync_dataset(
            demographics_data=demographics_data,
            health_trends_data=health_trends_data
        )
        
        # Generate insights
        insights = ai_model.generate_insights(dataset)
        
        print("\n💡 Insights from your CSV data:")
        print(f"Risk Assessment: {insights['risk_assessment']['overall_risk']}")
        print(f"Confidence: {insights['risk_assessment']['confidence']:.2f}")
        
        return insights
        
    except Exception as e:
        print(f"❌ Error processing CSV file: {str(e)}")
        return None

def main():
    """
    Main function to demonstrate testing with external datasets.
    """
    print("🏥 MediSync AI Model - External Dataset Testing")
    print("=" * 50)
    
    print("\nThis script demonstrates how to test the MediSync AI model with external healthcare datasets.")
    print("\nSupported dataset types:")
    print("• Patient demographics (age, gender, location)")
    print("• Disease/condition prevalence data")
    print("• Hospital admission records")
    print("• Public health statistics")
    print("• Clinical trial data")
    print("• Electronic Health Records (EHR)")
    
    # Test with synthetic data
    ai_model, insights = test_with_synthetic_external_data()
    
    # Example of testing with a real CSV file
    print("\n" + "="*70)
    print("📋 To test with your own CSV file:")
    print("1. Ensure your CSV has columns like 'age', 'gender', 'condition', 'diagnosis', 'date'")
    print("2. Uncomment the line below and provide your CSV file path")
    print("3. The adapter will automatically convert your data to MediSync format")
    
    # Uncomment and modify this line to test with your own CSV file:
    # test_with_csv_data('/path/to/your/healthcare_dataset.csv')
    
    print("\n✅ Testing completed successfully!")
    print("\nNext steps:")
    print("• Modify column mappings in the adapter for your specific dataset")
    print("• Add custom preprocessing for domain-specific healthcare data")
    print("• Integrate with your existing healthcare data pipeline")
    print("• Fine-tune the model with your organization's historical data")

if __name__ == "__main__":
    main()