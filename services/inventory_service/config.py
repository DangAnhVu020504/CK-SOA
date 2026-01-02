"""
Inventory Service - Configuration
"""
import os

# Lấy đường dẫn
current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(services_dir)

# Service info
SERVICE_NAME = 'inventory_service'
SERVICE_PORT = 5002
SERVICE_TAGS = ['inventory', 'stock']

# External service URLs
PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://localhost:5001')

# Database config
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'inventory-service-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'INVENTORY_DB_URL',
        f'sqlite:///{current_dir}/inventory_service.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280, 'pool_pre_ping': True}
