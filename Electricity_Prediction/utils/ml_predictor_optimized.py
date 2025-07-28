"""
Optimized ML Predictor with Lazy Loading and Caching
Loads models only when needed and caches predictions
"""

import pickle
import pandas as pd
import numpy as np
import os
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

class OptimizedMLPredictor:
    """Optimized ML predictor with lazy loading and caching"""
    
    def __init__(self):
        self.regions = ['DELHI', 'BRPL', 'BYPL', 'NDPL', 'NDMC', 'MES']
        self.model_types = ['rf', 'lstm', 'xgb']
        self.models = {}  # Lazy loading - models loaded only when needed
        self.model_dir = 'models'
        
        # Cache for predictions
        self._prediction_cache = {}
        
    def _load_model_if_needed(self, region, model_type):
        """Load model only when first requested"""
        model_key = f"{region}_{model_type}"
        
        if model_key not in self.models:
            model_path = os.path.join(self.model_dir, f"{region}_{model_type}_model.pkl")
            
            if os.path.exists(model_path):
                try:
                    with open(model_path, 'rb') as f:
                        self.models[model_key] = pickle.load(f)
                    print(f"🚀 Loaded {model_key} model")
                except Exception as e:
                    print(f"❌ Error loading {model_key}: {e}")
                    self.models[model_key] = None
            else:
                print(f"⚠️ Model file not found: {model_path}")
                self.models[model_key] = None
        
        return self.models.get(model_key)
    
    @lru_cache(maxsize=100)
    def predict_demand_cached(self, region, temperature, humidity, wind_speed, hour, cache_key):
        """Cached prediction to avoid repeated calculations"""
        return self._predict_demand_internal(region, temperature, humidity, wind_speed, hour)
    
    def _predict_demand_internal(self, region, temperature, humidity, wind_speed, hour):
        """Internal prediction method"""
        try:
            # Prepare input features
            features = np.array([[temperature, humidity, wind_speed, hour]])
            predictions = []
            model_names = []
            
            # Get predictions from available models
            for model_type in self.model_types:
                model = self._load_model_if_needed(region, model_type)
                if model is not None:
                    try:
                        if model_type == 'lstm':
                            # LSTM expects 3D input
                            lstm_features = features.reshape(1, 1, -1)
                            pred = model.predict(lstm_features, verbose=0)[0][0]
                        else:
                            pred = model.predict(features)[0]
                        
                        predictions.append(max(0, pred))  # Ensure non-negative
                        model_names.append(model_type.upper())
                    except Exception as e:
                        print(f"⚠️ Error predicting with {model_type}: {e}")
            
            if predictions:
                # Ensemble prediction (weighted average)
                weights = [0.4, 0.3, 0.3][:len(predictions)]  # RF, LSTM, XGB
                ensemble_pred = np.average(predictions, weights=weights)
                
                # Calculate confidence based on prediction variance
                if len(predictions) > 1:
                    variance = np.var(predictions)
                    confidence = max(0.6, min(0.95, 1.0 - (variance / (ensemble_pred + 1))))
                else:
                    confidence = 0.8
                
                return {
                    'prediction': round(ensemble_pred, 2),
                    'confidence': round(confidence * 100, 1),
                    'models_used': model_names,
                    'individual_predictions': {name: round(pred, 2) for name, pred in zip(model_names, predictions)}
                }
            else:
                # Fallback prediction based on historical patterns
                base_demand = self._get_historical_demand(region, hour)
                return {
                    'prediction': base_demand,
                    'confidence': 60.0,
                    'models_used': ['HISTORICAL'],
                    'individual_predictions': {'HISTORICAL': base_demand}
                }
                
        except Exception as e:
            print(f"❌ Error in prediction: {e}")
            return {
                'prediction': 1000.0,
                'confidence': 50.0,
                'models_used': ['FALLBACK'],
                'individual_predictions': {'FALLBACK': 1000.0}
            }
    
    def predict_demand(self, region, temperature, humidity, wind_speed, hour):
        """Main prediction method with caching"""
        # Create cache key
        cache_key = f"{region}_{temperature}_{humidity}_{wind_speed}_{hour}"
        
        return self.predict_demand_cached(region, temperature, humidity, wind_speed, hour, cache_key)
    
    def _get_historical_demand(self, region, hour):
        """Get historical demand patterns for fallback"""
        # Simplified historical patterns based on hour and region
        base_demands = {
            'DELHI': 2500,
            'BRPL': 800,
            'BYPL': 600,
            'NDPL': 700,
            'NDMC': 400,
            'MES': 300
        }
        
        base = base_demands.get(region, 1000)
        
        # Hour-based adjustment
        if 6 <= hour <= 10:  # Morning peak
            multiplier = 1.3
        elif 18 <= hour <= 22:  # Evening peak
            multiplier = 1.4
        elif 0 <= hour <= 5:  # Night low
            multiplier = 0.7
        else:  # Day time
            multiplier = 1.1
        
        return round(base * multiplier, 2)
    
    def get_regions(self):
        """Get available regions"""
        return self.regions
    
    def clear_cache(self):
        """Clear prediction cache"""
        self.predict_demand_cached.cache_clear()
        self._prediction_cache.clear()
        print("🧹 Cache cleared")
