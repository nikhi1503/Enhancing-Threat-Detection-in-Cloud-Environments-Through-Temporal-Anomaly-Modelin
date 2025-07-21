#!/usr/bin/env python3
"""
Enhanced Threat Detection Pipeline
Comprehensive system for detecting threats in cloud environments using temporal anomaly modeling
"""

import sys
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.cloud_simulator import CloudEnvironmentSimulator
from anomaly_detection.temporal_models import TemporalAnomalyDetector
from reporting.advanced_reporter import ThreatDetectionReporter

def main():
    """Main pipeline for threat detection"""
    print("🚀 Starting Enhanced Threat Detection Pipeline...")
    
    # Step 1: Generate simulated cloud environment data with attacks
    print("📊 Generating cloud environment data with attack scenarios...")
    simulator = CloudEnvironmentSimulator()
    data = simulator.generate_attack_scenario(days=7)
    print(f"   Generated {len(data)} data points over 7 days")
    
    # Step 2: Initialize and train temporal anomaly detector
    print("🧠 Training temporal anomaly detection model...")
    detector = TemporalAnomalyDetector(contamination=0.15, random_state=42)
    
    # Step 3: Detect anomalies
    print("🔍 Detecting anomalies in cloud environment data...")
    results = detector.fit_predict(data)
    
    # Extract anomalies
    anomalies = results[results['anomaly'] == -1]
    print(f"   Detected {len(anomalies)} anomalies ({len(anomalies)/len(results)*100:.2f}% of data)")
    
    # Step 4: Generate comprehensive report
    print("📈 Generating comprehensive threat detection report...")
    reporter = ThreatDetectionReporter()
    summary = reporter.generate_comprehensive_report(results, anomalies)
    
    # Step 5: Display summary
    print("\n" + "="*60)
    print("THREAT DETECTION SUMMARY")
    print("="*60)
    print(f"Total Data Points: {summary['total_data_points']}")
    print(f"Anomalies Detected: {summary['total_anomalies_detected']}")
    print(f"Anomaly Rate: {summary['anomaly_rate_percentage']}%")
    print(f"Analysis Period: {summary['analysis_period']['start']} to {summary['analysis_period']['end']}")
    
    if summary.get('anomaly_statistics'):
        print("\nANOMALY CHARACTERISTICS:")
        print(f"  Average CPU Usage: {summary['anomaly_statistics']['avg_cpu_usage']}")
        print(f"  Average Network Traffic: {summary['anomaly_statistics']['avg_network_traffic']}")
        print(f"  Average Login Attempts: {summary['anomaly_statistics']['avg_login_attempts']}")
        print(f"  Peak CPU Usage: {summary['anomaly_statistics']['max_cpu_usage']}")
        print(f"  Peak Network Traffic: {summary['anomaly_statistics']['max_network_traffic']}")
        print(f"  Peak Login Attempts: {summary['anomaly_statistics']['max_login_attempts']}")
    
    print("\n📁 Reports generated in 'reports' directory:")
    print("   - threat_detection_report.html (comprehensive summary)")
    print("   - timeline_analysis.png (metrics timeline)")
    print("   - anomaly_distribution.png (anomaly patterns)")
    print("   - feature_correlation.png (feature relationships)")
    print("   - anomaly_scores.png (score distributions)")
    
    print("\n✅ Threat detection pipeline completed successfully!")
    
    return results, anomalies, summary

if __name__ == "__main__":
    try:
        results, anomalies, summary = main()
    except Exception as e:
        print(f"❌ Error in threat detection pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
