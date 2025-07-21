"""
Cloud Integration Manager
Unified interface for connecting to multiple cloud providers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud_integration.aws_connector import AWSCloudWatchConnector
from cloud_integration.azure_connector import AzureMonitorConnector
from cloud_integration.gcp_connector import GCPMonitoringConnector
from anomaly_detection.temporal_models import TemporalAnomalyDetector
from reporting.advanced_reporter import ThreatDetectionReporter
import pandas as pd
from datetime import datetime

class CloudIntegrationManager:
    def __init__(self):
        """Initialize cloud integration manager"""
        self.connectors = {}
        self.detector = TemporalAnomalyDetector(contamination=0.15)
        self.reporter = ThreatDetectionReporter()
    
    def setup_aws(self, region='us-east-1'):
        """Setup AWS CloudWatch connection"""
        try:
            self.connectors['aws'] = AWSCloudWatchConnector(region)
            return True
        except Exception as e:
            print(f"❌ AWS setup failed: {e}")
            return False
    
    def setup_azure(self, subscription_id):
        """Setup Azure Monitor connection"""
        try:
            self.connectors['azure'] = AzureMonitorConnector(subscription_id)
            return True
        except Exception as e:
            print(f"❌ Azure setup failed: {e}")
            return False
    
    def setup_gcp(self, project_id):
        """Setup GCP Monitoring connection"""
        try:
            self.connectors['gcp'] = GCPMonitoringConnector(project_id)
            return True
        except Exception as e:
            print(f"❌ GCP setup failed: {e}")
            return False
    
    def collect_cloud_data(self, provider, hours=24, **kwargs):
        """
        Collect data from specified cloud provider
        
        Args:
            provider: 'aws', 'azure', or 'gcp'
            hours: Hours of historical data to collect
            **kwargs: Provider-specific parameters
        """
        if provider not in self.connectors:
            print(f"❌ {provider.upper()} not configured. Run setup_{provider}() first.")
            return None
        
        connector = self.connectors[provider]
        
        try:
            if provider == 'aws':
                data = connector.get_ec2_metrics(
                    instance_ids=kwargs.get('instance_ids'),
                    hours=hours
                )
            elif provider == 'azure':
                data = connector.get_vm_metrics(
                    resource_group=kwargs.get('resource_group'),
                    hours=hours
                )
            elif provider == 'gcp':
                data = connector.get_compute_metrics(hours=hours)
            
            if data is not None and len(data) > 0:
                print(f"✅ Collected {len(data)} data points from {provider.upper()}")
                return data
            else:
                print(f"⚠️  No data collected from {provider.upper()}")
                return None
                
        except Exception as e:
            print(f"❌ Error collecting data from {provider.upper()}: {e}")
            return None
    
    def run_threat_detection(self, data, output_dir=None):
        """
        Run threat detection on cloud data
        
        Args:
            data: DataFrame with cloud metrics
            output_dir: Directory to save reports
        """
        if data is None or len(data) == 0:
            print("❌ No data to analyze")
            return None
        
        try:
            print("🧠 Running threat detection analysis...")
            
            # Detect anomalies
            results = self.detector.fit_predict(data)
            anomalies = results[results['anomaly'] == -1]
            
            print(f"🚨 Detected {len(anomalies)} anomalies out of {len(results)} data points")
            print(f"📊 Anomaly rate: {len(anomalies)/len(results)*100:.2f}%")
            
            # Generate reports
            if output_dir is None:
                output_dir = f"cloud_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            summary = self.reporter.generate_comprehensive_report(
                results, anomalies, output_dir
            )
            
            return {
                'results': results,
                'anomalies': anomalies,
                'summary': summary,
                'output_dir': output_dir
            }
            
        except Exception as e:
            print(f"❌ Error running threat detection: {e}")
            return None
    
    def setup_cloud_alerts(self, provider, **kwargs):
        """Setup alerts on cloud platform"""
        if provider not in self.connectors:
            print(f"❌ {provider.upper()} not configured")
            return False
        
        try:
            connector = self.connectors[provider]
            
            if provider == 'aws':
                connector.setup_cloudwatch_alarms(**kwargs)
            elif provider == 'azure':
                connector.setup_azure_alerts(kwargs.get('resource_group'))
            elif provider == 'gcp':
                connector.setup_gcp_alerts()
            
            print(f"✅ Alerts configured for {provider.upper()}")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up alerts for {provider.upper()}: {e}")
            return False
    
    def multi_cloud_analysis(self, configs, hours=24):
        """
        Run threat detection across multiple cloud providers
        
        Args:
            configs: List of provider configs
                [
                    {'provider': 'aws', 'region': 'us-east-1'},
                    {'provider': 'azure', 'subscription_id': 'xxx', 'resource_group': 'yyy'},
                    {'provider': 'gcp', 'project_id': 'zzz'}
                ]
        """
        all_results = {}
        
        for config in configs:
            provider = config['provider']
            print(f"\n🔄 Processing {provider.upper()}...")
            
            # Setup connection
            if provider == 'aws':
                if not self.setup_aws(config.get('region', 'us-east-1')):
                    continue
                data = self.collect_cloud_data('aws', hours, 
                                             instance_ids=config.get('instance_ids'))
            elif provider == 'azure':
                if not self.setup_azure(config['subscription_id']):
                    continue
                data = self.collect_cloud_data('azure', hours,
                                             resource_group=config['resource_group'])
            elif provider == 'gcp':
                if not self.setup_gcp(config['project_id']):
                    continue
                data = self.collect_cloud_data('gcp', hours)
            
            # Run analysis
            if data is not None:
                results = self.run_threat_detection(
                    data, 
                    output_dir=f"{provider}_threat_analysis"
                )
                all_results[provider] = results
        
        # Generate combined report
        self._generate_multi_cloud_report(all_results)
        return all_results
    
    def _generate_multi_cloud_report(self, all_results):
        """Generate a combined multi-cloud report"""
        total_data_points = 0
        total_anomalies = 0
        
        print("\n" + "="*60)
        print("MULTI-CLOUD THREAT DETECTION SUMMARY")
        print("="*60)
        
        for provider, results in all_results.items():
            if results:
                data_points = len(results['results'])
                anomalies = len(results['anomalies'])
                total_data_points += data_points
                total_anomalies += anomalies
                
                print(f"{provider.upper():8} | {data_points:6} points | {anomalies:4} anomalies | {anomalies/data_points*100:5.1f}%")
        
        print("-"*60)
        print(f"{'TOTAL':8} | {total_data_points:6} points | {total_anomalies:4} anomalies | {total_anomalies/total_data_points*100 if total_data_points > 0 else 0:5.1f}%")
        print("="*60)

# Example usage and testing
def demo_cloud_integration():
    """Demonstrate cloud integration capabilities"""
    print("🌩️  Cloud Integration Demo")
    print("=" * 50)
    
    manager = CloudIntegrationManager()
    
    # Example configurations (update with real values)
    print("📋 Example cloud configurations:")
    print("""
    # AWS Example:
    manager.setup_aws('us-east-1')
    data = manager.collect_cloud_data('aws', hours=24, instance_ids=['i-1234567890abcdef0'])
    
    # Azure Example:
    manager.setup_azure('your-subscription-id')
    data = manager.collect_cloud_data('azure', hours=24, resource_group='your-rg')
    
    # GCP Example:
    manager.setup_gcp('your-project-id')
    data = manager.collect_cloud_data('gcp', hours=24)
    
    # Multi-cloud analysis:
    configs = [
        {'provider': 'aws', 'region': 'us-east-1'},
        {'provider': 'azure', 'subscription_id': 'xxx', 'resource_group': 'yyy'},
        {'provider': 'gcp', 'project_id': 'zzz'}
    ]
    results = manager.multi_cloud_analysis(configs)
    """)
    
    print("\n🔧 Setup Requirements:")
    print("1. AWS: pip install boto3 awscli → aws configure")
    print("2. Azure: pip install azure-cli azure-monitor-query → az login")
    print("3. GCP: pip install google-cloud-monitoring → gcloud auth login")

if __name__ == "__main__":
    demo_cloud_integration()
