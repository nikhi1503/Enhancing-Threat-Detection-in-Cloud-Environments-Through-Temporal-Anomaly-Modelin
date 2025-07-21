"""
Google Cloud Monitoring Integration Module
Connects threat detection system to Google Cloud Monitoring (formerly Stackdriver)
"""

from google.cloud import monitoring_v3
from google.cloud import logging
import pandas as pd
from datetime import datetime, timedelta
import json

class GCPMonitoringConnector:
    def __init__(self, project_id):
        """
        Initialize GCP Monitoring connection
        
        Setup GCP credentials first:
        1. Install GCP SDK: pip install google-cloud-monitoring google-cloud-logging
        2. Setup authentication: gcloud auth application-default login
        3. Set project: gcloud config set project your-project-id
        """
        self.project_id = project_id
        self.project_name = f"projects/{project_id}"
        
        try:
            self.monitoring_client = monitoring_v3.MetricServiceClient()
            self.logging_client = logging.Client(project=project_id)
            print(f"✅ Connected to GCP Monitoring for project: {project_id}")
        except Exception as e:
            print(f"❌ GCP connection failed: {e}")
            print("💡 Setup instructions:")
            print("   1. pip install google-cloud-monitoring google-cloud-logging")
            print("   2. gcloud auth application-default login")
            print("   3. gcloud config set project your-project-id")
    
    def get_compute_metrics(self, hours=24):
        """
        Fetch Compute Engine metrics from Cloud Monitoring
        
        Args:
            hours: Number of hours of historical data to fetch
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Convert to protobuf timestamp
            interval = monitoring_v3.TimeInterval({
                "end_time": {"seconds": int(end_time.timestamp())},
                "start_time": {"seconds": int(start_time.timestamp())},
            })
            
            all_data = []
            
            # CPU Utilization
            cpu_data = self._get_metric_data(
                "compute.googleapis.com/instance/cpu/utilization",
                interval
            )
            
            # Network bytes
            network_data = self._get_metric_data(
                "compute.googleapis.com/instance/network/received_bytes_count",
                interval
            )
            
            # Combine metrics by instance and timestamp
            combined_data = self._combine_gcp_metrics(cpu_data, network_data)
            
            print(f"✅ Fetched {len(combined_data)} data points from GCP Monitoring")
            return combined_data
            
        except Exception as e:
            print(f"❌ Error fetching GCP metrics: {e}")
            return None
    
    def _get_metric_data(self, metric_type, interval):
        """Helper method to fetch specific metric data"""
        try:
            results = self.monitoring_client.list_time_series(
                request={
                    "name": self.project_name,
                    "filter": f'metric.type="{metric_type}"',
                    "interval": interval,
                    "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                }
            )
            
            data = []
            for result in results:
                instance_id = result.resource.labels.get('instance_id', 'unknown')
                zone = result.resource.labels.get('zone', 'unknown')
                
                for point in result.points:
                    timestamp = point.interval.end_time.timestamp()
                    value = point.value.double_value
                    
                    data.append({
                        'timestamp': datetime.fromtimestamp(timestamp),
                        'instance_id': instance_id,
                        'zone': zone,
                        'metric_type': metric_type,
                        'value': value
                    })
            
            return data
            
        except Exception as e:
            print(f"❌ Error fetching metric {metric_type}: {e}")
            return []
    
    def _combine_gcp_metrics(self, cpu_data, network_data):
        """Combine different metrics into our standard format"""
        combined = {}
        
        # Process CPU data
        for point in cpu_data:
            key = (point['timestamp'], point['instance_id'])
            if key not in combined:
                combined[key] = {
                    'timestamp': point['timestamp'],
                    'instance_id': point['instance_id'],
                    'zone': point['zone'],
                    'cpu_usage': 0,
                    'network_traffic': 0,
                    'login_attempts': 0
                }
            combined[key]['cpu_usage'] = point['value']
        
        # Process network data
        for point in network_data:
            key = (point['timestamp'], point['instance_id'])
            if key not in combined:
                combined[key] = {
                    'timestamp': point['timestamp'],
                    'instance_id': point['instance_id'],
                    'zone': point['zone'],
                    'cpu_usage': 0,
                    'network_traffic': 0,
                    'login_attempts': 0
                }
            combined[key]['network_traffic'] = point['value'] / 1000000  # Convert to MB
        
        # Add estimated login attempts
        for key in combined:
            combined[key]['login_attempts'] = self._estimate_login_attempts()
        
        return pd.DataFrame(list(combined.values()))
    
    def get_security_logs(self, hours=24):
        """
        Fetch security-related logs from Cloud Logging
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Query for authentication and security events
            filter_str = f'''
            timestamp >= "{start_time.isoformat()}Z"
            AND timestamp <= "{end_time.isoformat()}Z"
            AND (
                resource.type="gce_instance"
                OR protoPayload.serviceName="compute.googleapis.com"
            )
            AND (
                protoPayload.methodName="compute.instances.start"
                OR protoPayload.methodName="compute.instances.stop"
                OR severity="ERROR"
            )
            '''
            
            entries = list(self.logging_client.list_entries(filter_=filter_str))
            
            events = []
            for entry in entries:
                events.append({
                    'timestamp': entry.timestamp,
                    'severity': entry.severity,
                    'log_name': entry.log_name,
                    'resource_type': entry.resource.type if entry.resource else 'unknown',
                    'method_name': getattr(entry.payload, 'method_name', 'unknown') if hasattr(entry, 'payload') else 'unknown'
                })
            
            df = pd.DataFrame(events)
            print(f"✅ Fetched {len(df)} security log entries from GCP")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching GCP security logs: {e}")
            return pd.DataFrame()
    
    def _estimate_login_attempts(self):
        """Placeholder for login attempts estimation"""
        import random
        return random.randint(0, 10)
    
    def setup_gcp_alerts(self):
        """
        Setup Cloud Monitoring alerts
        """
        try:
            # Create alert policy for high CPU
            alert_policy = monitoring_v3.AlertPolicy(
                display_name="High CPU Usage - Threat Detection",
                conditions=[
                    monitoring_v3.AlertPolicy.Condition(
                        display_name="CPU usage above 80%",
                        condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                            filter='metric.type="compute.googleapis.com/instance/cpu/utilization"',
                            comparison=monitoring_v3.ComparisonType.COMPARISON_GREATER_THAN,
                            threshold_value=0.8,
                            duration={"seconds": 300},
                            aggregations=[
                                monitoring_v3.Aggregation(
                                    alignment_period={"seconds": 300},
                                    per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
                                )
                            ],
                        )
                    )
                ],
                combiner=monitoring_v3.AlertPolicy.ConditionCombinerType.AND,
                enabled=True,
            )
            
            policy = self.monitoring_client.create_alert_policy(
                name=self.project_name, alert_policy=alert_policy
            )
            print(f"✅ Created GCP alert policy: {policy.name}")
            
        except Exception as e:
            print(f"❌ Error creating GCP alerts: {e}")

# Example usage
if __name__ == "__main__":
    print("🔧 GCP Monitoring Integration Test")
    print("=" * 40)
    
    # Test connection (replace with your project ID)
    connector = GCPMonitoringConnector("your-project-id")
    
    print("\n📚 Next steps to connect to GCP:")
    print("1. Install GCP SDK: pip install google-cloud-monitoring google-cloud-logging")
    print("2. Setup auth: gcloud auth application-default login")
    print("3. Set project: gcloud config set project your-project-id")
    print("4. Update the project_id in this script")
    print("5. Enable Cloud Monitoring API in GCP Console")
