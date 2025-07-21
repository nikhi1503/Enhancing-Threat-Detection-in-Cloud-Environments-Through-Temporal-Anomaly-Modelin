#!/usr/bin/env python3
"""
Simple Anomaly Generator for Dashboard Visualization
Creates data that the dashboard can immediately display
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def create_dashboard_anomaly():
    """Create anomaly data that dashboard can display"""
    print("📊 CREATING DASHBOARD ANOMALY DATA")
    print("=" * 50)
    
    # Generate current time-based data
    now = datetime.now()
    timestamps = pd.date_range(start=now - timedelta(hours=2), end=now, freq='5min')
    
    # Create normal baseline data
    n_points = len(timestamps)
    normal_cpu = np.random.normal(0.3, 0.1, n_points)
    normal_network = np.random.normal(0.2, 0.05, n_points)
    normal_logins = np.random.poisson(5, n_points)
    
    # Inject anomalies in the last 20 minutes
    anomaly_start = n_points - 4  # Last 4 data points (20 minutes)
    
    # Create high anomalies
    normal_cpu[anomaly_start:] = np.random.normal(0.95, 0.02, 4)  # 95% CPU
    normal_network[anomaly_start:] = np.random.normal(5.0, 0.1, 4)  # 5x network
    normal_logins[anomaly_start:] = np.random.poisson(100, 4)  # High login attempts
    
    # Create DataFrame
    data = pd.DataFrame({
        'timestamp': timestamps,
        'cpu_usage': np.clip(normal_cpu, 0, 1),
        'network_traffic': np.clip(normal_network, 0, 10),
        'failed_login_attempts': np.clip(normal_logins, 0, 200),
        'memory_usage': np.random.normal(0.4, 0.1, n_points),
        'disk_io': np.random.normal(0.3, 0.08, n_points)
    })
    
    # Calculate anomaly scores (simple threshold-based)
    anomaly_scores = np.zeros(n_points)
    
    # CPU anomalies
    cpu_anomalies = data['cpu_usage'] > 0.8
    anomaly_scores[cpu_anomalies] += 0.6
    
    # Network anomalies  
    network_anomalies = data['network_traffic'] > 2.0
    anomaly_scores[network_anomalies] += 0.4
    
    # Login anomalies
    login_anomalies = data['failed_login_attempts'] > 50
    anomaly_scores[login_anomalies] += 0.3
    
    # Normalize scores
    anomaly_scores = np.clip(anomaly_scores, 0, 1)
    
    data['anomaly_score'] = anomaly_scores
    data['is_anomaly'] = anomaly_scores > 0.5
    
    # Save data
    data.to_csv('current_anomaly_data.csv', index=False)
    
    # Create JSON for real-time updates
    latest_data = {
        'timestamp': now.isoformat(),
        'current_metrics': {
            'cpu_usage': float(data['cpu_usage'].iloc[-1]),
            'network_traffic': float(data['network_traffic'].iloc[-1]),
            'failed_login_attempts': int(data['failed_login_attempts'].iloc[-1]),
            'anomaly_score': float(data['anomaly_score'].iloc[-1])
        },
        'anomaly_detected': bool(data['is_anomaly'].iloc[-1]),
        'total_anomalies': int(data['is_anomaly'].sum()),
        'anomaly_rate': float(data['is_anomaly'].mean())
    }
    
    with open('current_anomaly.json', 'w') as f:
        json.dump(latest_data, f, indent=2)
    
    print(f"✅ Created {data['is_anomaly'].sum()} anomalies in {len(data)} data points")
    print(f"📈 Anomaly rate: {data['is_anomaly'].mean():.1%}")
    print(f"💾 Saved to: current_anomaly_data.csv and current_anomaly.json")
    
    # Show recent anomalies
    recent_anomalies = data[data['is_anomaly']].tail(3)
    if not recent_anomalies.empty:
        print("\n🚨 RECENT ANOMALIES:")
        for _, row in recent_anomalies.iterrows():
            print(f"   🕐 {row['timestamp'].strftime('%H:%M')}: "
                  f"CPU={row['cpu_usage']:.1%}, "
                  f"Net={row['network_traffic']:.1f}x, "
                  f"Logins={row['failed_login_attempts']}")
    
    return data

def main():
    print("🎯 DASHBOARD ANOMALY GENERATOR")
    print("=" * 40)
    print("Creating anomalies for dashboard visualization...")
    print()
    
    # Create dashboard anomalies
    anomaly_data = create_dashboard_anomaly()
    
    print()
    print("🎉 DASHBOARD ANOMALIES CREATED!")
    print("=" * 40)
    print("📊 View in dashboard: http://localhost:8051")
    print("📁 Data files created:")
    print("   • current_anomaly_data.csv (historical data)")
    print("   • current_anomaly.json (latest metrics)")
    print()
    print("🔄 Your dashboard will now show:")
    print("   • High CPU usage (95%)")
    print("   • Elevated network traffic (5x normal)")
    print("   • Suspicious login attempts (100+)")
    print("   • Real-time anomaly detection")
    print()
    print("🎓 Perfect for final year project demonstration!")

if __name__ == "__main__":
    main()
