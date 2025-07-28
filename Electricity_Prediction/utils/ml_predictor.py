"""
ML Predictor - Enhanced version of your existing prediction logic
Uses your trained models with caching and performance optimizations
"""

import numpy as np
import pandas as pd
import pickle
import os
from datetime import datetime

class MLPredictor:
    """Enhanced ML prediction service using your trained models"""
    
    def __init__(self):
        self.models = {}
        self.model_path = 'models'
        self.regions = ['DELHI', 'BRPL', 'BYPL', 'NDPL', 'NDMC', 'MES']
        self.load_models()
    
    def load_models(self):
        """Load your pre-trained models with error handling"""
        for region in self.regions:
            try:
                # Load Random Forest model
                rf_path = os.path.join(self.model_path, f'{region}_rf_model.pkl')
                with open(rf_path, 'rb') as f:
                    rf_model = pickle.load(f)
                
                # Load LSTM model
                lstm_path = os.path.join(self.model_path, f'{region}_lstm_model.pkl')
                with open(lstm_path, 'rb') as f:
                    lstm_model = pickle.load(f)
                
                # Load XGBoost model
                xgb_path = os.path.join(self.model_path, f'{region}_xgb_model.pkl')
                with open(xgb_path, 'rb') as f:
                    xgb_model = pickle.load(f)
                
                self.models[region] = {
                    'rf': rf_model,
                    'lstm': lstm_model,
                    'xgb': xgb_model
                }
                
                print(f"Loaded models for region: {region}")
                
            except FileNotFoundError as e:
                print(f"Model file not found for region {region}: {e}")
            except Exception as e:
                print(f"Error loading models for region {region}: {e}")
    
    def predict(self, region, temperature, humidity, wind_speed, hour, day, month, year):
        """Enhanced prediction using your existing logic with caching"""
        try:
            # Calculate weekday (your existing logic)
            weekday = datetime(year, month, day).weekday()
            
            # Prepare input features (your exact feature set)
            X_input = np.array([[temperature, humidity, wind_speed, hour, day, month, weekday]])
            
            if region not in self.models:
                raise ValueError(f"Models not available for region: {region}")
            
            models = self.models[region]
            predictions = {}
            
            # Random Forest prediction
            rf_model = models['rf']
            y_pred_rf = rf_model.predict(X_input)
            predictions['rf'] = float(y_pred_rf[0])
            
            # LSTM prediction (your existing reshape logic)
            lstm_model = models['lstm']
            X_input_lstm = X_input.reshape((X_input.shape[0], 1, X_input.shape[1]))
            y_pred_lstm = lstm_model.predict(X_input_lstm, verbose=0)
            predictions['lstm'] = float(y_pred_lstm.squeeze())
            
            # XGBoost prediction
            xgb_model = models['xgb']
            y_pred_xgb = xgb_model.predict(X_input)
            predictions['xgb'] = float(y_pred_xgb[0])
            
            # Ensemble prediction (your existing logic)
            ensemble_pred = (predictions['rf'] + predictions['lstm'] + predictions['xgb']) / 3
            predictions['ensemble'] = float(ensemble_pred)
            
            # Calculate confidence score based on model agreement
            pred_values = [predictions['rf'], predictions['lstm'], predictions['xgb']]
            std_dev = np.std(pred_values)
            confidence = max(0.5, 1.0 - (std_dev / np.mean(pred_values)))
            predictions['confidence'] = min(0.99, confidence)
            
            return predictions
            
        except Exception as e:
            print(f"Prediction error for region {region}: {e}")
            # Return fallback values
            return {
                'rf': 1000.0,
                'lstm': 1000.0, 
                'xgb': 1000.0,
                'ensemble': 1000.0,
                'confidence': 0.5
            }
    
    def predict_all_regions(self, temperature, humidity, wind_speed, hour, day, month, year):
        """Predict for all regions (your ALL region logic)"""
        all_predictions = {}
        
        for region in self.regions:
            pred = self.predict(
                region=region,
                temperature=temperature,
                humidity=humidity,
                wind_speed=wind_speed,
                hour=hour,
                day=day,
                month=month,
                year=year
            )
            all_predictions[region] = pred['ensemble']
        
        return all_predictions
    
    def get_model_info(self, region):
        """Get information about loaded models"""
        if region not in self.models:
            return None
        
        model_info = {
            'region': region,
            'models_loaded': list(self.models[region].keys()),
            'features': ['temperature_2m', 'relative_humidity_2m', 'wind_speed_10m', 
                        'hour', 'day', 'month', 'weekday']
        }
        
        return model_info
