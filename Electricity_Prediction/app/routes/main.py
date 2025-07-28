"""
Main Routes - Home, Forecast, and Core Functionality
Simplified version using your existing models and logic
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime
from utils.ml_predictor import MLPredictor
from utils.weather_service import WeatherService
from utils.data_processor import DataProcessor

main_bp = Blueprint('main', __name__)

# Initialize services
ml_predictor = MLPredictor()
weather_service = WeatherService()
data_processor = DataProcessor()

# Your regions (from your existing code)
REGIONS = ['DELHI', 'BRPL', 'BYPL', 'NDPL', 'NDMC', 'MES']

@main_bp.route('/')
def index():
    """Enhanced home page with dashboard preview"""
    return render_template('index.html', regions=REGIONS)

@main_bp.route('/forecast', methods=['GET', 'POST'])
def forecast():
    """Enhanced forecast page with your existing logic"""
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
                return render_template('forecast.html', regions=REGIONS, 
                                     selected_date=selected_date)
            
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

@main_bp.route('/api/regions')
def api_regions():
    """API endpoint for regions"""
    return jsonify([{'code': region, 'name': region} for region in REGIONS])

@main_bp.route('/api/predict', methods=['POST'])
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
