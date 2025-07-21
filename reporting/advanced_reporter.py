import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import numpy as np

class ThreatDetectionReporter:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        
    def generate_comprehensive_report(self, data, anomalies, output_dir='reports'):
        """Generate a comprehensive threat detection report"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Timeline plot of all metrics
        self._plot_timeline(data, anomalies, f'{output_dir}/timeline_analysis.png')
        
        # 2. Anomaly distribution
        self._plot_anomaly_distribution(anomalies, f'{output_dir}/anomaly_distribution.png')
        
        # 3. Feature correlation heatmap
        self._plot_correlation_heatmap(data, f'{output_dir}/feature_correlation.png')
        
        # 4. Anomaly scores distribution
        self._plot_anomaly_scores(data, f'{output_dir}/anomaly_scores.png')
        
        # 5. Generate summary statistics
        summary = self._generate_summary_stats(data, anomalies)
        
        # 6. Create HTML report
        self._create_html_report(summary, output_dir)
        
        print(f"Comprehensive report generated in '{output_dir}' directory")
        return summary
    
    def _plot_timeline(self, data, anomalies, filename):
        """Plot timeline of metrics with anomalies highlighted"""
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        metrics = ['cpu_usage', 'network_traffic', 'login_attempts']
        colors = ['red', 'blue', 'green']
        
        for i, (metric, color) in enumerate(zip(metrics, colors)):
            # Plot normal data
            axes[i].plot(data['timestamp'], data[metric], 
                        color=color, alpha=0.7, label=f'Normal {metric}')
            
            # Highlight anomalies
            if len(anomalies) > 0:
                axes[i].scatter(anomalies['timestamp'], anomalies[metric], 
                              color='red', s=50, alpha=0.8, label='Anomalies')
            
            axes[i].set_ylabel(metric.replace('_', ' ').title())
            axes[i].legend()
            axes[i].grid(True, alpha=0.3)
        
        axes[0].set_title('Cloud Environment Metrics Timeline with Detected Anomalies')
        axes[-1].set_xlabel('Timestamp')
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_anomaly_distribution(self, anomalies, filename):
        """Plot distribution of anomalies across different metrics"""
        if len(anomalies) == 0:
            print("No anomalies detected to plot distribution")
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Anomalies by hour
        anomalies['hour'] = pd.to_datetime(anomalies['timestamp']).dt.hour
        hourly_counts = anomalies['hour'].value_counts().sort_index()
        axes[0, 0].bar(hourly_counts.index, hourly_counts.values, color='coral')
        axes[0, 0].set_title('Anomalies by Hour of Day')
        axes[0, 0].set_xlabel('Hour')
        axes[0, 0].set_ylabel('Number of Anomalies')
        
        # Anomalies by day of week
        anomalies['day_of_week'] = pd.to_datetime(anomalies['timestamp']).dt.day_name()
        daily_counts = anomalies['day_of_week'].value_counts()
        axes[0, 1].bar(daily_counts.index, daily_counts.values, color='lightblue')
        axes[0, 1].set_title('Anomalies by Day of Week')
        axes[0, 1].set_xlabel('Day')
        axes[0, 1].set_ylabel('Number of Anomalies')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # CPU vs Network scatter for anomalies
        axes[1, 0].scatter(anomalies['cpu_usage'], anomalies['network_traffic'], 
                          color='red', alpha=0.6)
        axes[1, 0].set_title('Anomalous CPU vs Network Traffic')
        axes[1, 0].set_xlabel('CPU Usage')
        axes[1, 0].set_ylabel('Network Traffic')
        
        # Login attempts histogram for anomalies
        axes[1, 1].hist(anomalies['login_attempts'], bins=20, color='gold', alpha=0.7)
        axes[1, 1].set_title('Distribution of Anomalous Login Attempts')
        axes[1, 1].set_xlabel('Login Attempts')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_correlation_heatmap(self, data, filename):
        """Plot correlation heatmap of features"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        correlation_matrix = data[numeric_cols].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5)
        plt.title('Feature Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_anomaly_scores(self, data, filename):
        """Plot distribution of anomaly scores"""
        if 'anomaly_score' not in data.columns:
            print("No anomaly scores available to plot")
            return
            
        plt.figure(figsize=(12, 6))
        
        # Split data by anomaly status
        normal_scores = data[data['anomaly'] == 1]['anomaly_score']
        anomaly_scores = data[data['anomaly'] == -1]['anomaly_score']
        
        plt.hist(normal_scores, bins=30, alpha=0.7, label='Normal', color='blue')
        plt.hist(anomaly_scores, bins=30, alpha=0.7, label='Anomaly', color='red')
        
        plt.xlabel('Anomaly Score')
        plt.ylabel('Frequency')
        plt.title('Distribution of Anomaly Scores')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_summary_stats(self, data, anomalies):
        """Generate summary statistics"""
        total_points = len(data)
        total_anomalies = len(anomalies)
        anomaly_rate = (total_anomalies / total_points) * 100 if total_points > 0 else 0
        
        summary = {
            'total_data_points': total_points,
            'total_anomalies_detected': total_anomalies,
            'anomaly_rate_percentage': round(anomaly_rate, 2),
            'analysis_period': {
                'start': data['timestamp'].min(),
                'end': data['timestamp'].max()
            }
        }
        
        if len(anomalies) > 0:
            summary['anomaly_statistics'] = {
                'avg_cpu_usage': round(anomalies['cpu_usage'].mean(), 3),
                'avg_network_traffic': round(anomalies['network_traffic'].mean(), 3),
                'avg_login_attempts': round(anomalies['login_attempts'].mean(), 1),
                'max_cpu_usage': round(anomalies['cpu_usage'].max(), 3),
                'max_network_traffic': round(anomalies['network_traffic'].max(), 3),
                'max_login_attempts': int(anomalies['login_attempts'].max())
            }
        
        return summary
    
    def _create_html_report(self, summary, output_dir):
        """Create an HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Threat Detection Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ color: #2c3e50; }}
                .summary {{ background-color: #ecf0f1; padding: 20px; border-radius: 5px; }}
                .anomaly-stats {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin-top: 20px; }}
                .warning {{ background-color: #fdf2e9; padding: 15px; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <h1 class="header">Cloud Environment Threat Detection Report</h1>
            <p><strong>Generated on:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary">
                <h2>Summary Statistics</h2>
                <ul>
                    <li><strong>Total Data Points:</strong> {summary['total_data_points']}</li>
                    <li><strong>Anomalies Detected:</strong> {summary['total_anomalies_detected']}</li>
                    <li><strong>Anomaly Rate:</strong> {summary['anomaly_rate_percentage']}%</li>
                    <li><strong>Analysis Period:</strong> {summary['analysis_period']['start']} to {summary['analysis_period']['end']}</li>
                </ul>
            </div>
            
            {'<div class="anomaly-stats"><h2>Anomaly Statistics</h2><ul>' + 
             ''.join([f'<li><strong>{k.replace("_", " ").title()}:</strong> {v}</li>' 
                     for k, v in summary.get("anomaly_statistics", {}).items()]) + 
             '</ul></div>' if summary.get("anomaly_statistics") else ''}
            
            <div class="warning">
                <h2>Recommendations</h2>
                <ul>
                    <li>Monitor high CPU usage patterns that may indicate resource exhaustion attacks</li>
                    <li>Watch for unusual spikes in network traffic suggesting DDoS attacks</li>
                    <li>Alert on excessive login attempts indicating brute force attacks</li>
                    <li>Implement automated response systems for detected anomalies</li>
                </ul>
            </div>
            
            <h2>Generated Visualizations</h2>
            <ul>
                <li>Timeline Analysis: timeline_analysis.png</li>
                <li>Anomaly Distribution: anomaly_distribution.png</li>
                <li>Feature Correlation: feature_correlation.png</li>
                <li>Anomaly Scores: anomaly_scores.png</li>
            </ul>
        </body>
        </html>
        """
        
        with open(f'{output_dir}/threat_detection_report.html', 'w') as f:
            f.write(html_content)
