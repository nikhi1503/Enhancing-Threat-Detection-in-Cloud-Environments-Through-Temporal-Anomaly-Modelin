import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def preprocess_data(data):
    """
    Enhanced preprocessing for temporal anomaly detection
    Part of: Enhancing Threat Detection in Cloud Environments Through Temporal Anomaly Modeling
    """
    print("🔧 PREPROCESSING MODULE")
    print("=" * 30)
    print(f"🔍 Processing {len(data)} records...")
    
    # Create a copy to avoid modifying original data
    processed_data = data.copy()
    
    # Handle timestamp conversion
    if 'timestamp' in processed_data.columns:
        processed_data['timestamp'] = pd.to_datetime(processed_data['timestamp'])
        print("✅ Timestamp converted to datetime")
    
    # Fill missing values using forward fill
    initial_nulls = processed_data.isnull().sum().sum()
    processed_data = processed_data.fillna(method='ffill')
    final_nulls = processed_data.isnull().sum().sum()
    print(f"🔧 Missing values handled: {initial_nulls} → {final_nulls}")
    
    # Normalize numeric features for temporal anomaly detection
    numeric_cols = ['cpu_usage', 'network_traffic', 'failed_login_attempts', 'memory_usage', 'disk_io']
    available_cols = [col for col in numeric_cols if col in processed_data.columns]
    
    print(f"📊 Normalizing features: {available_cols}")
    
    for col in available_cols:
        if processed_data[col].max() != processed_data[col].min():  # Avoid division by zero
            # Min-Max normalization for better anomaly detection
            processed_data[col] = (processed_data[col] - processed_data[col].min()) / (processed_data[col].max() - processed_data[col].min())
            print(f"   ✅ {col}: normalized to [0, 1] range")
        else:
            print(f"   ⚠️  {col}: constant values, skipping normalization")
    
    # Create temporal features for enhanced anomaly detection
    if 'timestamp' in processed_data.columns:
        processed_data['hour'] = processed_data['timestamp'].dt.hour
        processed_data['day_of_week'] = processed_data['timestamp'].dt.dayofweek
        print("✅ Temporal features extracted")
    
    # Calculate moving averages for trend analysis
    if len(processed_data) > 3:
        for col in ['cpu_usage', 'network_traffic']:
            if col in processed_data.columns:
                processed_data[f'{col}_ma3'] = processed_data[col].rolling(window=3, min_periods=1).mean()
                processed_data[f'{col}_trend'] = processed_data[col].diff()
        print("✅ Moving averages and trends calculated")
    
    print(f"✅ Preprocessing complete: {len(processed_data)} records ready")
    print(f"📊 Features: {len(processed_data.columns)} columns")
    
    return processed_data

if __name__ == "__main__":
    print("🎯 TESTING PREPROCESSING MODULE")
    print("Final Year Project: Threat Detection in Cloud Environments")
    print("=" * 60)
    
    # Test with sample data if available
    try:
        import os
        if os.path.exists('../current_anomaly_data.csv'):
            test_data = pd.read_csv('../current_anomaly_data.csv')
            print(f"📥 Loaded test data: {len(test_data)} records")
            
            # Run preprocessing
            processed = preprocess_data(test_data)
            
            print(f"\n📊 PREPROCESSING RESULTS:")
            print(f"   Input records: {len(test_data)}")
            print(f"   Output records: {len(processed)}")
            print(f"   Input features: {len(test_data.columns)}")
            print(f"   Output features: {len(processed.columns)}")
            print(f"   New columns: {set(processed.columns) - set(test_data.columns)}")
            
        else:
            print("📊 Creating sample data for testing...")
            sample_data = pd.DataFrame({
                'timestamp': pd.date_range('2025-01-01', periods=10, freq='H'),
                'cpu_usage': np.random.rand(10),
                'network_traffic': np.random.rand(10) * 2,
                'failed_login_attempts': np.random.randint(0, 20, 10)
            })
            
            processed = preprocess_data(sample_data)
            print(f"✅ Sample preprocessing completed")
            
    except Exception as e:
        print(f"❌ Error in preprocessing test: {e}")
    
    print("\n🎯 Preprocessing module ready for integration!")
    print("=" * 60)
