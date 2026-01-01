"""
API Gateway - Điều phối các requests tới các services
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, request
from flask_cors import CORS
from config import config
import requests
import logging

app = Flask(__name__)
app.config.from_object(config['development'])

CORS(app)

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
PRODUCT_SERVICE = 'http://localhost:5001'
INVENTORY_SERVICE = 'http://localhost:5002'
SALES_SERVICE = 'http://localhost:5003'
SUPPLIER_SERVICE = 'http://localhost:5004'

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'message': 'Endpoint không tìm thấy',
        'data': None
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'message': 'Lỗi server nội bộ',
        'data': None
    }), 500

# ============ HEALTH CHECK ============

@app.route('/health', methods=['GET'])
def health_check():
    """Kiểm tra trạng thái gateway"""
    services_status = {
        'product_service': check_service(PRODUCT_SERVICE),
        'inventory_service': check_service(INVENTORY_SERVICE),
        'sales_service': check_service(SALES_SERVICE),
        'supplier_service': check_service(SUPPLIER_SERVICE)
    }
    
    all_healthy = all(services_status.values())
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'services': services_status
    }), 200 if all_healthy else 503

def check_service(service_url):
    """Kiểm tra trạng thái của một service"""
    try:
        response = requests.get(f'{service_url}/health', timeout=2)
        return response.status_code == 200
    except:
        return False

# ============ PRODUCT SERVICE PROXY ============

@app.route('/api/products', methods=['GET', 'POST'])
def products_list():
    """Proxy tới Product Service"""
    try:
        if request.method == 'GET':
            response = requests.get(f'{PRODUCT_SERVICE}/api/products', params=request.args)
        else:
            response = requests.post(f'{PRODUCT_SERVICE}/api/products', json=request.get_json())
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling product service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Product Service',
            'data': None
        }), 503

@app.route('/api/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
def product_detail(product_id):
    """Proxy chi tiết sản phẩm"""
    try:
        url = f'{PRODUCT_SERVICE}/api/products/{product_id}'
        
        if request.method == 'GET':
            response = requests.get(url)
        elif request.method == 'PUT':
            response = requests.put(url, json=request.get_json())
        else:
            response = requests.delete(url)
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling product service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Product Service',
            'data': None
        }), 503

@app.route('/api/products/by-barcode/<barcode>', methods=['GET'])
def product_by_barcode(barcode):
    """Proxy tìm sản phẩm theo barcode"""
    try:
        response = requests.get(f'{PRODUCT_SERVICE}/api/products/by-barcode/{barcode}')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling product service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Product Service',
            'data': None
        }), 503

# ============ INVENTORY SERVICE PROXY ============

@app.route('/api/inventory/by-product/<int:product_id>', methods=['GET'])
def inventory_by_product(product_id):
    """Proxy lấy tồn kho"""
    try:
        response = requests.get(f'{INVENTORY_SERVICE}/api/inventory/by-product/{product_id}')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling inventory service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Inventory Service',
            'data': None
        }), 503

@app.route('/api/inventory/all', methods=['GET'])
def inventory_all():
    """Proxy lấy tất cả tồn kho"""
    try:
        response = requests.get(f'{INVENTORY_SERVICE}/api/inventory/all')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling inventory service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Inventory Service',
            'data': None
        }), 503

@app.route('/api/inventory/low-stock', methods=['GET'])
def inventory_low_stock():
    """Proxy lấy sản phẩm sắp hết"""
    try:
        response = requests.get(f'{INVENTORY_SERVICE}/api/inventory/low-stock')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling inventory service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Inventory Service',
            'data': None
        }), 503

@app.route('/api/inventory/expiry-warnings', methods=['GET'])
def inventory_expiry_warnings():
    """Proxy lấy cảnh báo hết hạn"""
    try:
        response = requests.get(f'{INVENTORY_SERVICE}/api/inventory/expiry-warnings')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling inventory service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Inventory Service',
            'data': None
        }), 503

@app.route('/api/inventory/init', methods=['POST'])
def inventory_init():
    """Proxy khởi tạo tồn kho"""
    try:
        response = requests.post(f'{INVENTORY_SERVICE}/api/inventory/init', json=request.get_json())
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling inventory service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Inventory Service',
            'data': None
        }), 503

@app.route('/api/inventory/adjust', methods=['POST'])
def inventory_adjust():
    """Proxy điều chỉnh tồn kho"""
    try:
        response = requests.post(f'{INVENTORY_SERVICE}/api/inventory/adjust', json=request.get_json())
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling inventory service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Inventory Service',
            'data': None
        }), 503

# ============ SALES SERVICE PROXY ============

@app.route('/api/sales/invoices', methods=['GET', 'POST'])
def sales_invoices():
    """Proxy hóa đơn"""
    try:
        if request.method == 'GET':
            response = requests.get(f'{SALES_SERVICE}/api/sales/invoices', params=request.args)
        else:
            response = requests.post(f'{SALES_SERVICE}/api/sales/invoices', json=request.get_json())
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling sales service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Sales Service',
            'data': None
        }), 503

@app.route('/api/sales/invoices/<int:invoice_id>/checkout', methods=['PUT'])
def sales_checkout(invoice_id):
    """Proxy thanh toán hóa đơn"""
    try:
        response = requests.put(f'{SALES_SERVICE}/api/sales/invoices/{invoice_id}/checkout', json=request.get_json())
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling sales service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Sales Service',
            'data': None
        }), 503

@app.route('/api/sales/invoices/<int:invoice_id>/add-item', methods=['POST'])
def sales_add_item(invoice_id):
    """Proxy thêm item vào hóa đơn"""
    try:
        response = requests.post(f'{SALES_SERVICE}/api/sales/invoices/{invoice_id}/add-item', json=request.get_json())
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling sales service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Sales Service',
            'data': None
        }), 503

@app.route('/api/sales/revenue', methods=['GET'])
def sales_revenue():
    """Proxy thống kê doanh thu"""
    try:
        response = requests.get(f'{SALES_SERVICE}/api/sales/revenue')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling sales service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Sales Service',
            'data': None
        }), 503

# ============ SUPPLIER SERVICE PROXY ============

@app.route('/api/suppliers', methods=['GET', 'POST'])
def suppliers_list():
    """Proxy danh sách nhà cung cấp"""
    try:
        if request.method == 'GET':
            response = requests.get(f'{SUPPLIER_SERVICE}/api/suppliers', params=request.args)
        else:
            response = requests.post(f'{SUPPLIER_SERVICE}/api/suppliers', json=request.get_json())
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling supplier service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Supplier Service',
            'data': None
        }), 503

@app.route('/api/suppliers/<int:supplier_id>', methods=['GET', 'PUT', 'DELETE'])
def supplier_detail(supplier_id):
    """Proxy chi tiết nhà cung cấp"""
    try:
        url = f'{SUPPLIER_SERVICE}/api/suppliers/{supplier_id}'
        
        if request.method == 'GET':
            response = requests.get(url)
        elif request.method == 'PUT':
            response = requests.put(url, json=request.get_json())
        else:
            response = requests.delete(url)
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling supplier service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Supplier Service',
            'data': None
        }), 503

@app.route('/api/suppliers/purchase-orders', methods=['GET', 'POST'])
def purchase_orders():
    """Proxy đơn nhập hàng"""
    try:
        if request.method == 'GET':
            response = requests.get(f'{SUPPLIER_SERVICE}/api/suppliers/purchase-orders', params=request.args)
        else:
            response = requests.post(f'{SUPPLIER_SERVICE}/api/suppliers/purchase-orders', json=request.get_json())
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling supplier service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Supplier Service',
            'data': None
        }), 503

@app.route('/api/suppliers/purchase-orders/<int:po_id>/receive', methods=['PUT'])
def purchase_order_receive(po_id):
    """Proxy nhận hàng từ đơn nhập"""
    try:
        response = requests.put(f'{SUPPLIER_SERVICE}/api/suppliers/purchase-orders/{po_id}/receive', json=request.get_json())
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling supplier service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Supplier Service',
            'data': None
        }), 503

@app.route('/api/suppliers/purchase-orders/<int:po_id>/pay', methods=['PUT'])
def purchase_order_pay(po_id):
    """Proxy thanh toán đơn nhập"""
    try:
        response = requests.put(f'{SUPPLIER_SERVICE}/api/suppliers/purchase-orders/{po_id}/pay', json=request.get_json())
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error calling supplier service: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Lỗi kết nối tới Supplier Service',
            'data': None
        }), 503

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
