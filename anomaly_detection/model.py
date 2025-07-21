from sklearn.ensemble import IsolationForest

def detect_anomalies(data):
    # Use Isolation Forest for anomaly detection
    model = IsolationForest(contamination=0.1, random_state=42)
    features = data[['cpu_usage', 'network_traffic', 'login_attempts']]
    data['anomaly'] = model.fit_predict(features)
    anomalies = data[data['anomaly'] == -1]
    return anomalies
