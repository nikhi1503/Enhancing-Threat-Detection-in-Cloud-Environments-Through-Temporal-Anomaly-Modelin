import pandas as pd
import numpy as np
import os

def load_data():
    """
    Load cloud environment data for threat detection system
    Part of: Enhancing Threat Detection in Cloud Environments Through Temporal Anomaly Modeling
    """
    print("📥 DATA INGESTION MODULE")
    print("=" * 30)
    print("🔍 Loading cloud environment data...")
    
    # Try to load real anomaly data first
    try:
        data_path = '../current_anomaly_data.csv'
        if os.path.exists(data_path):
            data = pd.read_csv(data_path)
            print(f"✅ Loaded real anomaly data: {data.shape[0]} records")
            print(f"📊 Columns: {list(data.columns)}")
            print(f"📅 Time range: {data['timestamp'].min()} → {data['timestamp'].max()}")
            
            # Check for anomalies
            if 'is_anomaly' in data.columns:
                anomaly_count = data['is_anomaly'].sum()
                anomaly_rate = (anomaly_count / len(data)) * 100
                print(f"🚨 Anomalies detected: {anomaly_count}/{len(data)} ({anomaly_rate:.1f}%)")
            
        else:
            # Try current directory
            data = pd.read_csv('current_anomaly_data.csv')
            print(f"✅ Loaded current anomaly data: {data.shape[0]} records")
            
    except FileNotFoundError:
        print("⚠️  Real data not found, generating dummy data...")
        # Generate dummy data if file not found
        data = pd.DataFrame({
            'timestamp': pd.date_range(start='2025-01-01', periods=100, freq='H'),
            'cpu_usage': np.random.rand(100),
            'network_traffic': np.random.rand(100),
            'login_attempts': np.random.randint(0, 10, 100)
        })
        print(f"📊 Generated dummy data: {data.shape[0]} records")
    
    print(f"\n📋 Sample data:")
    print(data.head(3).to_string(index=False))
    print("\n✅ Data ingestion complete!")
    return data

if __name__ == "__main__":
    # Test the data ingestion
    print("🎯 TESTING DATA INGESTION MODULE")
    print("Final Year Project: Threat Detection in Cloud Environments")
    print("=" * 60)
    
    # Load the data
    dataset = load_data()
    
    print(f"\n📊 INGESTION SUMMARY:")
    print(f"   Records loaded: {len(dataset):,}")
    print(f"   Features: {len(dataset.columns)}")
    print(f"   Memory usage: {dataset.memory_usage(deep=True).sum():,} bytes")
    
    # Save summary for other modules
    summary = {
        'records': len(dataset),
        'columns': list(dataset.columns),
        'timestamp': pd.Timestamp.now().isoformat()
    }
    
    print(f"\n🎯 Data ready for preprocessing and anomaly detection!")
    print("=" * 60)
