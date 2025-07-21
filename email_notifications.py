"""
Enhanced Email Notification System for Threat Detection
Sends HTML email alerts when threats are detected in cloud environments
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ThreatAlertEmailer:
    def __init__(self):
        """Initialize email configuration"""
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Get email configuration from environment
        self.sender_email = os.getenv('SENDER_EMAIL', 'nikhil19151915@gmail.com')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.alert_email = os.getenv('ALERT_EMAIL', 'girishgowda5539@gmail.com')
        
    def send_threat_alert(self, total_data_points, anomalies_detected, anomaly_rate, analysis_period, summary_stats=None):
        """Send email alert for general threat detection"""
        if not self.sender_email or not self.sender_password:
            print("Email configuration missing!")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.alert_email
            msg['Subject'] = f"THREAT ALERT: {anomalies_detected} Anomalies Detected ({anomaly_rate:.1f}% rate)"
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ padding: 20px; }}
        .alert-box {{ background: #fff5f5; border-left: 4px solid #e74c3c; padding: 15px; margin: 20px 0; }}
        .metric {{ margin: 10px 0; padding: 8px; background: #ecf0f1; border-radius: 5px; }}
        .critical {{ color: #e74c3c; font-weight: bold; }}
        .footer {{ text-align: center; padding: 20px; color: #7f8c8d; border-top: 1px solid #ecf0f1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>THREAT DETECTION ALERT</h1>
            <h2>Multiple Anomalies Detected</h2>
        </div>
        
        <div class="content">
            <div class="alert-box">
                <h3>THREAT SUMMARY</h3>
                <p><strong>Anomalies Detected:</strong> <span class="critical">{anomalies_detected}</span></p>
                <p><strong>Detection Rate:</strong> <span class="critical">{anomaly_rate:.1f}%</span></p>
                <p><strong>Analysis Period:</strong> {analysis_period}</p>
            </div>
            
            <div class="metric">
                <strong>Total Data Points Analyzed:</strong> {total_data_points}
            </div>
            
            <div class="alert-box">
                <h3>Recommended Actions</h3>
                <ul>
                    <li>Review system logs immediately</li>
                    <li>Check for unauthorized access attempts</li>
                    <li>Monitor network traffic patterns</li>
                    <li>Verify system resource usage</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated alert from your Cloud Threat Detection System.</p>
            <p>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
            print(f"Threat alert email sent to {self.alert_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send threat alert: {e}")
            return False

    def send_test_email(self):
        """Send a test email to verify configuration"""
        if not self.sender_email or not self.sender_password:
            print("Email configuration missing!")
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Test: Threat Detection System"
            message["From"] = self.sender_email
            message["To"] = self.alert_email
            
            test_html = f"""
            <html>
            <body>
                <h2>Email Notification Test</h2>
                <p>This is a test email from your threat detection system.</p>
                <p><strong>Timestamp:</strong> {datetime.now()}</p>
                <p><strong>Alert Email:</strong> {self.alert_email}</p>
                <p><strong>Status:</strong> Email system is working correctly!</p>
            </body>
            </html>
            """
            
            html_part = MIMEText(test_html, "html")
            message.attach(html_part)
            
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email, 
                    self.alert_email, 
                    message.as_string()
                )
            
            print(f"Test email sent successfully to {self.alert_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send test email: {e}")
            return False

    def send_ddos_alert(self, max_network_traffic, max_cpu_usage, attack_duration, timestamp):
        """Send DDoS attack specific alert"""
        if not self.sender_email or not self.sender_password:
            print("Email configuration missing!")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.alert_email
            msg['Subject'] = f"🚨 CRITICAL: DDoS Attack Detected - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #dc3545; margin: 0;">🚨 DDoS ATTACK DETECTED</h1>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">Critical Security Alert</p>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                        <h2 style="color: #856404; margin: 0 0 15px 0;">Attack Details</h2>
                        <p><strong>Attack Type:</strong> Distributed Denial of Service (DDoS)</p>
                        <p><strong>Detection Time:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>Max Network Traffic:</strong> {max_network_traffic:.2%}</p>
                        <p><strong>Max CPU Usage:</strong> {max_cpu_usage:.2%}</p>
                        <p><strong>Attack Duration:</strong> {attack_duration} data points</p>
                    </div>
                    
                    <div style="background: #f8d7da; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545; margin-bottom: 20px;">
                        <h3 style="color: #721c24; margin: 0 0 15px 0;">Immediate Actions Required</h3>
                        <ul style="color: #721c24; margin: 0; padding-left: 20px;">
                            <li>Enable DDoS protection services</li>
                            <li>Increase server capacity</li>
                            <li>Block suspicious IP addresses</li>
                            <li>Monitor network traffic patterns</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                        <p>This is an automated alert from your Cloud Threat Detection System.</p>
                        <p>Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"DDoS alert email sent to {self.alert_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send DDoS alert: {e}")
            return False

    def send_brute_force_alert(self, max_login_attempts, avg_login_attempts, attack_duration, timestamp):
        """Send brute force attack specific alert"""
        if not self.sender_email or not self.sender_password:
            print("Email configuration missing!")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.alert_email
            msg['Subject'] = f"🔐 HIGH: Brute Force Attack Detected - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #fd7e14; margin: 0;">🔐 BRUTE FORCE ATTACK DETECTED</h1>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">High Priority Security Alert</p>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                        <h2 style="color: #856404; margin: 0 0 15px 0;">Attack Details</h2>
                        <p><strong>Attack Type:</strong> Brute Force Authentication Attack</p>
                        <p><strong>Detection Time:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>Max Login Attempts:</strong> {max_login_attempts:.0f} attempts</p>
                        <p><strong>Average Login Attempts:</strong> {avg_login_attempts:.1f} attempts</p>
                        <p><strong>Attack Duration:</strong> {attack_duration} data points</p>
                    </div>
                    
                    <div style="background: #f8d7da; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545; margin-bottom: 20px;">
                        <h3 style="color: #721c24; margin: 0 0 15px 0;">Immediate Actions Required</h3>
                        <ul style="color: #721c24; margin: 0; padding-left: 20px;">
                            <li>Enable account lockout policies</li>
                            <li>Implement CAPTCHA verification</li>
                            <li>Review authentication logs</li>
                            <li>Block suspicious IP addresses</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                        <p>This is an automated alert from your Cloud Threat Detection System.</p>
                        <p>Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"Brute force alert email sent to {self.alert_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send brute force alert: {e}")
            return False

    def send_resource_exhaustion_alert(self, max_cpu_usage, cpu_trend, duration, timestamp):
        """Send resource exhaustion specific alert"""
        if not self.sender_email or not self.sender_password:
            print("Email configuration missing!")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.alert_email
            msg['Subject'] = f"💻 MEDIUM: Resource Exhaustion Detected - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #17a2b8; margin: 0;">💻 RESOURCE EXHAUSTION DETECTED</h1>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">Medium Priority System Alert</p>
                    </div>
                    
                    <div style="background: #d1ecf1; padding: 20px; border-radius: 8px; border-left: 4px solid #17a2b8; margin-bottom: 20px;">
                        <h2 style="color: #0c5460; margin: 0 0 15px 0;">Resource Details</h2>
                        <p><strong>Issue Type:</strong> Resource Exhaustion Attack</p>
                        <p><strong>Detection Time:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>Max CPU Usage:</strong> {max_cpu_usage:.2%}</p>
                        <p><strong>CPU Trend:</strong> {cpu_trend:+.3f} (increase)</p>
                        <p><strong>Duration:</strong> {duration} data points</p>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                        <h3 style="color: #856404; margin: 0 0 15px 0;">Recommended Actions</h3>
                        <ul style="color: #856404; margin: 0; padding-left: 20px;">
                            <li>Monitor system resource usage</li>
                            <li>Scale up server resources</li>
                            <li>Identify resource-intensive processes</li>
                            <li>Implement resource limits</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                        <p>This is an automated alert from your Cloud Threat Detection System.</p>
                        <p>Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"Resource exhaustion alert email sent to {self.alert_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send resource exhaustion alert: {e}")
            return False

    def send_temporal_anomaly_alert(self, off_hours_count, weekend_count, total_anomalies, timestamp):
        """Send temporal anomaly specific alert"""
        if not self.sender_email or not self.sender_password:
            print("Email configuration missing!")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.alert_email
            msg['Subject'] = f"⏰ LOW: Temporal Anomaly Detected - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #6c757d; margin: 0;">⏰ TEMPORAL ANOMALY DETECTED</h1>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">Low Priority Time-based Alert</p>
                    </div>
                    
                    <div style="background: #e2e3e5; padding: 20px; border-radius: 8px; border-left: 4px solid #6c757d; margin-bottom: 20px;">
                        <h2 style="color: #495057; margin: 0 0 15px 0;">Temporal Pattern Details</h2>
                        <p><strong>Anomaly Type:</strong> Unusual Time-based Activity</p>
                        <p><strong>Detection Time:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>Off-Hours Activities:</strong> {off_hours_count} events</p>
                        <p><strong>Weekend Activities:</strong> {weekend_count} events</p>
                        <p><strong>Total Anomalies:</strong> {total_anomalies} events</p>
                    </div>
                    
                    <div style="background: #d1ecf1; padding: 20px; border-radius: 8px; border-left: 4px solid #17a2b8; margin-bottom: 20px;">
                        <h3 style="color: #0c5460; margin: 0 0 15px 0;">Review Actions</h3>
                        <ul style="color: #0c5460; margin: 0; padding-left: 20px;">
                            <li>Review off-hours system access</li>
                            <li>Check for scheduled maintenance</li>
                            <li>Verify authorized personnel activity</li>
                            <li>Monitor for pattern changes</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                        <p>This is an automated alert from your Cloud Threat Detection System.</p>
                        <p>Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"Temporal anomaly alert email sent to {self.alert_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send temporal anomaly alert: {e}")
            return False

    def send_ml_anomaly_alert(self, avg_anomaly_score, min_anomaly_score, max_anomaly_score, total_anomalies, timestamp):
        """Send ML anomaly specific alert"""
        if not self.sender_email or not self.sender_password:
            print("Email configuration missing!")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.alert_email
            msg['Subject'] = f"🤖 MEDIUM: ML Anomaly Detected - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #6f42c1; margin: 0;">🤖 MACHINE LEARNING ANOMALY DETECTED</h1>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">Medium Priority ML-based Alert</p>
                    </div>
                    
                    <div style="background: #e2e3f3; padding: 20px; border-radius: 8px; border-left: 4px solid #6f42c1; margin-bottom: 20px;">
                        <h2 style="color: #493971; margin: 0 0 15px 0;">ML Analysis Results</h2>
                        <p><strong>Detection Method:</strong> Multi-dimensional Machine Learning</p>
                        <p><strong>Detection Time:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>Average Anomaly Score:</strong> {avg_anomaly_score:.4f}</p>
                        <p><strong>Min Anomaly Score:</strong> {min_anomaly_score:.4f}</p>
                        <p><strong>Max Anomaly Score:</strong> {max_anomaly_score:.4f}</p>
                        <p><strong>Total Anomalies:</strong> {total_anomalies} events</p>
                    </div>
                    
                    <div style="background: #d1ecf1; padding: 20px; border-radius: 8px; border-left: 4px solid #17a2b8; margin-bottom: 20px;">
                        <h3 style="color: #0c5460; margin: 0 0 15px 0;">Analysis Actions</h3>
                        <ul style="color: #0c5460; margin: 0; padding-left: 20px;">
                            <li>Review multi-dimensional patterns</li>
                            <li>Analyze feature correlations</li>
                            <li>Check for complex attack vectors</li>
                            <li>Validate ML model predictions</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                        <p>This is an automated alert from your Cloud Threat Detection System.</p>
                        <p>Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"ML anomaly alert email sent to {self.alert_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send ML anomaly alert: {e}")
            return False

if __name__ == "__main__":
    print("Testing Email Notification System")
    print("=" * 50)
    
    emailer = ThreatAlertEmailer()
    
    print(f"Configured to send alerts to: {emailer.alert_email}")
    print(f"Sender email: {emailer.sender_email}")
    
    success = emailer.send_test_email()
    
    if success:
        print("Email notification system is working!")
    else:
        print("Email setup needs configuration.")
