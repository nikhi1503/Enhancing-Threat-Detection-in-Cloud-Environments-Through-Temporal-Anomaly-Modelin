import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class CloudEnvironmentSimulator:
    def __init__(self):
        self.base_cpu = 0.3
        self.base_network = 0.2
        self.base_logins = 2
        
    def generate_normal_traffic(self, start_date, end_date, freq='H'):
        """Generate normal cloud environment data"""
        timestamps = pd.date_range(start=start_date, end=end_date, freq=freq)
        n_points = len(timestamps)
        
        # Normal patterns with daily cycles
        hours = np.array([ts.hour for ts in timestamps])
        
        # CPU usage with daily pattern (higher during business hours)
        cpu_pattern = 0.3 + 0.2 * np.sin(2 * np.pi * hours / 24)
        cpu_noise = np.random.normal(0, 0.05, n_points)
        cpu_usage = np.clip(cpu_pattern + cpu_noise, 0, 1)
        
        # Network traffic with business hours pattern
        network_pattern = 0.2 + 0.3 * np.sin(2 * np.pi * (hours - 6) / 24)
        network_noise = np.random.normal(0, 0.08, n_points)
        network_traffic = np.clip(network_pattern + network_noise, 0, 1)
        
        # Login attempts (higher during business hours)
        login_pattern = 2 + 3 * np.maximum(0, np.sin(2 * np.pi * (hours - 8) / 12))
        login_noise = np.random.poisson(1, n_points)
        login_attempts = np.maximum(0, login_pattern + login_noise)
        
        return pd.DataFrame({
            'timestamp': timestamps,
            'cpu_usage': cpu_usage,
            'network_traffic': network_traffic,
            'login_attempts': login_attempts
        })
    
    def inject_ddos_attack(self, data, attack_start_idx, duration_hours=2):
        """Inject DDoS attack pattern"""
        data = data.copy()
        attack_end_idx = min(attack_start_idx + duration_hours, len(data))
        
        # Increase network traffic and CPU usage during attack
        data.loc[attack_start_idx:attack_end_idx, 'network_traffic'] *= 5
        data.loc[attack_start_idx:attack_end_idx, 'cpu_usage'] *= 1.8
        
        # Clip to valid ranges
        data['network_traffic'] = np.clip(data['network_traffic'], 0, 1)
        data['cpu_usage'] = np.clip(data['cpu_usage'], 0, 1)
        
        return data
    
    def inject_brute_force_attack(self, data, attack_start_idx, duration_hours=1):
        """Inject brute force login attack"""
        data = data.copy()
        attack_end_idx = min(attack_start_idx + duration_hours, len(data))
        
        # Dramatically increase login attempts
        data.loc[attack_start_idx:attack_end_idx, 'login_attempts'] += 50
        
        return data
    
    def inject_resource_exhaustion(self, data, attack_start_idx, duration_hours=3):
        """Inject resource exhaustion attack"""
        data = data.copy()
        attack_end_idx = min(attack_start_idx + duration_hours, len(data))
        
        # Gradually increase CPU usage to near maximum
        for i in range(attack_start_idx, attack_end_idx):
            progress = (i - attack_start_idx) / (attack_end_idx - attack_start_idx)
            data.loc[i, 'cpu_usage'] = min(0.95, data.loc[i, 'cpu_usage'] + 0.6 * progress)
        
        return data
    
    def generate_attack_scenario(self, days=7):
        """Generate a complete attack scenario"""
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        
        # Generate normal data
        data = self.generate_normal_traffic(start_date, end_date)
        
        # Inject various attacks
        total_hours = len(data)
        
        # DDoS attack at 25% through the timeline
        ddos_start = int(total_hours * 0.25)
        data = self.inject_ddos_attack(data, ddos_start)
        
        # Brute force attack at 60% through the timeline
        brute_force_start = int(total_hours * 0.6)
        data = self.inject_brute_force_attack(data, brute_force_start)
        
        # Resource exhaustion at 80% through the timeline
        resource_start = int(total_hours * 0.8)
        data = self.inject_resource_exhaustion(data, resource_start)
        
        return data
