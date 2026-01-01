"""
Product Service - Quản lý sản phẩm
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from shared.database import db
from shared.utils import handle_exceptions

app = Flask(__name__)
app.config.from_object(config['development'])

CORS(app)
db.init_app(app)

# Import models
from models.product_model import Product

# Import routes
from routes.product_routes import product_bp

# Đăng ký blueprint
app.register_blueprint(product_bp, url_prefix='/api/products')

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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'product_service'
    }), 200

@app.before_request
def create_tables():
    """Tự động tạo bảng nếu chưa tồn tại"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
