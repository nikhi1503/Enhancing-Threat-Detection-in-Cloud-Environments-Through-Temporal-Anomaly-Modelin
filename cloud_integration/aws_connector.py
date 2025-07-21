"""
AWS CloudWatch Integration Module
Connects threat detection system to AWS CloudWatch metrics
"""

import boto3
import pandas as pd
from datetime import datetime, timedelta
import json
import time

class AWSCloudWatchConnector:
    def __init__(self, region_name='us-east-1'):
        """
        Initialize AWS CloudWatch connection
        
        Setup AWS credentials first:
        1. Install AWS CLI: pip install awscli boto3
        2. Configure credentials: aws configure
        3. Or use IAM roles if running on EC2
        """
        try:
            self.cloudwatch = boto3.client('cloudwatch', region_name=region_name)
            self.ec2 = boto3.client('ec2', region_name=region_name)
            self.region = region_name
            print(f"✅ Connected to AWS CloudWatch in {region_name}")
        except Exception as e:
            print(f"❌ AWS Connection failed: {e}")
            print("💡 Setup instructions:")
            print("   1. pip install boto3 awscli")
            print("   2. aws configure")
            print("   3. Enter your AWS Access Key ID and Secret")
    
    def get_ec2_metrics(self, instance_ids=None, hours=24):
        """
        Fetch EC2 instance metrics from CloudWatch
        
        Args:
            instance_ids: List of EC2 instance IDs (if None, gets all)
            hours: Number of hours of historical data to fetch
        """
        try:
            # Get all EC2 instances if none specified
            if instance_ids is None:
                response = self.ec2.describe_instances()
                instance_ids = []
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        if instance['State']['Name'] == 'running':
                            instance_ids.append(instance['InstanceId'])
            
            print(f"📊 Fetching metrics for {len(instance_ids)} instances...")
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            all_data = []
            
            for instance_id in instance_ids:
                # CPU Utilization
                cpu_data = self._get_metric_data(
                    namespace='AWS/EC2',
                    metric_name='CPUUtilization',
                    dimension_name='InstanceId',
                    dimension_value=instance_id,
                    start_time=start_time,
                    end_time=end_time
                )
                
                # Network In
                network_in_data = self._get_metric_data(
                    namespace='AWS/EC2',
                    metric_name='NetworkIn',
                    dimension_name='InstanceId',
                    dimension_value=instance_id,
                    start_time=start_time,
                    end_time=end_time
                )
                
                # Network Out
                network_out_data = self._get_metric_data(
                    namespace='AWS/EC2',
                    metric_name='NetworkOut',
                    dimension_name='InstanceId',
                    dimension_value=instance_id,
                    start_time=start_time,
                    end_time=end_time
                )
                
                # Combine metrics
                for i, timestamp in enumerate(cpu_data['timestamps']):
                    network_in = network_in_data['values'][i] if i < len(network_in_data['values']) else 0
                    network_out = network_out_data['values'][i] if i < len(network_out_data['values']) else 0
                    
                    all_data.append({
                        'timestamp': timestamp,
                        'instance_id': instance_id,
                        'cpu_usage': cpu_data['values'][i] / 100,  # Normalize to 0-1
                        'network_traffic': (network_in + network_out) / 1000000,  # Convert to MB
                        'login_attempts': self._estimate_login_attempts(),  # Simulated for demo
                    })
            
            df = pd.DataFrame(all_data)
            print(f"✅ Fetched {len(df)} data points from AWS CloudWatch")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching AWS metrics: {e}")
            return None
    
    def _get_metric_data(self, namespace, metric_name, dimension_name, dimension_value, start_time, end_time):
        """Helper method to fetch specific metric data"""
        try:
            response = self.cloudwatch.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=[{
                    'Name': dimension_name,
                    'Value': dimension_value
                }],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5-minute intervals
                Statistics=['Average']
            )
            
            timestamps = [point['Timestamp'] for point in response['Datapoints']]
            values = [point['Average'] for point in response['Datapoints']]
            
            # Sort by timestamp
            sorted_data = sorted(zip(timestamps, values))
            timestamps, values = zip(*sorted_data) if sorted_data else ([], [])
            
            return {
                'timestamps': list(timestamps),
                'values': list(values)
            }
        except Exception as e:
            print(f"❌ Error fetching {metric_name}: {e}")
            return {'timestamps': [], 'values': []}
    
    def _estimate_login_attempts(self):
        """
        Estimate login attempts (placeholder)
        In real implementation, you would:
        1. Parse CloudTrail logs for authentication events
        2. Use AWS Config for security events
        3. Integrate with VPC Flow Logs
        """
        import random
        return random.randint(0, 10)
    
    def get_cloudtrail_logs(self, hours=24):
        """
        Fetch CloudTrail logs for security events
        """
        try:
            cloudtrail = boto3.client('cloudtrail', region_name=self.region)
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            response = cloudtrail.lookup_events(
                StartTime=start_time,
                EndTime=end_time,
                MaxItems=1000
            )
            
            events = []
            for event in response.get('Events', []):
                if event.get('EventName') in ['ConsoleLogin', 'AssumeRole', 'GetSessionToken']:
                    events.append({
                        'timestamp': event['EventTime'],
                        'event_name': event['EventName'],
                        'user_name': event.get('Username', 'Unknown'),
                        'source_ip': event.get('SourceIPAddress', 'Unknown'),
                        'user_agent': event.get('UserAgent', 'Unknown')
                    })
            
            print(f"✅ Fetched {len(events)} CloudTrail security events")
            return pd.DataFrame(events)
            
        except Exception as e:
            print(f"❌ Error fetching CloudTrail logs: {e}")
            return pd.DataFrame()
    
    def setup_cloudwatch_alarms(self, threshold_cpu=80, threshold_network=1000000):
        """
        Setup CloudWatch alarms for anomaly detection
        """
        try:
            # CPU alarm
            self.cloudwatch.put_metric_alarm(
                AlarmName='ThreatDetection-HighCPU',
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=2,
                MetricName='CPUUtilization',
                Namespace='AWS/EC2',
                Period=300,
                Statistic='Average',
                Threshold=threshold_cpu,
                ActionsEnabled=True,
                AlarmDescription='High CPU usage detected - potential security threat',
                Unit='Percent'
            )
            
            print("✅ CloudWatch alarms configured")
            
        except Exception as e:
            print(f"❌ Error setting up alarms: {e}")

# Example usage and testing
if __name__ == "__main__":
    print("🔧 AWS CloudWatch Integration Test")
    print("=" * 40)
    
    # Test connection (will show setup instructions if not configured)
    connector = AWSCloudWatchConnector()
    
    # Example of how to use (uncomment when AWS is configured):
    # data = connector.get_ec2_metrics(hours=2)
    # if data is not None:
    #     print(f"Sample data:\n{data.head()}")
    
    print("\n📚 Next steps to connect to AWS:")
    print("1. Install AWS CLI: pip install boto3 awscli")
    print("2. Configure credentials: aws configure")
    print("3. Uncomment the test code above")
    print("4. Run this script to fetch real AWS data")
