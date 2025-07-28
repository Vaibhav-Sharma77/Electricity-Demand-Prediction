"""
PowerPulse Enhanced - Optimized Flask Application
Fast loading, beautiful UI, and optimized performance
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import json
import os
from utils.weather_service_optimized import OptimizedWeatherService
from utils.ml_predictor_optimized import OptimizedMLPredictor

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'powerpulse-enhanced-2025'

# Global instances with lazy loading
weather_service = None
ml_predictor = None

def get_weather_service():
    """Lazy loading of weather service"""
    global weather_service
    if weather_service is None:
        weather_service = OptimizedWeatherService()
    return weather_service

def get_ml_predictor():
    """Lazy loading of ML predictor"""
    global ml_predictor
    if ml_predictor is None:
        ml_predictor = OptimizedMLPredictor()
    return ml_predictor

@app.route('/')
def index():
    """Homepage with current weather"""
    try:
        current_weather = get_weather_service().get_current_weather()
        regions = get_ml_predictor().get_regions()
        today = datetime.now().strftime('%Y-%m-%d')
        
        return render_template('index_optimized.html', 
                             current_weather=current_weather,
                             regions=regions,
                             today=today)
    except Exception as e:
        print(f"❌ Error in index: {e}")
        today = datetime.now().strftime('%Y-%m-%d')
        return render_template('index_optimized.html', 
                             current_weather=None,
                             regions=['DELHI', 'BRPL', 'BYPL', 'NDPL', 'NDMC', 'MES'],
                             today=today)

@app.route('/api/forecast', methods=['POST'])
def api_forecast():
    """Fast API endpoint for predictions"""
    try:
        data = request.get_json()
        
        # Extract parameters
        region = data.get('region', 'DELHI')
        forecast_date = datetime.strptime(data.get('date'), '%Y-%m-%d')
        
        # Get weather data
        print(f"🔍 Fetching weather for {forecast_date.strftime('%Y-%m-%d')}")
        weather_df = get_weather_service().fetch_weather_forecast(forecast_date)
        
        if weather_df is None or weather_df.empty:
            return jsonify({'error': 'Failed to fetch weather data'}), 500
        
        # Generate predictions for each hour
        predictions = []
        for _, row in weather_df.iterrows():
            pred_result = get_ml_predictor().predict_demand(
                region=region,
                temperature=row['temperature_2m'],
                humidity=row['relative_humidity_2m'],
                wind_speed=row['wind_speed_10m'],
                hour=row['hour']
            )
            
            predictions.append({
                'hour': int(row['hour']),
                'temperature': round(row['temperature_2m'], 1),
                'humidity': round(row['relative_humidity_2m'], 1),
                'wind_speed': round(row['wind_speed_10m'], 1),
                'demand': pred_result['prediction'],
                'confidence': pred_result['confidence']
            })
        
        # Calculate summary statistics
        demands = [p['demand'] for p in predictions]
        peak_hour = predictions[np.argmax(demands)]['hour']
        total_demand = sum(demands)
        avg_confidence = np.mean([p['confidence'] for p in predictions])
        
        return jsonify({
            'success': True,
            'region': region,
            'date': forecast_date.strftime('%Y-%m-%d'),
            'predictions': predictions,
            'summary': {
                'peak_demand': max(demands),
                'peak_hour': peak_hour,
                'total_daily_demand': round(total_demand, 2),
                'average_demand': round(np.mean(demands), 2),
                'average_confidence': round(avg_confidence, 1)
            }
        })
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/forecast')
def forecast():
    """Forecast page"""
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('forecast_optimized.html', today=today)

@app.route('/api/chart/<region>/<date>')
def api_chart(region, date):
    """Generate optimized chart"""
    try:
        forecast_date = datetime.strptime(date, '%Y-%m-%d')
        weather_df = get_weather_service().fetch_weather_forecast(forecast_date)
        
        if weather_df is None or weather_df.empty:
            return jsonify({'error': 'No data available'}), 404
        
        # Generate predictions
        predictions = []
        for _, row in weather_df.iterrows():
            pred_result = get_ml_predictor().predict_demand(
                region=region,
                temperature=row['temperature_2m'],
                humidity=row['relative_humidity_2m'],
                wind_speed=row['wind_speed_10m'],
                hour=row['hour']
            )
            predictions.append(pred_result['prediction'])
        
        # Create optimized chart
        plt.style.use('seaborn-v0_8')
        fig, ax = plt.subplots(figsize=(12, 6))
        
        hours = list(range(24))
        ax.plot(hours, predictions, 'b-', linewidth=3, marker='o', markersize=4, 
                label=f'{region} Demand Forecast')
        ax.fill_between(hours, predictions, alpha=0.3)
        
        ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax.set_ylabel('Electricity Demand (MW)', fontsize=12, fontweight='bold')
        ax.set_title(f'24-Hour Electricity Demand Forecast - {region}\n{forecast_date.strftime("%B %d, %Y")}', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Peak demand annotation
        peak_idx = np.argmax(predictions)
        ax.annotate(f'Peak: {predictions[peak_idx]:.0f} MW\nat {hours[peak_idx]}:00', 
                   xy=(peak_idx, predictions[peak_idx]), xytext=(peak_idx+2, predictions[peak_idx]+50),
                   arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        # Save to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return jsonify({
            'image': f'data:image/png;base64,{image_base64}',
            'peak_demand': max(predictions),
            'peak_hour': hours[np.argmax(predictions)]
        })
        
    except Exception as e:
        print(f"❌ Chart Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear all caches for fresh data"""
    try:
        if weather_service:
            weather_service.clear_cache()
        if ml_predictor:
            ml_predictor.clear_cache()
        return jsonify({'success': True, 'message': 'Cache cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'weather': weather_service is not None,
            'ml_predictor': ml_predictor is not None
        }
    })

if __name__ == '__main__':
    print("🚀 Starting PowerPulse Enhanced (Optimized)")
    print("🌟 Features: Fast loading, lazy initialization, caching")
    print("🔗 Access at: http://localhost:5000")
    
    # Run with optimized settings
    app.run(
        debug=False,  # Disabled debug mode for performance
        host='0.0.0.0',
        port=5000,
        threaded=True,
        use_reloader=False  # Disabled reloader to prevent model reloading
    )
