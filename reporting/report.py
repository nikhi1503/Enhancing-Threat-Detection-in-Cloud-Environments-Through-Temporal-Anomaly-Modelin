import matplotlib.pyplot as plt

def generate_report(anomalies):
    # Simple report: plot anomalies over time
    plt.figure(figsize=(10, 5))
    plt.plot(anomalies['timestamp'], anomalies['cpu_usage'], 'ro', label='CPU Anomaly')
    plt.plot(anomalies['timestamp'], anomalies['network_traffic'], 'bo', label='Network Anomaly')
    plt.xlabel('Timestamp')
    plt.ylabel('Normalized Value')
    plt.title('Detected Anomalies in Cloud Environment')
    plt.legend()
    plt.tight_layout()
    plt.savefig('anomaly_report.png')
    print('Report generated: anomaly_report.png')
