#!/usr/bin/env python3
"""
Data Ingestion Module Execution
Final Year Project: Enhancing Threat Detection in Cloud Environments Through Temporal Anomaly Modeling
"""

print("📥 DATA INGESTION MODULE")
print("=" * 30)
print("🔍 Loading cloud environment data...")

try:
    import pandas as pd
    import numpy as np
    
    # Load the current anomaly data
    data = pd.read_csv('/home/nikhi/Desktop/final year project/final/current_anomaly_data.csv')
    
    print(f"✅ Loaded real anomaly data: {data.shape[0]} records")
    print(f"📊 Columns: {list(data.columns)}")
    print(f"📅 Time range: {data['timestamp'].iloc[0]} → {data['timestamp'].iloc[-1]}")
    
    # Check for anomalies
    if 'is_anomaly' in data.columns:
        anomaly_count = data['is_anomaly'].sum()
        anomaly_rate = (anomaly_count / len(data)) * 100
        print(f"🚨 Anomalies detected: {anomaly_count}/{len(data)} ({anomaly_rate:.1f}%)")
    
    print("\n📋 Sample data:")
    print(data.head(3).to_string(index=False))
    
    print("\n✅ Data ingestion complete!")
    print(f"📊 Memory usage: {data.memory_usage(deep=True).sum():,} bytes")
    print(f"🎯 Data ready for preprocessing and anomaly detection!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except FileNotFoundError as e:
    print(f"❌ File not found: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("🎯 DATA INGESTION MODULE EXECUTION COMPLETE")
print("=" * 50)
