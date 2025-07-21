"""
Azure Monitor Integration Module
Connects threat detection system to Azure Monitor metrics
"""

from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, MetricsQueryClient
import pandas as pd
from datetime import datetime, timedelta
import json

class AzureMonitorConnector:
    def __init__(self, subscription_id):
        """
        Initialize Azure Monitor connection
        
        Setup Azure credentials first:
        1. Install Azure CLI: pip install azure-cli azure-monitor-query azure-identity
        2. Login: az login
        3. Set subscription: az account set --subscription "your-subscription-id"
        """
        self.subscription_id = subscription_id
        try:
            self.credential = DefaultAzureCredential()
            self.logs_client = LogsQueryClient(self.credential)
            self.metrics_client = MetricsQueryClient(self.credential)
            print(f"✅ Connected to Azure Monitor for subscription: {subscription_id}")
        except Exception as e:
            print(f"❌ Azure connection failed: {e}")
            print("💡 Setup instructions:")
            print("   1. pip install azure-cli azure-monitor-query azure-identity")
            print("   2. az login")
            print("   3. az account set --subscription 'your-subscription-id'")
    
    def get_vm_metrics(self, resource_group, hours=24):
        """
        Fetch Virtual Machine metrics from Azure Monitor
        
        Args:
            resource_group: Azure resource group name
            hours: Number of hours of historical data to fetch
        """
        try:
            # KQL query to get VM performance data
            kql_query = f"""
            Perf
            | where TimeGenerated > ago({hours}h)
            | where ObjectName == "Processor" and CounterName == "% Processor Time"
                or ObjectName == "Network Adapter" and CounterName == "Bytes Total/sec"
                or ObjectName == "Memory" and CounterName == "Available MBytes"
            | summarize avg(CounterValue) by bin(TimeGenerated, 5m), Computer, CounterName
            | order by TimeGenerated desc
            """
            
            # Execute query
            response = self.logs_client.query_workspace(
                workspace_id="your-workspace-id",  # Replace with actual Log Analytics workspace ID
                query=kql_query,
                timespan=timedelta(hours=hours)
            )
            
            data = []
            for table in response.tables:
                for row in table.rows:
                    timestamp = row[0]
                    computer = row[1]
                    counter_name = row[2]
                    value = row[3]
                    
                    data.append({
                        'timestamp': timestamp,
                        'computer': computer,
                        'metric': counter_name,
                        'value': value
                    })
            
            df = pd.DataFrame(data)
            
            # Transform to our standard format
            processed_data = self._transform_azure_data(df)
            print(f"✅ Fetched {len(processed_data)} data points from Azure Monitor")
            return processed_data
            
        except Exception as e:
            print(f"❌ Error fetching Azure metrics: {e}")
            return None
    
    def get_security_events(self, resource_group, hours=24):
        """
        Fetch security events from Azure Security Center
        """
        try:
            kql_query = f"""
            SecurityEvent
            | where TimeGenerated > ago({hours}h)
            | where EventID in (4624, 4625, 4648, 4672)  // Login events
            | summarize count() by bin(TimeGenerated, 5m), Computer, EventID
            | order by TimeGenerated desc
            """
            
            response = self.logs_client.query_workspace(
                workspace_id="your-workspace-id",
                query=kql_query,
                timespan=timedelta(hours=hours)
            )
            
            events = []
            for table in response.tables:
                for row in table.rows:
                    events.append({
                        'timestamp': row[0],
                        'computer': row[1],
                        'event_id': row[2],
                        'count': row[3]
                    })
            
            df = pd.DataFrame(events)
            print(f"✅ Fetched {len(df)} security events from Azure")
            return df
            
        except Exception as e:
            print(f"❌ Error fetching Azure security events: {e}")
            return pd.DataFrame()
    
    def _transform_azure_data(self, df):
        """Transform Azure data to our standard format"""
        if df.empty:
            return pd.DataFrame()
        
        # Pivot the data to get metrics as columns
        pivot_df = df.pivot_table(
            index=['timestamp', 'computer'], 
            columns='metric', 
            values='value', 
            aggfunc='mean'
        ).reset_index()
        
        # Normalize column names and values
        result = []
        for _, row in pivot_df.iterrows():
            cpu_usage = row.get('% Processor Time', 0) / 100  # Normalize to 0-1
            network_traffic = row.get('Bytes Total/sec', 0) / 1000000  # Convert to MB/s
            
            result.append({
                'timestamp': row['timestamp'],
                'computer': row['computer'],
                'cpu_usage': max(0, min(1, cpu_usage)),  # Ensure 0-1 range
                'network_traffic': max(0, network_traffic),
                'login_attempts': self._estimate_login_attempts()  # Placeholder
            })
        
        return pd.DataFrame(result)
    
    def _estimate_login_attempts(self):
        """Placeholder for login attempts estimation"""
        import random
        return random.randint(0, 10)
    
    def setup_azure_alerts(self, resource_group):
        """
        Setup Azure Monitor alerts for anomaly detection
        """
        print("💡 To setup Azure alerts:")
        print("1. Use Azure CLI or Azure Portal")
        print("2. Create metric alerts for CPU, Network, Memory")
        print("3. Configure action groups for notifications")
        print("4. Example CLI command:")
        print("   az monitor metrics alert create --name 'HighCPU' --resource-group", resource_group)

# Example usage
if __name__ == "__main__":
    print("🔧 Azure Monitor Integration Test")
    print("=" * 40)
    
    # Test connection (replace with your subscription ID)
    connector = AzureMonitorConnector("your-subscription-id")
    
    print("\n📚 Next steps to connect to Azure:")
    print("1. Install Azure CLI: pip install azure-cli azure-monitor-query")
    print("2. Login: az login")
    print("3. Get subscription ID: az account show")
    print("4. Update the subscription_id in this script")
    print("5. Get Log Analytics workspace ID from Azure portal")
