import pandas as pd
import numpy as np
import json
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import chi2_contingency
from django.db.models import QuerySet

def get_data_from_queryset(queryset: QuerySet):
    """
    Loads data from a Django QuerySet into a pandas DataFrame.
    """
    if not queryset.exists():
        return pd.DataFrame()
    
    # Efficiently load data into a DataFrame
    return pd.DataFrame.from_records(queryset.values())

def perform_patient_health_trends(df):
    """Analyzes and returns the top 5 medical conditions per week."""
    # Ensure 'Date of Admission' is in datetime format
    df['date_of_admission'] = pd.to_datetime(df['date_of_admission'], errors='coerce')
    df.dropna(subset=['date_of_admission'], inplace=True)
    
    if 'medical_condition' not in df.columns or 'date_of_admission' not in df.columns:
        return {"error": "Required columns not found for patient health trends."}
        
    weekly_illness_counts = df.groupby([pd.Grouper(key='date_of_admission', freq='W'), 'medical_condition']).size().reset_index(name='count')
    top_illnesses = weekly_illness_counts.sort_values(by='count', ascending=False).groupby('date_of_admission').head(5)
    
    # Prepare data for JSON serialization
    top_illnesses['date_of_admission'] = top_illnesses['date_of_admission'].astype(str)
    return {"top_illnesses_by_week": top_illnesses.to_dict('records')}

def analyze_patient_demographics(df):
    """Analyzes and returns patient age and gender distribution."""
    demographics_data = df[['age', 'gender']].copy()
    age_bins = [20, 40, 60, 80, 100]
    age_labels = ['20-39', '40-59', '60-79', '80+']
    demographics_data['age_group'] = pd.cut(demographics_data['age'], bins=age_bins, labels=age_labels, right=False)
    
    age_distribution = demographics_data['age_group'].value_counts().sort_index()
    gender_counts = demographics_data['gender'].value_counts()
    gender_proportions = (gender_counts / gender_counts.sum() * 100).round(2)
    
    return {
        "age_distribution": age_distribution.to_dict(),
        "gender_proportions": gender_proportions.to_dict()
    }

def analyze_illness_prediction_chi_square(df):
    """Performs Chi-Square test for illness prediction based on age and gender."""
    df['date_of_admission'] = pd.to_datetime(df['date_of_admission'], errors='coerce')
    df.dropna(subset=['date_of_admission'], inplace=True)
    
    age_bins = [20, 40, 60, 90]
    age_labels = ['20-39', '40-59', '60+']
    df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=False)
    
    contingency_table = pd.crosstab([df['age_group'], df['gender']], df['medical_condition'])
    
    chi2, p_value, _, _ = chi2_contingency(contingency_table)
    
    association_result = "Statistically significant association." if p_value < 0.05 else "No statistically significant association."
    
    contingency_data = contingency_table.reset_index().to_dict('records')
    
    return {
        "chi_square_statistic": round(chi2, 2),
        "p_value": round(p_value, 4),
        "association_result": association_result,
        "contingency_table": contingency_data
    }

def analyze_common_medications(df):
    """Analyzes and returns the frequency of prescribed medications."""
    medication_frequency = df['medication'].value_counts()
    medication_frequency_sorted = medication_frequency.sort_values(ascending=False)
    cumulative_frequency = medication_frequency_sorted.cumsum()
    cumulative_percentage = (cumulative_frequency / cumulative_frequency.iloc[-1] * 100).round(2)
    
    pareto_data = pd.DataFrame({
        'frequency': medication_frequency_sorted,
        'cumulative_percentage': cumulative_percentage
    })
    
    return {"medication_pareto_data": pareto_data.reset_index().rename(columns={'index': 'medication'}).to_dict('records')}

def predict_patient_volume(df):
    """Predicts future patient volume using SARIMA model."""
    df['date_of_admission'] = pd.to_datetime(df['date_of_admission'], errors='coerce')
    df.dropna(subset=['date_of_admission'], inplace=True)

    df['month_year'] = df['date_of_admission'].dt.to_period('M')
    monthly_volumes = df.groupby('month_year').size()
    monthly_volumes.index = monthly_volumes.index.to_timestamp()

    # Split the data
    train_size = int(len(monthly_volumes) * 0.7)
    train_data = monthly_volumes[:train_size]
    test_data = monthly_volumes[train_size:]
    
    try:
        model = SARIMAX(train_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        results = model.fit(disp=False)
        forecast = results.get_forecast(steps=len(test_data))
        forecasted_values = forecast.predicted_mean

        mae = mean_absolute_error(test_data, forecasted_values)
        mse = mean_squared_error(test_data, forecasted_values)
        rmse = np.sqrt(mse)
        
        comparison_df = pd.DataFrame({'Actual': test_data, 'Forecasted': forecasted_values})
        comparison_df['Actual'] = comparison_df['Actual'].round(2)
        comparison_df['Forecasted'] = comparison_df['Forecasted'].round(2)
        
        return {
            "evaluation_metrics": {
                "mae": round(mae, 2),
                "mse": round(mse, 2),
                "rmse": round(rmse, 2)
            },
            "comparison_data": comparison_df.reset_index().rename(columns={'index': 'date'}).to_dict('records')
        }
    except Exception as e:
        return {"error": f"Patient volume prediction failed: {str(e)}"}

def predict_illness_surge(df):
    """Predicts illness surge for each medical condition using SARIMA."""
    df['date_of_admission'] = pd.to_datetime(df['date_of_admission'], errors='coerce')
    df.dropna(subset=['date_of_admission'], inplace=True)
    
    df['month_year'] = df['date_of_admission'].dt.to_period('M')
    df_monthly = df.groupby(['month_year', 'medical_condition']).size().unstack(fill_value=0)
    df_monthly.index = df_monthly.index.to_timestamp()
    
    forecast_df = pd.DataFrame()
    evaluation_metrics = {}
    forecast_steps = 6

    for medical_condition in df_monthly.columns:
        ts = df_monthly[medical_condition]
        train_size = int(len(ts) * 0.8)
        train = ts[:train_size]
        test = ts[train_size:]
        
        try:
            model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12),
                            enforce_stationarity=False, enforce_invertibility=False)
            results = model.fit(disp=False)
            forecast = results.get_forecast(steps=forecast_steps)
            forecast_values = forecast.predicted_mean
            
            forecast_df[medical_condition] = forecast_values
            
            if len(test) > 0:
                common_index = test.index.intersection(forecast_values.index)
                if len(common_index) > 0:
                    actual = test[common_index]
                    predicted = forecast_values[common_index]
                    
                    mae = mean_absolute_error(actual, predicted)
                    mse = mean_squared_error(actual, predicted)
                    rmse = np.sqrt(mse)
                    evaluation_metrics[medical_condition] = {
                        'mae': round(mae, 2), 'mse': round(mse, 2), 'rmse': round(rmse, 2)
                    }
        except Exception:
            evaluation_metrics[medical_condition] = {'error': 'Failed to fit model'}

    forecast_json = forecast_df.reset_index().rename(columns={'index': 'date'}).to_dict('records')
    
    return {
        "forecasted_monthly_cases": forecast_json,
        "evaluation_metrics": evaluation_metrics
    }

def predict_weekly_illness_forecast(df):
    """Predicts specific illnesses that will occur in the following weeks."""
    df['date_of_admission'] = pd.to_datetime(df['date_of_admission'], errors='coerce')
    df.dropna(subset=['date_of_admission'], inplace=True)
    
    # Group by week and medical condition
    df['week_year'] = df['date_of_admission'].dt.to_period('W')
    df_weekly = df.groupby(['week_year', 'medical_condition']).size().unstack(fill_value=0)
    df_weekly.index = df_weekly.index.to_timestamp()
    
    forecast_df = pd.DataFrame()
    evaluation_metrics = {}
    forecast_steps = 8  # Predict next 8 weeks
    
    illness_predictions = []
    
    for medical_condition in df_weekly.columns:
        ts = df_weekly[medical_condition]
        if len(ts) < 4:  # Need at least 4 weeks of data
            continue
            
        train_size = int(len(ts) * 0.8)
        train = ts[:train_size]
        test = ts[train_size:]
        
        try:
            # Use simpler model for weekly data
            model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 4),
                            enforce_stationarity=False, enforce_invertibility=False)
            results = model.fit(disp=False)
            forecast = results.get_forecast(steps=forecast_steps)
            forecast_values = forecast.predicted_mean
            
            forecast_df[medical_condition] = forecast_values
            
            # Calculate confidence intervals
            confidence_intervals = forecast.conf_int()
            
            # Create weekly predictions with confidence
            for i, (date, predicted_cases) in enumerate(forecast_values.items()):
                if predicted_cases > 0:  # Only include predictions with expected cases
                    lower_bound = confidence_intervals.iloc[i, 0]
                    upper_bound = confidence_intervals.iloc[i, 1]
                    
                    illness_predictions.append({
                        'illness': medical_condition,
                        'week': date.strftime('%Y-%m-%d'),
                        'predicted_cases': round(predicted_cases, 1),
                        'confidence_lower': round(lower_bound, 1),
                        'confidence_upper': round(upper_bound, 1),
                        'risk_level': 'High' if predicted_cases > ts.mean() * 1.5 else 'Medium' if predicted_cases > ts.mean() else 'Low'
                    })
            
            if len(test) > 0:
                common_index = test.index.intersection(forecast_values.index)
                if len(common_index) > 0:
                    actual = test[common_index]
                    predicted = forecast_values[common_index]
                    
                    mae = mean_absolute_error(actual, predicted)
                    mse = mean_squared_error(actual, predicted)
                    rmse = np.sqrt(mse)
                    evaluation_metrics[medical_condition] = {
                        'mae': round(mae, 2), 'mse': round(mse, 2), 'rmse': round(rmse, 2)
                    }
        except Exception as e:
            evaluation_metrics[medical_condition] = {'error': f'Failed to fit model: {str(e)}'}

    # Sort predictions by predicted cases (highest risk first)
    illness_predictions.sort(key=lambda x: x['predicted_cases'], reverse=True)
    
    return {
        "weekly_illness_forecast": illness_predictions,
        "evaluation_metrics": evaluation_metrics,
        "summary": {
            "total_predictions": len(illness_predictions),
            "high_risk_illnesses": len([p for p in illness_predictions if p['risk_level'] == 'High']),
            "medium_risk_illnesses": len([p for p in illness_predictions if p['risk_level'] == 'Medium']),
            "low_risk_illnesses": len([p for p in illness_predictions if p['risk_level'] == 'Low'])
        }
    }

def predict_monthly_illness_forecast(df):
    """Predicts specific illnesses that will occur in the following months."""
    df['date_of_admission'] = pd.to_datetime(df['date_of_admission'], errors='coerce')
    df.dropna(subset=['date_of_admission'], inplace=True)
    
    # Group by month and medical condition
    df['month_year'] = df['date_of_admission'].dt.to_period('M')
    df_monthly = df.groupby(['month_year', 'medical_condition']).size().unstack(fill_value=0)
    df_monthly.index = df_monthly.index.to_timestamp()
    
    forecast_df = pd.DataFrame()
    evaluation_metrics = {}
    forecast_steps = 6  # Predict next 6 months
    
    illness_predictions = []
    
    for medical_condition in df_monthly.columns:
        ts = df_monthly[medical_condition]
        if len(ts) < 3:  # Need at least 3 months of data
            continue
            
        train_size = int(len(ts) * 0.8)
        train = ts[:train_size]
        test = ts[train_size:]
        
        try:
            model = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12),
                            enforce_stationarity=False, enforce_invertibility=False)
            results = model.fit(disp=False)
            forecast = results.get_forecast(steps=forecast_steps)
            forecast_values = forecast.predicted_mean
            
            forecast_df[medical_condition] = forecast_values
            
            # Calculate confidence intervals
            confidence_intervals = forecast.conf_int()
            
            # Create monthly predictions with confidence
            for i, (date, predicted_cases) in enumerate(forecast_values.items()):
                if predicted_cases > 0:  # Only include predictions with expected cases
                    lower_bound = confidence_intervals.iloc[i, 0]
                    upper_bound = confidence_intervals.iloc[i, 1]
                    
                    # Determine risk level based on historical average
                    historical_avg = ts.mean()
                    if predicted_cases > historical_avg * 2:
                        risk_level = 'Critical'
                    elif predicted_cases > historical_avg * 1.5:
                        risk_level = 'High'
                    elif predicted_cases > historical_avg:
                        risk_level = 'Medium'
                    else:
                        risk_level = 'Low'
                    
                    illness_predictions.append({
                        'illness': medical_condition,
                        'month': date.strftime('%Y-%m'),
                        'predicted_cases': round(predicted_cases, 1),
                        'confidence_lower': round(lower_bound, 1),
                        'confidence_upper': round(upper_bound, 1),
                        'risk_level': risk_level,
                        'trend': 'Increasing' if predicted_cases > historical_avg else 'Stable' if predicted_cases > historical_avg * 0.8 else 'Decreasing'
                    })
            
            if len(test) > 0:
                common_index = test.index.intersection(forecast_values.index)
                if len(common_index) > 0:
                    actual = test[common_index]
                    predicted = forecast_values[common_index]
                    
                    mae = mean_absolute_error(actual, predicted)
                    mse = mean_squared_error(actual, predicted)
                    rmse = np.sqrt(mse)
                    evaluation_metrics[medical_condition] = {
                        'mae': round(mae, 2), 'mse': round(mse, 2), 'rmse': round(rmse, 2)
                    }
        except Exception as e:
            evaluation_metrics[medical_condition] = {'error': f'Failed to fit model: {str(e)}'}

    # Sort predictions by predicted cases (highest risk first)
    illness_predictions.sort(key=lambda x: x['predicted_cases'], reverse=True)
    
    return {
        "monthly_illness_forecast": illness_predictions,
        "evaluation_metrics": evaluation_metrics,
        "summary": {
            "total_predictions": len(illness_predictions),
            "critical_risk_illnesses": len([p for p in illness_predictions if p['risk_level'] == 'Critical']),
            "high_risk_illnesses": len([p for p in illness_predictions if p['risk_level'] == 'High']),
            "medium_risk_illnesses": len([p for p in illness_predictions if p['risk_level'] == 'Medium']),
            "low_risk_illnesses": len([p for p in illness_predictions if p['risk_level'] == 'Low'])
        }
    }
    
def run_full_analysis():
    """Master function to run the full predictive analysis pipeline."""
    # Assuming this function is called from a Django view or Celery task.
    # We must access the model from a Django context.
    from .models import PatientRecord 
    queryset = PatientRecord.objects.all()
    df = get_data_from_queryset(queryset)
    
    if df.empty:
        return {"error": "No data available for analysis."}
    
    # Clean and rename columns to be consistent with the original notebook
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Call all analytical functions
    results = {
        "patient_health_trends": perform_patient_health_trends(df),
        "patient_demographics": analyze_patient_demographics(df),
        "illness_prediction_chi_square": analyze_illness_prediction_chi_square(df),
        "common_medications": analyze_common_medications(df),
        "predictive_analytics": predict_patient_volume(df),
        "illness_surge_prediction": predict_illness_surge(df),
        "weekly_illness_forecast": predict_weekly_illness_forecast(df),
        "monthly_illness_forecast": predict_monthly_illness_forecast(df)
    }
    return results

if __name__ == "__main__":
    try:
        # This block is for direct execution (e.g., via subprocess)
        # It's a placeholder for local testing and requires a way to mock a Django environment
        # to access the models. For a real setup, this would be run by the Django view/Celery task.
        print(json.dumps({"info": "This script is designed to be run within a Django context."}, indent=4))
        
    except Exception as e:
        print(json.dumps({"error": f"An error occurred: {str(e)}"}))
