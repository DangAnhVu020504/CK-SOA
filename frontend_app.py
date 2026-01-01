"""
Frontend Router - Phục vụ các templates HTML
"""
from flask import Flask, render_template, request, jsonify
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'frontend-secret-key'

# ============ ROUTES ============

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard"""
    return render_template('dashboard.html')

@app.route('/products')
def products():
    """Quản lý sản phẩm"""
    return render_template('products.html')

@app.route('/inventory')
def inventory():
    """Quản lý tồn kho"""
    return render_template('inventory.html')

@app.route('/sales')
def sales():
    """Bán hàng POS"""
    return render_template('sales.html')

@app.route('/suppliers')
def suppliers():
    """Quản lý nhà cung cấp"""
    return render_template('suppliers.html')

@app.route('/purchase-orders')
def purchase_orders():
    """Đơn nhập hàng"""
    return render_template('suppliers.html')  # Shared template

@app.route('/reports')
def reports():
    """Báo cáo"""
    return render_template('index.html')  # Placeholder

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
