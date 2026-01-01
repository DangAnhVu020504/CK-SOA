"""
Configuration cho ứng dụng Mini Supermarket SOA
"""
import os
from datetime import timedelta

class Config:
    """Cấu hình cơ bản"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-mini-supermarket'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mini_supermarket.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-key-mini-supermarket'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Services URLs
    PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL') or 'http://localhost:5001'
    INVENTORY_SERVICE_URL = os.environ.get('INVENTORY_SERVICE_URL') or 'http://localhost:5002'
    SALES_SERVICE_URL = os.environ.get('SALES_SERVICE_URL') or 'http://localhost:5003'
    SUPPLIER_SERVICE_URL = os.environ.get('SUPPLIER_SERVICE_URL') or 'http://localhost:5004'
    
    # API Gateway
    GATEWAY_URL = os.environ.get('GATEWAY_URL') or 'http://localhost:5000'
    
    # Logging
    LOG_FILE = 'logs/app.log'
    LOG_LEVEL = 'INFO'

class DevelopmentConfig(Config):
    """Cấu hình phát triển"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Cấu hình kiểm tra"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Cấu hình sản xuất"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mini_supermarket.db'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
