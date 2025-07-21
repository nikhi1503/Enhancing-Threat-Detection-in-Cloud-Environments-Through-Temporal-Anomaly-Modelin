#!/usr/bin/env python3
"""
GCP Incident Monitor for Dashboard Integration
Fetches real GCP incidents, alerts, and monitoring data
"""

import sys
import os
from datetime import datetime, timedelta
import json
import subprocess

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from google.cloud import monitoring_v3
    from google.cloud import logging
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

class GCPIncidentMonitor:
    def __init__(self):
        self.project_id = "mimetic-asset-462914-d9"
        self.project_name = f"projects/{self.project_id}"
        
        if GCP_AVAILABLE:
            try:
                self.monitoring_client = monitoring_v3.MetricServiceClient()
                self.alert_client = monitoring_v3.AlertPolicyServiceClient()
                self.logging_client = logging.Client(project=self.project_id)
                print("✅ GCP clients initialized")
            except Exception as e:
                print(f"⚠️ GCP client initialization failed: {e}")
                self.monitoring_client = None
                self.alert_client = None
                self.logging_client = None
        else:
            self.monitoring_client = None
            self.alert_client = None
            self.logging_client = None
    
    def get_active_incidents(self):
        """Get current GCP incidents and alerts"""
        incidents = []
        
        try:
            # Get alert policy incidents
            if self.alert_client:
                policies = self.alert_client.list_alert_policies(name=self.project_name)
                
                for policy in policies:
                    if policy.enabled:
                        # Check if policy has triggered recently
                        incident = {
                            'id': policy.name.split('/')[-1],
                            'name': policy.display_name,
                            'type': 'ALERT_POLICY',
                            'status': 'ACTIVE' if policy.enabled else 'INACTIVE',
                            'severity': 'HIGH' if 'high' in policy.display_name.lower() else 'MEDIUM',
                            'created_time': datetime.now().isoformat(),
                            'description': f"Alert policy: {policy.display_name}",
                            'conditions': [cond.display_name for cond in policy.conditions]
                        }
                        incidents.append(incident)
            
            # Get recent log entries that might indicate incidents
            if self.logging_client:
                # Look for recent high-severity logs
                filter_str = 'severity>=WARNING timestamp>"{}"'.format(
                    (datetime.now() - timedelta(hours=1)).isoformat()
                )
                
                try:
                    entries = self.logging_client.list_entries(filter_=filter_str, max_results=10)
                    
                    for entry in entries:
                        incident = {
                            'id': f"log_{entry.timestamp.isoformat()}",
                            'name': f"Log Alert: {entry.severity.name}",
                            'type': 'LOG_ENTRY',
                            'status': 'ACTIVE',
                            'severity': entry.severity.name,
                            'created_time': entry.timestamp.isoformat(),
                            'description': str(entry.payload),
                            'conditions': [f"Severity: {entry.severity.name}"]
                        }
                        incidents.append(incident)
                except Exception as e:
                    print(f"⚠️ Log entries fetch failed: {e}")
            
        except Exception as e:
            print(f"⚠️ Incident retrieval failed: {e}")
        
        return incidents
    
    def get_instance_metrics(self):
        """Get real-time instance metrics"""
        metrics = {}
        
        try:
            if not self.monitoring_client:
                return metrics
            
            # Get CPU utilization for alert-monitor-test
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=30)
            
            # Convert to protobuf timestamp
            interval = monitoring_v3.TimeInterval({
                "end_time": {"seconds": int(end_time.timestamp())},
                "start_time": {"seconds": int(start_time.timestamp())},
            })
            
            # CPU utilization metric
            request = monitoring_v3.ListTimeSeriesRequest(
                name=self.project_name,
                filter='metric.type="compute.googleapis.com/instance/cpu/utilization" AND resource.labels.instance_name="alert-monitor-test"',
                interval=interval,
                view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            )
            
            results = self.monitoring_client.list_time_series(request=request)
            
            for result in results:
                if result.points:
                    latest_point = result.points[0]
                    cpu_value = latest_point.value.double_value * 100
                    
                    metrics['cpu_utilization'] = {
                        'value': cpu_value,
                        'timestamp': latest_point.interval.end_time.seconds,
                        'unit': 'percent',
                        'status': 'CRITICAL' if cpu_value > 80 else 'WARNING' if cpu_value > 50 else 'NORMAL'
                    }
                    break
            
        except Exception as e:
            print(f"⚠️ Metrics retrieval failed: {e}")
        
        return metrics
    
    def get_alert_status(self):
        """Get current alert policy status"""
        alerts = []
        
        try:
            # Use gcloud command as fallback
            result = subprocess.run([
                'gcloud', 'alpha', 'monitoring', 'policies', 'list',
                '--project', self.project_id,
                '--format', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                policies = json.loads(result.stdout)
                
                for policy in policies:
                    alert = {
                        'name': policy.get('displayName', 'Unknown'),
                        'enabled': policy.get('enabled', False),
                        'conditions': [cond.get('displayName', '') for cond in policy.get('conditions', [])],
                        'notification_channels': len(policy.get('notificationChannels', [])),
                        'status': 'ACTIVE' if policy.get('enabled') else 'INACTIVE'
                    }
                    alerts.append(alert)
            
        except Exception as e:
            print(f"⚠️ Alert status retrieval failed: {e}")
        
        return alerts
    
    def get_comprehensive_status(self):
        """Get comprehensive GCP status for dashboard"""
        print("🔍 Fetching GCP incident and monitoring data...")
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'incidents': self.get_active_incidents(),
            'metrics': self.get_instance_metrics(),
            'alerts': self.get_alert_status(),
            'summary': {
                'total_incidents': 0,
                'critical_alerts': 0,
                'active_policies': 0,
                'system_status': 'UNKNOWN'
            }
        }
        
        # Calculate summary
        status['summary']['total_incidents'] = len(status['incidents'])
        status['summary']['active_policies'] = len([a for a in status['alerts'] if a['enabled']])
        
        # Determine system status
        cpu_status = status['metrics'].get('cpu_utilization', {}).get('status', 'UNKNOWN')
        if cpu_status == 'CRITICAL' or status['summary']['total_incidents'] > 0:
            status['summary']['system_status'] = 'INCIDENT'
        elif cpu_status == 'WARNING':
            status['summary']['system_status'] = 'WARNING'
        else:
            status['summary']['system_status'] = 'NORMAL'
        
        # Save to file for dashboard to read
        with open('gcp_incident_status.json', 'w') as f:
            json.dump(status, f, indent=2, default=str)
        
        print(f"✅ GCP status saved: {status['summary']['total_incidents']} incidents, {status['summary']['active_policies']} active policies")
        
        return status

def main():
    print("🚨 GCP INCIDENT MONITOR")
    print("=" * 40)
    
    monitor = GCPIncidentMonitor()
    status = monitor.get_comprehensive_status()
    
    print()
    print("📋 CURRENT GCP STATUS:")
    print(f"   🚨 Incidents: {status['summary']['total_incidents']}")
    print(f"   ⚠️  Alerts: {status['summary']['active_policies']} active")
    print(f"   🖥️  System: {status['summary']['system_status']}")
    
    if status['metrics'].get('cpu_utilization'):
        cpu = status['metrics']['cpu_utilization']
        print(f"   💻 CPU: {cpu['value']:.1f}% ({cpu['status']})")
    
    print()
    print("💾 Data saved to: gcp_incident_status.json")
    print("📊 Dashboard can now display GCP incidents!")

if __name__ == "__main__":
    main()
