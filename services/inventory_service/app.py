"""
Inventory Service - Quản lý tồn kho
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
from models.inventory_model import Inventory, InventoryMovement, ExpiryWarning

# Import routes
from routes.inventory_routes import inventory_bp

# Đăng ký blueprint
app.register_blueprint(inventory_bp, url_prefix='/api/inventory')

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
        'service': 'inventory_service'
    }), 200

@app.before_request
def create_tables():
    """Tự động tạo bảng nếu chưa tồn tại"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5002, host='0.0.0.0')
