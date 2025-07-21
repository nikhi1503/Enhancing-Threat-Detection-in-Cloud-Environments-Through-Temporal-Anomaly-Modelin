"""
Real-time Cloud Data Stream Processor
Simulates real-time data collection and processing
"""

import asyncio
import websockets
import json
import pandas as pd
from datetime import datetime, timedelta
import random
import threading
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anomaly_detection.temporal_models import TemporalAnomalyDetector
from cloud_integration.manager import CloudIntegrationManager

class RealTimeProcessor:
    def __init__(self, update_interval=30):
        """
        Initialize real-time processor
        
        Args:
            update_interval: Seconds between data updates
        """
        self.update_interval = update_interval
        self.detector = TemporalAnomalyDetector(contamination=0.1)
        self.is_trained = False
        self.running = False
        self.data_buffer = []
        self.max_buffer_size = 1000
        self.alerts = []
        
    def simulate_real_time_data(self):
        """Generate realistic real-time cloud data"""
        base_time = datetime.now()
        
        # Simulate different cloud instances
        instances = ['web-server-1', 'db-server-1', 'api-server-1', 'cache-server-1']
        
        data_point = {
            'timestamp': base_time,
            'instance': random.choice(instances),
            'cpu_usage': self._generate_cpu_usage(),
            'network_traffic': self._generate_network_traffic(),
            'login_attempts': self._generate_login_attempts(),
            'memory_usage': random.uniform(0.3, 0.9),
            'disk_io': random.uniform(0.1, 0.8)
        }
        
        # Occasionally simulate attacks
        if random.random() < 0.05:  # 5% chance of attack
            data_point = self._inject_attack(data_point)
        
        return data_point
    
    def _generate_cpu_usage(self):
        """Generate realistic CPU usage with daily patterns"""
        hour = datetime.now().hour
        
        # Higher usage during business hours
        if 9 <= hour <= 17:
            base_cpu = 0.5 + 0.3 * random.random()
        else:
            base_cpu = 0.2 + 0.2 * random.random()
        
        # Add some noise
        return min(1.0, max(0.0, base_cpu + random.gauss(0, 0.1)))
    
    def _generate_network_traffic(self):
        """Generate realistic network traffic"""
        base_traffic = random.uniform(0.1, 0.6)
        return base_traffic + random.gauss(0, 0.05)
    
    def _generate_login_attempts(self):
        """Generate realistic login attempts"""
        hour = datetime.now().hour
        
        # More login attempts during business hours
        if 8 <= hour <= 18:
            return random.poisson(5)
        else:
            return random.poisson(1)
    
    def _inject_attack(self, data_point):
        """Inject attack patterns into data"""
        attack_type = random.choice(['ddos', 'brute_force', 'resource_exhaustion'])
        
        if attack_type == 'ddos':
            data_point['network_traffic'] *= 5
            data_point['cpu_usage'] = min(1.0, data_point['cpu_usage'] * 1.5)
            data_point['attack_type'] = 'ddos'
        elif attack_type == 'brute_force':
            data_point['login_attempts'] += random.randint(20, 100)
            data_point['attack_type'] = 'brute_force'
        elif attack_type == 'resource_exhaustion':
            data_point['cpu_usage'] = min(1.0, data_point['cpu_usage'] + 0.4)
            data_point['memory_usage'] = min(1.0, data_point['memory_usage'] + 0.3)
            data_point['attack_type'] = 'resource_exhaustion'
        
        return data_point
    
    def process_data_point(self, data_point):
        """Process a single data point for anomaly detection"""
        # Add to buffer
        self.data_buffer.append(data_point)
        
        # Maintain buffer size
        if len(self.data_buffer) > self.max_buffer_size:
            self.data_buffer.pop(0)
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(self.data_buffer)
        
        # Train detector if we have enough data
        if len(df) >= 50 and not self.is_trained:
            print("🧠 Training anomaly detector with initial data...")
            self.detector.fit(df)
            self.is_trained = True
            return None
        
        # Detect anomalies if trained
        if self.is_trained and len(df) >= 10:
            try:
                # Use only recent data for prediction
                recent_data = df.tail(10).copy()
                results = self.detector.predict(recent_data)
                
                # Check if latest point is anomaly
                latest_result = results.iloc[-1]
                if latest_result['anomaly'] == -1:
                    alert = {
                        'timestamp': latest_result['timestamp'],
                        'instance': latest_result.get('instance', 'unknown'),
                        'anomaly_score': latest_result.get('anomaly_score', 0),
                        'cpu_usage': latest_result['cpu_usage'],
                        'network_traffic': latest_result['network_traffic'],
                        'login_attempts': latest_result['login_attempts'],
                        'severity': self._calculate_severity(latest_result)
                    }
                    
                    self.alerts.append(alert)
                    return alert
                    
            except Exception as e:
                print(f"⚠️  Error in anomaly detection: {e}")
        
        return None
    
    def _calculate_severity(self, data_point):
        """Calculate alert severity based on metrics"""
        cpu = data_point.get('cpu_usage', 0)
        network = data_point.get('network_traffic', 0)
        logins = data_point.get('login_attempts', 0)
        
        severity_score = 0
        
        if cpu > 0.8:
            severity_score += 3
        elif cpu > 0.6:
            severity_score += 2
        elif cpu > 0.4:
            severity_score += 1
        
        if network > 0.8:
            severity_score += 3
        elif network > 0.5:
            severity_score += 1
        
        if logins > 15:
            severity_score += 3
        elif logins > 8:
            severity_score += 1
        
        if severity_score >= 6:
            return 'CRITICAL'
        elif severity_score >= 4:
            return 'HIGH'
        elif severity_score >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def start_real_time_monitoring(self, duration_minutes=10):
        """Start real-time monitoring for specified duration"""
        print(f"🚀 Starting real-time threat detection monitoring for {duration_minutes} minutes...")
        print("⏱️  Collecting data every", self.update_interval, "seconds")
        
        self.running = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        data_points_processed = 0
        alerts_generated = 0
        
        try:
            while self.running and time.time() < end_time:
                # Generate new data point
                data_point = self.simulate_real_time_data()
                data_points_processed += 1
                
                # Process for anomalies
                alert = self.process_data_point(data_point)
                
                if alert:
                    alerts_generated += 1
                    self._print_alert(alert, data_points_processed)
                else:
                    # Print normal status occasionally
                    if data_points_processed % 10 == 0:
                        print(f"📊 Processed {data_points_processed} data points, {alerts_generated} alerts generated")
                
                # Wait for next update
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
        
        self.running = False
        
        # Final summary
        print(f"\n📋 Real-time Monitoring Summary:")
        print(f"   ⏱️  Duration: {(time.time() - start_time)/60:.1f} minutes")
        print(f"   📊 Data points processed: {data_points_processed}")
        print(f"   🚨 Alerts generated: {alerts_generated}")
        print(f"   📈 Alert rate: {alerts_generated/data_points_processed*100:.1f}%" if data_points_processed > 0 else "   📈 Alert rate: 0%")
        
        return {
            'duration': (time.time() - start_time) / 60,
            'data_points': data_points_processed,
            'alerts': alerts_generated,
            'alert_data': self.alerts[-10:]  # Last 10 alerts
        }
    
    def _print_alert(self, alert, count):
        """Print formatted alert message"""
        severity_colors = {
            'LOW': '🟡',
            'MEDIUM': '🟠', 
            'HIGH': '🔴',
            'CRITICAL': '🚨'
        }
        
        color = severity_colors.get(alert['severity'], '⚪')
        
        print(f"\n{color} THREAT ALERT #{count}")
        print(f"   🕐 Time: {alert['timestamp'].strftime('%H:%M:%S')}")
        print(f"   💻 Instance: {alert['instance']}")
        print(f"   ⚠️  Severity: {alert['severity']}")
        print(f"   📊 CPU: {alert['cpu_usage']:.2f} | Network: {alert['network_traffic']:.2f} | Logins: {alert['login_attempts']}")
        print(f"   🎯 Score: {alert['anomaly_score']:.3f}")

def demo_real_time_processing():
    """Demonstrate real-time processing capabilities"""
    print("⏰ Real-time Cloud Threat Detection Demo")
    print("=" * 50)
    
    processor = RealTimeProcessor(update_interval=5)  # 5-second intervals for demo
    
    print("🎯 This demo will:")
    print("   • Generate simulated real-time cloud data")
    print("   • Train anomaly detection models")
    print("   • Detect threats in real-time")
    print("   • Generate alerts for suspicious activity")
    print("\n⌨️  Press Ctrl+C to stop at any time")
    
    input("\n🚀 Press Enter to start real-time monitoring...")
    
    # Run monitoring for 2 minutes (demo)
    results = processor.start_real_time_monitoring(duration_minutes=2)
    
    print("\n✅ Real-time demo completed!")
    return results

if __name__ == "__main__":
    demo_real_time_processing()
