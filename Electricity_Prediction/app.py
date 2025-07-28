"""
PowerPulse Enhanced - Main Application
Enhanced version of your existing app.py with modern features
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
from utils.ml_predictor import MLPredictor
from utils.weather_service import WeatherService
from utils.data_processor import DataProcessor

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Initialize services
ml_predictor = MLPredictor()
weather_service = WeatherService()
data_processor = DataProcessor()

# Your regions (from your existing code)
REGIONS = ['DELHI', 'BRPL', 'BYPL', 'NDPL', 'NDMC', 'MES']

def create_plot(hourly_predictions, selected_regions, selected_date):
    """Enhanced version of your create_plot function"""
    plt.figure(figsize=(12, 6))
    
    for region in selected_regions:
        hours = list(range(24))
        demands = [hourly_predictions[region][hour]['predicted_demand'] for hour in hours]
        
        plt.plot(hours, demands, marker='o', label=region, linewidth=2)
    
    plt.title(f'Electricity Demand Forecast - {selected_date}', fontsize=16, fontweight='bold')
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Demand (MW)', fontsize=12)
    plt.xticks(hours)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save the plot
    plot_filename = 'static/predicted_demand_plot.png'
    os.makedirs('static', exist_ok=True)
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    return plot_filename

@app.route('/')
def index():
    """Enhanced home page"""
    return render_template('index.html', regions=REGIONS)

@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    """Enhanced forecast page using your existing logic"""
    predictions = []
    peak_least_demand_info = []
    plot_filename = None
    selected_date = None
    selected_regions = []
    
    if request.method == 'POST':
        try:
            selected_regions = request.form.getlist('region')
            selected_date = request.form.get('date')
            
            if not selected_regions:
                flash('Please select at least one region.', 'warning')
                return render_template('forecast.html', regions=REGIONS, selected_date=selected_date)
            
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
            
            # Get weather forecast data using your existing logic
            weather_data = weather_service.fetch_weather_forecast(date_obj)
            
            if weather_data is not None:
                hourly_predictions = {region: [] for region in selected_regions}
                
                # Process each hour using your existing prediction logic
                for index, row in weather_data.iterrows():
                    temperature = row['temperature_2m']
                    humidity = row['relative_humidity_2m']
                    wind_speed = row['wind_speed_10m']
                    hour = row['hour']
                    
                    for region in selected_regions:
                        try:
                            # Use your trained models for prediction
                            predicted_demand = ml_predictor.predict(
                                region=region,
                                temperature=temperature,
                                humidity=humidity,
                                wind_speed=wind_speed,
                                hour=hour,
                                day=date_obj.day,
                                month=date_obj.month,
                                year=date_obj.year
                            )
                            
                            hourly_predictions[region].append({
                                'hour': hour,
                                'predicted_demand': predicted_demand['ensemble']
                            })
                            
                        except Exception as e:
                            print(f"Error predicting for region {region} at hour {hour}: {e}")
                            hourly_predictions[region].append({
                                'hour': hour,
                                'predicted_demand': 1000  # Fallback value
                            })
                
                # Format predictions for display (your existing logic)
                for hour in range(24):
                    row = {'time': f'{hour:02}:00'}
                    for region in selected_regions:
                        if hour < len(hourly_predictions[region]):
                            row[region] = round(hourly_predictions[region][hour]['predicted_demand'], 2)
                        else:
                            row[region] = 0
                    predictions.append(row)
                
                # Calculate peak and least demand info (your existing logic)
                for region in selected_regions:
                    if hourly_predictions[region]:
                        demands = [item['predicted_demand'] for item in hourly_predictions[region]]
                        peak_demand = max(demands)
                        least_demand = min(demands)
                        peak_hour = demands.index(peak_demand)
                        least_hour = demands.index(least_demand)
                        
                        peak_least_demand_info.append({
                            'region': region,
                            'peak_demand': round(peak_demand, 2),
                            'least_demand': round(least_demand, 2),
                            'peak_hour': f'{peak_hour:02}:00',
                            'least_hour': f'{least_hour:02}:00',
                        })
                
                # Generate enhanced plot
                plot_filename = data_processor.create_enhanced_plot(hourly_predictions, selected_regions, selected_date)
                
                flash(f'Predictions generated successfully for {len(selected_regions)} regions!', 'success')
                
            else:
                flash('Unable to fetch weather data. Please try again.', 'error')
                
        except Exception as e:
            print(f"Error processing forecast request: {e}")
            flash('An error occurred while generating predictions. Please try again.', 'error')
    
    return render_template('forecast.html',
                         predictions=predictions,
                         peak_least_demand_info=peak_least_demand_info,
                         plot_filename=plot_filename,
                         selected_date=selected_date,
                         selected_regions=selected_regions,
                         regions=REGIONS)

@app.route('/api/regions')
def api_regions():
    """API endpoint for regions"""
    return jsonify([{'code': region, 'name': region} for region in REGIONS])

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for predictions"""
    try:
        data = request.get_json()
        
        region = data.get('region')
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        wind_speed = data.get('wind_speed')
        hour = data.get('hour')
        day = data.get('day')
        month = data.get('month')
        year = data.get('year')
        
        prediction = ml_predictor.predict(
            region=region,
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            hour=hour,
            day=day,
            month=month,
            year=year
        )
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
