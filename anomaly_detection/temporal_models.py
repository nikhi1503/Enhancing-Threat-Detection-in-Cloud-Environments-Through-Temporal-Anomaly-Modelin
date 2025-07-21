import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

class TemporalAnomalyDetector:
    def __init__(self, contamination=0.1, random_state=42):
        self.contamination = contamination
        self.random_state = random_state
        self.isolation_forest = IsolationForest(
            contamination=contamination, 
            random_state=random_state
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def create_temporal_features(self, data):
        """Create temporal features from timestamp"""
        data = data.copy()
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['hour'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
        
        # Rolling window features for numeric columns only
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        window_size = 5
        for col in numeric_cols:
            if col not in ['hour', 'day_of_week', 'is_weekend']:
                data[f'{col}_rolling_mean'] = data[col].rolling(window=window_size).mean()
                data[f'{col}_rolling_std'] = data[col].rolling(window=window_size).std()
        
        # Fill NaN values from rolling calculations
        data = data.bfill()
        return data
    
    def fit(self, data):
        """Fit the anomaly detection model"""
        # Create temporal features
        enhanced_data = self.create_temporal_features(data)
        
        # Select only numeric features for anomaly detection
        numeric_cols = enhanced_data.select_dtypes(include=[np.number]).columns
        feature_cols = [col for col in numeric_cols 
                       if col not in ['anomaly']]
        features = enhanced_data[feature_cols]
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Fit isolation forest
        self.isolation_forest.fit(scaled_features)
        self.is_fitted = True
        
        return self
    
    def predict(self, data):
        """Predict anomalies in the data"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
            
        # Create temporal features
        enhanced_data = self.create_temporal_features(data)
        
        # Select only numeric features for anomaly detection
        numeric_cols = enhanced_data.select_dtypes(include=[np.number]).columns
        feature_cols = [col for col in numeric_cols 
                       if col not in ['anomaly']]
        features = enhanced_data[feature_cols]
        
        # Scale features
        scaled_features = self.scaler.transform(features)
        
        # Predict anomalies
        anomaly_labels = self.isolation_forest.predict(scaled_features)
        enhanced_data['anomaly'] = anomaly_labels
        enhanced_data['anomaly_score'] = self.isolation_forest.decision_function(scaled_features)
        
        return enhanced_data
    
    def fit_predict(self, data):
        """Fit the model and predict anomalies"""
        return self.fit(data).predict(data)
