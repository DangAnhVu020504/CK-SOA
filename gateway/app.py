"""
API Gateway - Điều phối requests với Consul Service Discovery
Port: 5000
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
import logging

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gateway-secret-key')

CORS(app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ CONSUL INTEGRATION ============
from shared.consul_utils import ConsulClient, register_flask_service

consul = ConsulClient()

# Service configuration với fallback URLs
SERVICES_CONFIG = {
    'product_service': {'port': 5001, 'fallback': 'http://localhost:5001'},
    'inventory_service': {'port': 5002, 'fallback': 'http://localhost:5002'},
    'sales_service': {'port': 5003, 'fallback': 'http://localhost:5003'},
    'supplier_service': {'port': 5004, 'fallback': 'http://localhost:5004'},
    'customer_service': {'port': 5005, 'fallback': 'http://localhost:5005'},
    'employee_service': {'port': 5006, 'fallback': 'http://localhost:5006'},
    'auth_service': {'port': 5100, 'fallback': 'http://localhost:5100'},
}


def get_service_url(service_name: str) -> str:
    """
    Lấy URL của service từ Consul, fallback nếu không có Consul
    """
    # Thử lấy từ Consul trước
    if consul.is_available():
        url = consul.get_service_url(service_name)
        if url:
            return url
    
    # Fallback về URL cố định
    config = SERVICES_CONFIG.get(service_name, {})
    fallback_url = config.get('fallback', os.environ.get(
        f'{service_name.upper()}_URL', 
        f'http://localhost:{config.get("port", 5000)}'
    ))
    
    return fallback_url


def proxy_request(service_name: str, path: str = ''):
    """Forward request tới service với Consul discovery"""
    service_url = get_service_url(service_name)
    
    try:
        url = f'{service_url}{path}'
        
        if request.method == 'GET':
            response = requests.get(url, params=request.args, timeout=30)
        elif request.method == 'POST':
            response = requests.post(url, json=request.get_json(), timeout=30)
        elif request.method == 'PUT':
            response = requests.put(url, json=request.get_json(), timeout=30)
        elif request.method == 'DELETE':
            response = requests.delete(url, timeout=30)
        else:
            return jsonify({'success': False, 'message': 'Method not allowed'}), 405
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error to {service_name} at {service_url}")
        return jsonify({
            'success': False,
            'message': f'Không thể kết nối tới {service_name}',
            'data': None
        }), 503
    except Exception as e:
        logger.error(f"Error proxying to {service_name}: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': None
        }), 500


# ============ FRONTEND ROUTES ============

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/products')
def products_page():
    return render_template('products.html')


@app.route('/inventory')
def inventory_page():
    return render_template('inventory.html')


@app.route('/sales')
def sales_page():
    return render_template('sales.html')


@app.route('/suppliers')
def suppliers_page():
    return render_template('suppliers.html')


@app.route('/customers')
def customers_page():
    return render_template('customers.html')


@app.route('/employees')
def employees_page():
    return render_template('employees.html')


@app.route('/purchase-orders')
def purchase_orders_page():
    return render_template('purchase-orders.html')


@app.route('/reports')
def reports_page():
    return render_template('reports.html')


@app.route('/invoices')
def invoices_page():
    return render_template('invoices.html')


# ============ STAFF ROUTES ============

@app.route('/staff-dashboard')
def staff_dashboard():
    return render_template('staff-dashboard.html')


@app.route('/staff/customers')
def staff_customers_page():
    return render_template('staff-customers.html')


@app.route('/staff/products')
def staff_products_page():
    return render_template('staff-products.html')


@app.route('/staff/sales')
def staff_sales_page():
    return render_template('staff-sales.html')


# ============ CONSUL ENDPOINTS ============

@app.route('/consul/status', methods=['GET'])
def consul_status():
    """Kiểm tra trạng thái Consul"""
    return jsonify({
        'consul_available': consul.is_available(),
        'consul_host': consul.host,
        'consul_port': consul.port
    }), 200


@app.route('/consul/services', methods=['GET'])
def consul_services():
    """Liệt kê tất cả services đã đăng ký trên Consul"""
    if not consul.is_available():
        return jsonify({
            'success': False,
            'message': 'Consul không khả dụng',
            'data': None
        }), 503
    
    services = consul.get_all_services()
    return jsonify({
        'success': True,
        'data': services
    }), 200


@app.route('/consul/service/<name>/health', methods=['GET'])
def consul_service_health(name):
    """Lấy thông tin health của một service"""
    if not consul.is_available():
        return jsonify({
            'success': False,
            'message': 'Consul không khả dụng',
            'data': None
        }), 503
    
    health = consul.get_service_health(name)
    return jsonify({
        'success': True,
        'data': health
    }), 200


@app.route('/consul/discover/<name>', methods=['GET'])
def consul_discover(name):
    """Tìm các instances của một service"""
    if not consul.is_available():
        return jsonify({
            'success': False,
            'message': 'Consul không khả dụng',
            'data': None
        }), 503
    
    services = consul.discover_service(name)
    return jsonify({
        'success': True,
        'data': services
    }), 200


# ============ HEALTH CHECK ============

@app.route('/health', methods=['GET'])
def health_check():
    """Kiểm tra trạng thái Gateway và tất cả services"""
    services_status = {}
    consul_available = consul.is_available()
    
    for service_name in SERVICES_CONFIG.keys():
        if consul_available:
            # Lấy health từ Consul
            health = consul.get_service_health(service_name)
            if health:
                services_status[service_name] = {
                    'status': health[0]['status'] if health else 'unknown',
                    'instances': len(health),
                    'source': 'consul'
                }
            else:
                # Fallback check
                try:
                    url = SERVICES_CONFIG[service_name]['fallback']
                    response = requests.get(f'{url}/health', timeout=2)
                    services_status[service_name] = {
                        'status': 'passing' if response.status_code == 200 else 'critical',
                        'instances': 1,
                        'source': 'direct'
                    }
                except:
                    services_status[service_name] = {
                        'status': 'critical',
                        'instances': 0,
                        'source': 'direct'
                    }
        else:
            # Direct check nếu không có Consul
            try:
                url = SERVICES_CONFIG[service_name]['fallback']
                response = requests.get(f'{url}/health', timeout=2)
                services_status[service_name] = {
                    'status': 'passing' if response.status_code == 200 else 'critical',
                    'instances': 1,
                    'source': 'direct'
                }
            except:
                services_status[service_name] = {
                    'status': 'critical',
                    'instances': 0,
                    'source': 'direct'
                }
    
    all_healthy = all(s['status'] == 'passing' for s in services_status.values())
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'gateway': 'running',
        'consul': {
            'available': consul_available,
            'host': f'{consul.host}:{consul.port}'
        },
        'services': services_status
    }), 200 if all_healthy else 503


@app.route('/api', methods=['GET'])
def api_info():
    """Thông tin API với Consul discovery"""
    consul_available = consul.is_available()
    
    services_info = {}
    for name, config in SERVICES_CONFIG.items():
        if consul_available:
            discovered_url = consul.get_service_url(name)
            services_info[name] = {
                'url': discovered_url or config['fallback'],
                'discovered': discovered_url is not None
            }
        else:
            services_info[name] = {
                'url': config['fallback'],
                'discovered': False
            }
    
    return jsonify({
        'name': 'Mini Supermarket Management API',
        'version': '2.0.0',
        'architecture': 'SOA with Consul Service Discovery',
        'consul': {
            'available': consul_available,
            'host': f'{consul.host}:{consul.port}'
        },
        'services': services_info
    }), 200


# ============ PRODUCT SERVICE ROUTES ============

@app.route('/api/products', methods=['GET', 'POST'])
def products():
    return proxy_request('product_service', '/api/products')


@app.route('/api/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def product_detail(id):
    return proxy_request('product_service', f'/api/products/{id}')


@app.route('/api/products/by-barcode/<barcode>', methods=['GET'])
def product_by_barcode(barcode):
    return proxy_request('product_service', f'/api/products/by-barcode/{barcode}')


@app.route('/api/products/by-sku/<sku>', methods=['GET'])
def product_by_sku(sku):
    return proxy_request('product_service', f'/api/products/by-sku/{sku}')


@app.route('/api/products/search', methods=['POST'])
def product_search():
    return proxy_request('product_service', '/api/products/search')


# ============ INVENTORY SERVICE ROUTES ============

@app.route('/api/inventory/all', methods=['GET'])
def inventory_all():
    return proxy_request('inventory_service', '/api/inventory/all')


@app.route('/api/inventory/by-product/<int:product_id>', methods=['GET'])
def inventory_by_product(product_id):
    return proxy_request('inventory_service', f'/api/inventory/by-product/{product_id}')


@app.route('/api/inventory/low-stock', methods=['GET'])
def inventory_low_stock():
    return proxy_request('inventory_service', '/api/inventory/low-stock')


@app.route('/api/inventory/expiry-warnings', methods=['GET'])
def inventory_expiry_warnings():
    return proxy_request('inventory_service', '/api/inventory/expiry-warnings')


@app.route('/api/inventory/init', methods=['POST'])
def inventory_init():
    return proxy_request('inventory_service', '/api/inventory/init')


@app.route('/api/inventory/adjust', methods=['POST'])
def inventory_adjust():
    return proxy_request('inventory_service', '/api/inventory/adjust')


@app.route('/api/inventory/<int:product_id>', methods=['PUT'])
def inventory_update(product_id):
    return proxy_request('inventory_service', f'/api/inventory/{product_id}')


@app.route('/api/inventory/movements', methods=['GET'])
def inventory_movements():
    return proxy_request('inventory_service', '/api/inventory/movements')


@app.route('/api/inventory/movements/<int:product_id>', methods=['GET'])
def inventory_movements_by_product(product_id):
    return proxy_request('inventory_service', f'/api/inventory/movements/{product_id}')


# ============ SALES SERVICE ROUTES ============

@app.route('/api/sales/invoices', methods=['GET', 'POST'])
def sales_invoices():
    return proxy_request('sales_service', '/api/sales/invoices')


@app.route('/api/sales/invoices/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def sales_invoice_detail(id):
    return proxy_request('sales_service', f'/api/sales/invoices/{id}')


@app.route('/api/sales/invoices/<int:id>/add-item', methods=['POST'])
def sales_add_item(id):
    return proxy_request('sales_service', f'/api/sales/invoices/{id}/add-item')


@app.route('/api/sales/invoices/<int:id>/checkout', methods=['PUT'])
def sales_checkout(id):
    return proxy_request('sales_service', f'/api/sales/invoices/{id}/checkout')


@app.route('/api/sales/invoices/by-number/<number>', methods=['GET'])
def sales_by_number(number):
    return proxy_request('sales_service', f'/api/sales/invoices/by-number/{number}')


@app.route('/api/sales/revenue', methods=['GET'])
def sales_revenue():
    return proxy_request('sales_service', '/api/sales/revenue')


@app.route('/api/sales/invoices/search', methods=['GET'])
def sales_invoice_search():
    return proxy_request('sales_service', '/api/sales/invoices/search')


# ============ SUPPLIER SERVICE ROUTES ============

@app.route('/api/suppliers', methods=['GET', 'POST'])
def suppliers():
    return proxy_request('supplier_service', '/api/suppliers')


@app.route('/api/suppliers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def supplier_detail(id):
    return proxy_request('supplier_service', f'/api/suppliers/{id}')


@app.route('/api/suppliers/purchase-orders', methods=['GET', 'POST'])
def purchase_orders():
    return proxy_request('supplier_service', '/api/suppliers/purchase-orders')


@app.route('/api/suppliers/purchase-orders/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def purchase_order_detail(id):
    return proxy_request('supplier_service', f'/api/suppliers/purchase-orders/{id}')


@app.route('/api/suppliers/purchase-orders/<int:id>/receive', methods=['PUT'])
def purchase_order_receive(id):
    return proxy_request('supplier_service', f'/api/suppliers/purchase-orders/{id}/receive')


@app.route('/api/suppliers/purchase-orders/<int:id>/pay', methods=['PUT'])
def purchase_order_pay(id):
    return proxy_request('supplier_service', f'/api/suppliers/purchase-orders/{id}/pay')


# ============ CUSTOMER SERVICE ROUTES ============

@app.route('/api/customers', methods=['GET', 'POST'])
def customers():
    return proxy_request('customer_service', '/api/customers')


@app.route('/api/customers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def customer_detail(id):
    return proxy_request('customer_service', f'/api/customers/{id}')


@app.route('/api/customers/by-phone/<phone>', methods=['GET'])
def customer_by_phone(phone):
    return proxy_request('customer_service', f'/api/customers/by-phone/{phone}')


@app.route('/api/customers/search', methods=['GET'])
def customer_search():
    return proxy_request('customer_service', '/api/customers/search')


@app.route('/api/customers/<int:id>/add-points', methods=['POST'])
def customer_add_points(id):
    return proxy_request('customer_service', f'/api/customers/{id}/add-points')


@app.route('/api/customers/<int:id>/use-points', methods=['POST'])
def customer_use_points(id):
    return proxy_request('customer_service', f'/api/customers/{id}/use-points')


@app.route('/api/customers/<int:id>/purchase-history', methods=['GET'])
def customer_history(id):
    return proxy_request('customer_service', f'/api/customers/{id}/purchase-history')


@app.route('/api/customers/ranks', methods=['GET'])
def customer_ranks():
    return proxy_request('customer_service', '/api/customers/ranks')


@app.route('/api/customers/statistics', methods=['GET'])
def customer_statistics():
    return proxy_request('customer_service', '/api/customers/statistics')


# ============ EMPLOYEE SERVICE ROUTES ============

@app.route('/api/employees', methods=['GET', 'POST'])
def employees():
    return proxy_request('employee_service', '/api/employees')


@app.route('/api/employees/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def employee_detail(id):
    return proxy_request('employee_service', f'/api/employees/{id}')


@app.route('/api/employees/search', methods=['GET'])
def employee_search():
    return proxy_request('employee_service', '/api/employees/search')


@app.route('/api/employees/login', methods=['POST'])
def employee_login():
    return proxy_request('employee_service', '/api/employees/login')


@app.route('/api/employees/roles', methods=['GET', 'POST'])
def employee_roles():
    return proxy_request('employee_service', '/api/employees/roles')


@app.route('/api/employees/shifts', methods=['GET', 'POST'])
def employee_shifts():
    return proxy_request('employee_service', '/api/employees/shifts')


@app.route('/api/employees/employee-shifts', methods=['GET', 'POST'])
def employee_shift_assignments():
    return proxy_request('employee_service', '/api/employees/employee-shifts')


@app.route('/api/employees/employee-shifts/<int:id>/check-in', methods=['POST'])
def employee_checkin(id):
    return proxy_request('employee_service', f'/api/employees/employee-shifts/{id}/check-in')


@app.route('/api/employees/employee-shifts/<int:id>/check-out', methods=['POST'])
def employee_checkout(id):
    return proxy_request('employee_service', f'/api/employees/employee-shifts/{id}/check-out')


@app.route('/api/employees/statistics', methods=['GET'])
def employee_statistics():
    return proxy_request('employee_service', '/api/employees/statistics')


# ============ AUTH SERVICE ROUTES ============

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    return proxy_request('auth_service', '/api/auth/login')


@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    return proxy_request('auth_service', '/api/auth/register')


@app.route('/api/auth/refresh', methods=['POST'])
def auth_refresh():
    return proxy_request('auth_service', '/api/auth/refresh')


@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    return proxy_request('auth_service', '/api/auth/me')


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


if __name__ == '__main__':
    print("=" * 60)
    print("  Mini Supermarket Management - API Gateway")
    print("  With Consul Service Discovery")
    print("=" * 60)
    
    consul_status = "Available" if consul.is_available() else "Not Available"
    print(f"\nConsul: {consul_status} ({consul.host}:{consul.port})")
    
    print("\nServices Configuration:")
    for name, config in SERVICES_CONFIG.items():
        print(f"  {name:20} -> Port {config['port']}")
    
    print("\n" + "=" * 60)
    print("Gateway running at: http://localhost:5000")
    print("Consul endpoints:")
    print("  /consul/status          - Kiểm tra Consul")
    print("  /consul/services        - Liệt kê services")
    print("  /consul/discover/<name> - Tìm service")
    print("=" * 60 + "\n")
    
    # Đăng ký Gateway với Consul
    register_flask_service(app, 'api_gateway', 5000, ['gateway', 'soa'])
    
    app.run(debug=True, port=5000, host='0.0.0.0')
