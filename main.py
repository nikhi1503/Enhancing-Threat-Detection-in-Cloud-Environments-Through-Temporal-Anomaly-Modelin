# Main entry point for the threat detection pipeline
from data_ingestion.ingest import load_data
from preprocessing.clean import preprocess_data
from anomaly_detection.model import detect_anomalies
from reporting.report import generate_report

if __name__ == "__main__":
    # Step 1: Load data
    data = load_data()
    # Step 2: Preprocess data
    processed_data = preprocess_data(data)
    # Step 3: Detect anomalies
    anomalies = detect_anomalies(processed_data)
    # Step 4: Generate report
    generate_report(anomalies)
