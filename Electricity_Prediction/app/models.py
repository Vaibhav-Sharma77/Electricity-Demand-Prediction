"""
Database Models with B-tree Indexing for Performance
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json

class User(UserMixin, db.Model):
    """User model with authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Region(db.Model):
    """Region model for different electricity distribution areas"""
    __tablename__ = 'regions'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='region', lazy='dynamic')
    historical_data = db.relationship('HistoricalData', backref='region', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active
        }

class Prediction(db.Model):
    """Prediction model with B-tree indexing for fast queries"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False, index=True)
    prediction_date = db.Column(db.Date, nullable=False, index=True)
    prediction_hour = db.Column(db.Integer, nullable=False, index=True)
    
    # Weather features
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    
    # Predictions from different models
    rf_prediction = db.Column(db.Float, nullable=False)
    lstm_prediction = db.Column(db.Float, nullable=False)
    xgb_prediction = db.Column(db.Float, nullable=False)
    ensemble_prediction = db.Column(db.Float, nullable=False, index=True)
    
    # Metadata
    model_version = db.Column(db.String(20), default='v1.0')
    confidence_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Composite index for fast time-series queries
    __table_args__ = (
        db.Index('idx_prediction_datetime', 'prediction_date', 'prediction_hour'),
        db.Index('idx_region_datetime', 'region_id', 'prediction_date', 'prediction_hour'),
        db.Index('idx_user_predictions', 'user_id', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'region_code': self.region.code,
            'prediction_date': self.prediction_date.isoformat(),
            'prediction_hour': self.prediction_hour,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'wind_speed': self.wind_speed,
            'ensemble_prediction': self.ensemble_prediction,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat()
        }

class HistoricalData(db.Model):
    """Historical electricity demand data with B-tree indexing"""
    __tablename__ = 'historical_data'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    demand = db.Column(db.Float, nullable=False)
    
    # Weather data
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    
    # Additional features
    is_holiday = db.Column(db.Boolean, default=False)
    day_of_week = db.Column(db.Integer, index=True)
    month = db.Column(db.Integer, index=True)
    season = db.Column(db.String(10), index=True)
    
    # Composite indexes for time-series queries
    __table_args__ = (
        db.Index('idx_region_timestamp', 'region_id', 'timestamp'),
        db.Index('idx_timestamp_demand', 'timestamp', 'demand'),
        db.Index('idx_seasonal_data', 'region_id', 'month', 'day_of_week'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'region_code': self.region.code,
            'timestamp': self.timestamp.isoformat(),
            'demand': self.demand,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'wind_speed': self.wind_speed
        }

class ModelMetrics(db.Model):
    """Store model performance metrics"""
    __tablename__ = 'model_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False, index=True)
    model_type = db.Column(db.String(20), nullable=False, index=True)  # 'rf', 'lstm', 'xgb', 'ensemble'
    model_version = db.Column(db.String(20), default='v1.0')
    
    # Performance metrics
    mse = db.Column(db.Float)
    rmse = db.Column(db.Float)
    mae = db.Column(db.Float)
    r2_score = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    
    # Training metadata
    training_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    training_samples = db.Column(db.Integer)
    features_used = db.Column(db.Text)  # JSON string of features
    hyperparameters = db.Column(db.Text)  # JSON string of hyperparameters
    
    def to_dict(self):
        return {
            'id': self.id,
            'region_code': self.region.code,
            'model_type': self.model_type,
            'model_version': self.model_version,
            'rmse': self.rmse,
            'mae': self.mae,
            'r2_score': self.r2_score,
            'accuracy': self.accuracy,
            'training_date': self.training_date.isoformat()
        }

class APIKey(db.Model):
    """API keys for external access"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    key_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    rate_limit = db.Column(db.Integer, default=1000)  # requests per hour
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'rate_limit': self.rate_limit,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None
        }

class CacheEntry(db.Model):
    """Cache management for predictions"""
    __tablename__ = 'cache_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    data = db.Column(db.Text, nullable=False)  # JSON string
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def get_data(self):
        return json.loads(self.data)
    
    def set_data(self, data):
        self.data = json.dumps(data)
