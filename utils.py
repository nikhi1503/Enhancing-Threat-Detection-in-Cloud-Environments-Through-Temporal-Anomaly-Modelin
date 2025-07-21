"""
Utility functions for threat detection system
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_config():
    """Load configuration settings"""
    return {
        'anomaly_detection': {
            'contamination': 0.15,
            'random_state': 42,
            'features': ['cpu_usage', 'network_traffic', 'login_attempts']
        },
        'simulation': {
            'default_days': 7,
            'attack_scenarios': ['ddos', 'brute_force', 'resource_exhaustion']
        },
        'reporting': {
            'output_dir': 'reports',
            'include_plots': True,
            'generate_html': True
        }
    }

def validate_data(data):
    """Validate input data format and quality"""
    required_columns = ['timestamp', 'cpu_usage', 'network_traffic', 'login_attempts']
    
    # Check required columns
    missing_cols = [col for col in required_columns if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Check data types
    if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
        try:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
        except:
            raise ValueError("Cannot convert timestamp column to datetime")
    
    # Check for reasonable ranges
    for col in ['cpu_usage', 'network_traffic']:
        if (data[col] < 0).any() or (data[col] > 1).any():
            print(f"Warning: {col} contains values outside [0,1] range")
    
    if (data['login_attempts'] < 0).any():
        print("Warning: login_attempts contains negative values")
    
    return data

def create_sample_data(days=7, freq='H'):
    """Create sample data for testing"""
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()
    timestamps = pd.date_range(start=start_date, end=end_date, freq=freq)
    
    n_points = len(timestamps)
    np.random.seed(42)
    
    data = pd.DataFrame({
        'timestamp': timestamps,
        'cpu_usage': np.random.beta(2, 5, n_points),  # Skewed towards lower values
        'network_traffic': np.random.beta(2, 3, n_points),
        'login_attempts': np.random.poisson(3, n_points)
    })
    
    return data

def export_results(data, anomalies, filename='detection_results.csv'):
    """Export detection results to CSV"""
    data.to_csv(filename, index=False)
    print(f"Results exported to {filename}")

def calculate_detection_metrics(true_labels, predicted_labels):
    """Calculate performance metrics for anomaly detection"""
    from sklearn.metrics import classification_report, confusion_matrix
    
    # Convert anomaly labels (-1, 1) to binary (1, 0)
    predicted_binary = (predicted_labels == -1).astype(int)
    
    metrics = {
        'classification_report': classification_report(true_labels, predicted_binary),
        'confusion_matrix': confusion_matrix(true_labels, predicted_binary)
    }
    
    return metrics
