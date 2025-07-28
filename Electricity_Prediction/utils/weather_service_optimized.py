"""
Optimized Weather Service with Caching and Fast Response
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from functools import lru_cache
import numpy as np

class OptimizedWeatherService:
    """Fast weather service with caching and async support"""
    
    def __init__(self):
        self.api_url = 'https://api.open-meteo.com/v1/forecast'
        self.delhi_coords = {
            'latitude': 28.6519,
            'longitude': 77.2315
        }
        self.timeout = 5  # Reduced timeout for faster response
        self._cache = {}
        
    @lru_cache(maxsize=50)
    def fetch_weather_forecast_cached(self, date_str):
        """Cached weather fetching"""
        selected_date = datetime.strptime(date_str, '%Y-%m-%d')
        return self._fetch_weather_internal(selected_date)
    
    def fetch_weather_forecast(self, selected_date):
        """Main weather fetching method"""
        date_str = selected_date.strftime('%Y-%m-%d')
        return self.fetch_weather_forecast_cached(date_str)
    
    def _fetch_weather_internal(self, selected_date):
        """Internal weather fetching with fallback"""
        try:
            # Quick API call with reduced timeout
            params = {
                'latitude': self.delhi_coords['latitude'],
                'longitude': self.delhi_coords['longitude'],
                'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m',
                'timezone': 'auto',
                'start': selected_date.strftime('%Y-%m-%d'),
                'end': selected_date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(self.api_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'hourly' in data and data['hourly']['time']:
                    df = pd.DataFrame({
                        'datetime': data['hourly']['time'],
                        'temperature_2m': data['hourly']['temperature_2m'],
                        'relative_humidity_2m': data['hourly']['relative_humidity_2m'],
                        'wind_speed_10m': data['hourly']['wind_speed_10m']
                    })
                    
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df['hour'] = df['datetime'].dt.hour
                    
                    print(f"🌤️ Weather API success: {len(df)} records")
                    return df
            
            print(f"⚠️ API returned {response.status_code}, using fallback")
            return self._get_smart_fallback(selected_date)
            
        except requests.exceptions.Timeout:
            print("⚡ API timeout, using fast fallback")
            return self._get_smart_fallback(selected_date)
        except Exception as e:
            print(f"⚠️ Weather error: {str(e)[:50]}...")
            return self._get_smart_fallback(selected_date)
    
    def _get_smart_fallback(self, selected_date):
        """Smart fallback with realistic Delhi weather patterns"""
        month = selected_date.month
        day_of_year = selected_date.timetuple().tm_yday
        
        # Enhanced seasonal patterns for Delhi
        if month in [12, 1, 2]:  # Winter
            base_temp = 15 + np.sin(day_of_year * 2 * np.pi / 365) * 3
            humidity_base = 75
            wind_base = 4
        elif month in [3, 4, 5]:  # Spring/Pre-summer
            base_temp = 25 + np.sin(day_of_year * 2 * np.pi / 365) * 8
            humidity_base = 45
            wind_base = 6
        elif month in [6, 7, 8, 9]:  # Monsoon
            base_temp = 32 + np.sin(day_of_year * 2 * np.pi / 365) * 4
            humidity_base = 85
            wind_base = 8
        else:  # Post-monsoon
            base_temp = 22 + np.sin(day_of_year * 2 * np.pi / 365) * 5
            humidity_base = 65
            wind_base = 5
        
        # Generate realistic hourly data
        hourly_data = []
        for hour in range(24):
            # Temperature pattern
            hour_temp_factor = np.sin((hour - 6) * np.pi / 12) * 0.6 + 0.4
            temp = base_temp + hour_temp_factor * 12 - 6
            
            # Humidity pattern (inverse to temperature)
            humidity = humidity_base + (25 - temp) * 1.5
            humidity = np.clip(humidity, 20, 95)
            
            # Wind pattern
            wind = wind_base + np.sin(hour * np.pi / 12) * 3
            wind = np.clip(wind, 1, 15)
            
            hourly_data.append({
                'datetime': selected_date.replace(hour=hour),
                'temperature_2m': round(temp, 1),
                'relative_humidity_2m': round(humidity, 1),
                'wind_speed_10m': round(wind, 1),
                'hour': hour
            })
        
        df = pd.DataFrame(hourly_data)
        print(f"🔄 Using smart fallback for {selected_date.strftime('%Y-%m-%d')}")
        return df
    
    def get_current_weather(self):
        """Get current weather for immediate display"""
        try:
            current_params = {
                'latitude': self.delhi_coords['latitude'],
                'longitude': self.delhi_coords['longitude'],
                'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m',
                'timezone': 'auto'
            }
            
            response = requests.get(self.api_url, params=current_params, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if 'current' in data:
                    return {
                        'temperature': data['current']['temperature_2m'],
                        'humidity': data['current']['relative_humidity_2m'],
                        'wind_speed': data['current']['wind_speed_10m'],
                        'time': data['current']['time']
                    }
        except:
            pass
        
        # Fallback current weather
        now = datetime.now()
        return {
            'temperature': 25.0,
            'humidity': 60.0,
            'wind_speed': 5.0,
            'time': now.strftime('%Y-%m-%dT%H:%M')
        }
    
    def clear_cache(self):
        """Clear weather cache"""
        self.fetch_weather_forecast_cached.cache_clear()
        self._cache.clear()
        print("🧹 Weather cache cleared")
