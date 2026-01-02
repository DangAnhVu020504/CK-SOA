"""
Sales Service - Configuration
"""
import os

# Lấy đường dẫn
current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(services_dir)

# Service info
SERVICE_NAME = 'sales_service'
SERVICE_PORT = 5003
SERVICE_TAGS = ['sales', 'pos']

# Database config
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sales-service-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SALES_DB_URL',
        f'sqlite:///{current_dir}/sales_service.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280, 'pool_pre_ping': True}
