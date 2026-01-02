"""
Product Service - Configuration
"""
import os

# Lấy đường dẫn
current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(services_dir)

# Service info
SERVICE_NAME = 'product_service'
SERVICE_PORT = 5001
SERVICE_TAGS = ['product', 'catalog']

# Database config
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'product-service-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'PRODUCT_DB_URL',
        f'sqlite:///{current_dir}/product_service.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280, 'pool_pre_ping': True}
