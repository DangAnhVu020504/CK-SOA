"""
Inventory Service - Utility Functions
"""
import requests
from datetime import datetime, timedelta
from config import PRODUCT_SERVICE_URL
from models import Inventory


def fetch_products_with_expiry():
    """Lấy danh sách sản phẩm có ngày hết hạn từ product_service"""
    try:
        response = requests.get(f'{PRODUCT_SERVICE_URL}/api/products', timeout=5)
        if response.status_code == 200:
            return response.json().get('data', [])
    except Exception as e:
        print(f"Error fetching products: {e}")
    return []


def get_expiry_warnings(days=30):
    """Lấy cảnh báo sản phẩm sắp hết hạn"""
    products = fetch_products_with_expiry()
    today = datetime.now().date()
    warnings = []
    
    for p in products:
        if p.get('expiry_date'):
            try:
                expiry = datetime.strptime(p['expiry_date'], '%Y-%m-%d').date()
                days_left = (expiry - today).days
                
                if days_left <= days:
                    # Lấy số lượng từ inventory
                    inv = Inventory.query.filter_by(product_id=p['id']).first()
                    quantity = inv.quantity if inv else 0
                    
                    warning_level = 'critical' if days_left < 0 else ('warning' if days_left <= 7 else 'notice')
                    
                    warnings.append({
                        'product_id': p['id'],
                        'product_name': p['name'],
                        'batch_number': f"BATCH-{p['id']:04d}",
                        'expiry_date': p['expiry_date'],
                        'quantity': quantity,
                        'days_left': days_left,
                        'warning_level': warning_level
                    })
            except:
                pass
    
    return warnings
