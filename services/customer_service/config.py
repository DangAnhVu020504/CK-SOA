"""
Customer Service - Configuration
"""
import os

# Lấy đường dẫn
current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(services_dir)

# Service info
SERVICE_NAME = 'customer_service'
SERVICE_PORT = 5005
SERVICE_TAGS = ['customer', 'loyalty']

# Database config
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'customer-service-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'CUSTOMER_DB_URL',
        f'sqlite:///{current_dir}/customer_service.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280, 'pool_pre_ping': True}
