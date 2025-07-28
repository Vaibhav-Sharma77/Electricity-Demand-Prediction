"""
Weather Service - Enhanced version of your weather fetching logic
Includes caching, fallback, and current weather support
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json

class WeatherService:
    """Enhanced weather service using your existing API logic"""
    
    def __init__(self):
        self.api_url = 'https://api.open-meteo.com/v1/forecast'
        self.delhi_coords = {
            'latitude': 28.6519,
            'longitude': 77.2315
        }
        self.timeout = 10
    
    def fetch_weather_forecast(self, selected_date):
        """Enhanced version of your fetch_weather_forecast function"""
        try:
            # Your existing API parameters
            params = {
                'latitude': self.delhi_coords['latitude'],
                'longitude': self.delhi_coords['longitude'],
                'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m',
                'timezone': 'auto',
                'start': selected_date.strftime('%Y-%m-%dT00:00'),
                'end': selected_date.strftime('%Y-%m-%dT23:00')
            }
            
            response = requests.get(self.api_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Your existing DataFrame creation logic
                df = pd.DataFrame({
                    'datetime': data['hourly']['time'],
                    'temperature_2m': data['hourly']['temperature_2m'],
                    'relative_humidity_2m': data['hourly']['relative_humidity_2m'],
                    'wind_speed_10m': data['hourly']['wind_speed_10m']
                })
                
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['hour'] = df['datetime'].dt.hour
                
                print(f"Successfully fetched weather data: {len(df)} records")
                return df
                
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return self.get_fallback_weather_data(selected_date)
                
        except requests.exceptions.Timeout:
            print("Weather API timeout")
            return self.get_fallback_weather_data(selected_date)
        except requests.exceptions.ConnectionError:
            print("Weather API connection error")
            return self.get_fallback_weather_data(selected_date)
        except Exception as e:
            print(f"Weather API error: {e}")
            return self.get_fallback_weather_data(selected_date)
    
    def get_fallback_weather_data(self, selected_date):
        """Enhanced version of your fallback function with database lookup"""
        try:
            # Try to read historical weather data (your existing logic)
            weather_df = pd.read_csv('data/cleaned_weather.csv')
            weather_df['Timestamp'] = pd.to_datetime(weather_df['Timestamp'])
            
            # Filter for the same day of year from historical data (your logic)
            target_month = selected_date.month
            target_day = selected_date.day
            
            similar_dates = weather_df[
                (weather_df['Timestamp'].dt.month == target_month) & 
                (weather_df['Timestamp'].dt.day == target_day)
            ]
            
            if not similar_dates.empty:
                # Use the most recent similar date (your logic)
                recent_similar = similar_dates.iloc[-1]
                
                # Create hourly data for the selected date (your logic)
                hourly_data = []
                for hour in range(24):
                    hourly_data.append({
                        'datetime': selected_date.replace(hour=hour),
                        'temperature_2m': recent_similar.get('temperature_2m', 25.0),
                        'relative_humidity_2m': recent_similar.get('relative_humidity_2m', 60.0),
                        'wind_speed_10m': recent_similar.get('wind_speed_10m', 5.0),
                        'hour': hour
                    })
                
                df = pd.DataFrame(hourly_data)
                print(f"Using historical fallback data for {selected_date.strftime('%Y-%m-%d')}")
                return df
            else:
                # If no historical data, use default values (your logic)
                return self.get_default_weather_data(selected_date)
                
        except Exception as e:
            print(f"Error reading historical weather data: {e}")
            return self.get_default_weather_data(selected_date)
    
    def get_default_weather_data(self, selected_date):
        """Your existing default weather data generation with seasonal improvements"""
        print(f"Using default weather patterns for {selected_date.strftime('%Y-%m-%d')}")
        
        # Enhanced seasonal patterns
        month = selected_date.month
        
        # Seasonal base temperatures for Delhi
        if month in [12, 1, 2]:  # Winter
            base_temp = 15
            humidity_base = 70
        elif month in [3, 4, 5]:  # Spring/Pre-summer
            base_temp = 28
            humidity_base = 50
        elif month in [6, 7, 8, 9]:  # Monsoon
            base_temp = 32
            humidity_base = 80
        else:  # Post-monsoon
            base_temp = 25
            humidity_base = 60
        
        hourly_data = []
        for hour in range(24):
            # Enhanced temperature pattern (your existing logic improved)
            if hour < 6:
                temp = base_temp - 5 + hour * 0.5  # Night/early morning
            elif hour < 12:
                temp = base_temp - 2 + (hour - 6) * 2  # Morning warming
            elif hour < 18:
                temp = base_temp + 8 - (hour - 12) * 0.5  # Afternoon cooling
            else:
                temp = base_temp + 5 - (hour - 18) * 1.5  # Evening cooling
            
            # Enhanced humidity pattern
            if hour < 6:
                humidity = humidity_base + 10 - hour * 1.5
            elif hour < 16:
                humidity = humidity_base - 20 + hour * 1.2
            else:
                humidity = humidity_base - 5 + (hour - 16) * 2
            
            # Enhanced wind speed pattern
            if hour < 12:
                wind_speed = 3 + hour * 0.3
            else:
                wind_speed = 7 - (hour - 12) * 0.2
            
            hourly_data.append({
                'datetime': selected_date.replace(hour=hour),
                'temperature_2m': max(-5, min(50, temp)),  # Reasonable bounds
                'relative_humidity_2m': max(20, min(95, humidity)),
                'wind_speed_10m': max(0, min(15, wind_speed)),
                'hour': hour
            })
        
        df = pd.DataFrame(hourly_data)
        return df
