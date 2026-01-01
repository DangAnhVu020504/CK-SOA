"""
Sales Service - Quản lý bán hàng (POS)
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from shared.database import db

app = Flask(__name__)
app.config.from_object(config['development'])

CORS(app)
db.init_app(app)

# Import models
from models.sales_model import Invoice, InvoiceDetail

# Import routes
from routes.sales_routes import sales_bp

# Đăng ký blueprint
app.register_blueprint(sales_bp, url_prefix='/api/sales')

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'message': 'Endpoint không tìm thấy',
        'data': None
    }), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'sales_service'
    }), 200

@app.before_request
def create_tables():
    """Tự động tạo bảng nếu chưa tồn tại"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5003, host='0.0.0.0')
