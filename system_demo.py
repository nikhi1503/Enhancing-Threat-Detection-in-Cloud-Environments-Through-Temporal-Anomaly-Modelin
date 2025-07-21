#!/usr/bin/env python3
"""
Complete System Demonstration
Final Year Project: Enhancing Threat Detection in Cloud Environments Through Temporal Anomaly Modeling
"""

import json
import pandas as pd
import os
from datetime import datetime

def display_banner():
    print("=" * 80)
    print("🚀 THREAT DETECTION SYSTEM - COMPLETE DEMONSTRATION")
    print("   Final Year Project: Cloud Environment Anomaly Detection")
    print("=" * 80)

def show_anomaly_data():
    print("\n🔍 ANOMALY DETECTION STATUS:")
    print("-" * 40)
    
    try:
        # Load current anomaly data
        if os.path.exists('current_anomaly_data.csv'):
            data = pd.read_csv('current_anomaly_data.csv')
            anomalies = data[data['is_anomaly'] == True]
            
            print(f"📊 Total Data Points: {len(data)}")
            print(f"🚨 Anomalies Detected: {len(anomalies)}")
            print(f"📈 Anomaly Rate: {len(anomalies)/len(data)*100:.1f}%")
            
            if len(anomalies) > 0:
                print(f"⚠️  Latest Anomaly:")
                latest = anomalies.iloc[-1]
                print(f"   Time: {latest['timestamp']}")
                print(f"   CPU: {latest['cpu_usage']:.1f}%")
                print(f"   Network: {latest['network_traffic']:.1f}x normal")
                print(f"   Logins: {latest['failed_login_attempts']} attempts")
        else:
            print("❌ No anomaly data found")
            
    except Exception as e:
        print(f"❌ Error loading anomaly data: {e}")

def show_gcp_incidents():
    print("\n🚨 GCP INCIDENT STATUS:")
    print("-" * 40)
    
    try:
        if os.path.exists('gcp_incident_status.json'):
            with open('gcp_incident_status.json', 'r') as f:
                gcp_data = json.load(f)
            
            incidents = gcp_data.get('incidents', [])
            alerts = gcp_data.get('alerts', [])
            summary = gcp_data.get('summary', {})
            
            print(f"🔥 Active Incidents: {len(incidents)}")
            print(f"⚠️  Alert Policies: {len(alerts)}")
            print(f"📱 Notification Channels: {summary.get('notification_channels', 0)}")
            print(f"🖥️  System Status: {summary.get('status', 'UNKNOWN')}")
            
            if incidents:
                print(f"\n📋 Current Incidents:")
                for i, incident in enumerate(incidents[:3], 1):
                    print(f"   {i}. {incident['name']}")
                    print(f"      Status: {incident['status']} | Severity: {incident['severity']}")
                    
        else:
            print("❌ No GCP incident data found")
            
    except Exception as e:
        print(f"❌ Error loading GCP data: {e}")

def show_dashboard_info():
    print("\n📊 DASHBOARD STATUS:")
    print("-" * 40)
    print("🌐 URL: http://localhost:8051")
    print("🔧 Features:")
    print("   ✅ Real-time Anomaly Detection")
    print("   ✅ GCP Cloud Integration")
    print("   ✅ Interactive Visualization")
    print("   ✅ Email/SMS Notifications")
    print("   ✅ Temporal Pattern Analysis")
    print("   ✅ Threat Correlation Matrix")

def show_system_capabilities():
    print("\n⚡ SYSTEM CAPABILITIES:")
    print("-" * 40)
    print("🔍 Detection Methods:")
    print("   • Isolation Forest Algorithm")
    print("   • Statistical Anomaly Detection")
    print("   • Temporal Pattern Analysis")
    print("   • Multi-metric Correlation")
    
    print("\n☁️  Cloud Integration:")
    print("   • Google Cloud Platform (GCP)")
    print("   • Real-time Alert Policies")
    print("   • Incident Monitoring")
    print("   • Resource Utilization Tracking")
    
    print("\n📧 Notification Systems:")
    print("   • Email Alerts")
    print("   • SMS Notifications")
    print("   • Dashboard Alerts")
    print("   • GCP Console Integration")

def main():
    display_banner()
    show_anomaly_data()
    show_gcp_incidents()
    show_dashboard_info()
    show_system_capabilities()
    
    print("\n" + "=" * 80)
    print("🎯 SYSTEM READY FOR DEMONSTRATION")
    print("   Dashboard: http://localhost:8051")
    print("   Project: Complete and Functional")
    print("=" * 80)

if __name__ == "__main__":
    main()
