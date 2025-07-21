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
        """Get current GCP incidents and alerts that are actually firing"""
        incidents = []
        
        try:
            # NOTE: Only add actual incidents here, not just enabled policies
            # Enabled policies are tracked separately in get_alert_status()
            
            # Get incidents from Cloud Monitoring notifications or metrics that exceed thresholds
            # For now, we'll check if any current metrics exceed policy thresholds
            current_metrics = self.get_instance_metrics()
            
            if self.alert_client:
                policies = self.alert_client.list_alert_policies(name=self.project_name)
                
                for policy in policies:
                    if policy.enabled:
                        # Only create incident if policy conditions are actually met
                        policy_triggered = False
                        
                        # Check if current metrics trigger this policy
                        for condition in policy.conditions:
                            condition_name = condition.display_name.lower()
                            
                            # Check CPU threshold conditions
                            if 'cpu' in condition_name and 'utilization' in condition_name:
                                cpu_data = current_metrics.get('cpu_utilization', {})
                                current_cpu = cpu_data.get('value', 0)
                                
                                # Extract threshold from condition name
                                if '80%' in condition_name and current_cpu > 80:
                                    policy_triggered = True
                                elif '50%' in condition_name and current_cpu > 50:
                                    policy_triggered = True
                        
                        # Only create incident if policy is actually triggered
                        if policy_triggered:
                            incident = {
                                'id': policy.name.split('/')[-1],
                                'name': f"TRIGGERED: {policy.display_name}",
                                'type': 'ALERT_TRIGGERED',
                                'status': 'FIRING',
                                'severity': 'HIGH' if 'high' in policy.display_name.lower() else 'MEDIUM',
                                'created_time': datetime.now().isoformat(),
                                'description': f"Alert policy triggered: {policy.display_name}",
                                'conditions': [cond.display_name for cond in policy.conditions],
                                'current_metrics': current_metrics
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
        """Get real-time instance metrics using gcloud commands"""
        metrics = {}
        
        try:
            # First try using gcloud to get CPU metrics
            print("🔍 Fetching real-time CPU metrics from GCP...")
            
            # Get current time for metrics query
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=10)
            
            # Format timestamps for gcloud
            start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Use gcloud to fetch CPU utilization
            cpu_cmd = [
                'gcloud', 'monitoring', 'time-series', 'list',
                '--project', self.project_id,
                '--filter', f'metric.type="compute.googleapis.com/instance/cpu/utilization" AND resource.labels.instance_name="alert-monitor-test"',
                '--interval-end-time', end_str,
                '--interval-start-time', start_str,
                '--format', 'json'
            ]
            
            try:
                result = subprocess.run(cpu_cmd, capture_output=True, text=True, timeout=20)
                
                if result.returncode == 0 and result.stdout.strip():
                    cpu_data = json.loads(result.stdout)
                    
                    if cpu_data and len(cpu_data) > 0:
                        # Get the latest point
                        latest_series = cpu_data[0]
                        if 'points' in latest_series and latest_series['points']:
                            latest_point = latest_series['points'][0]
                            cpu_value = float(latest_point['value']['doubleValue']) * 100
                            
                            metrics['cpu_utilization'] = {
                                'value': round(cpu_value, 2),
                                'timestamp': latest_point['interval']['endTime'],
                                'unit': 'percent',
                                'status': 'CRITICAL' if cpu_value > 80 else 'WARNING' if cpu_value > 50 else 'NORMAL',
                                'instance_name': 'alert-monitor-test',
                                'source': 'gcloud_monitoring'
                            }
                            print(f"✅ Real-time CPU: {cpu_value:.2f}% ({metrics['cpu_utilization']['status']})")
                        else:
                            print("⚠️ No recent CPU data points found")
                    else:
                        print("⚠️ No CPU time series data returned")
                else:
                    print(f"⚠️ gcloud CPU query failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("⚠️ CPU metrics query timed out")
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse CPU metrics JSON: {e}")
            
            # Also try to get some basic instance info
            try:
                instance_cmd = [
                    'gcloud', 'compute', 'instances', 'describe', 'alert-monitor-test',
                    '--project', self.project_id,
                    '--zone', 'us-central1-a',
                    '--format', 'json'
                ]
                
                result = subprocess.run(instance_cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    instance_data = json.loads(result.stdout)
                    
                    metrics['instance_info'] = {
                        'status': instance_data.get('status', 'UNKNOWN'),
                        'machine_type': instance_data.get('machineType', '').split('/')[-1],
                        'zone': instance_data.get('zone', '').split('/')[-1],
                        'last_start': instance_data.get('lastStartTimestamp', ''),
                        'source': 'gcloud_compute'
                    }
                    print(f"✅ Instance status: {metrics['instance_info']['status']}")
                    
            except Exception as inst_e:
                print(f"ℹ️ Instance info not available: {inst_e}")
            
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
        
        # Determine system status based on actual incidents and metrics
        cpu_status = status['metrics'].get('cpu_utilization', {}).get('status', 'UNKNOWN')
        actual_incidents = len([i for i in status['incidents'] if i.get('status') == 'FIRING'])
        
        if actual_incidents > 0 or cpu_status == 'CRITICAL':
            status['summary']['system_status'] = 'INCIDENT'
        elif cpu_status == 'WARNING':
            status['summary']['system_status'] = 'WARNING'
        else:
            status['summary']['system_status'] = 'NORMAL'
        
        # Save to file for dashboard to read
        with open('gcp_incident_status.json', 'w') as f:
            json.dump(status, f, indent=2, default=str)
        
        print(f"✅ GCP status saved: {status['summary']['total_incidents']} triggered incidents, {status['summary']['active_policies']} active policies")
        
        return status

def main():
    print("🚨 GCP INCIDENT MONITOR")
    print("=" * 40)
    
    try:
        monitor = GCPIncidentMonitor()
        print("✅ Monitor instance created")
        
        status = monitor.get_comprehensive_status()
        print("✅ Status retrieved")
        
        print()
        print("📋 CURRENT GCP STATUS:")
        print(f"   🚨 Triggered Incidents: {status['summary']['total_incidents']}")
        print(f"   ⚠️  Alert Policies: {status['summary']['active_policies']} active")
        print(f"   🖥️  System: {status['summary']['system_status']}")
        
        if status['metrics'].get('cpu_utilization'):
            cpu = status['metrics']['cpu_utilization']
            print(f"   💻 CPU: {cpu['value']:.1f}% ({cpu['status']})")
        
        print()
        print("💾 Data saved to: gcp_incident_status.json")
        print("📊 Dashboard can now display GCP incidents!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
