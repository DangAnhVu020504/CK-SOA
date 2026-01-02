"""
Product Service - Quản lý sản phẩm
Port: 5001
Database: MySQL (product_db)
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(services_dir)
sys.path.insert(0, root_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(root_dir, '.env'))

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuration - MySQL
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'product-service-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'PRODUCT_DB_URL', 
    f'sqlite:///{current_dir}/product_service.db'  # Fallback to SQLite
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 280,
    'pool_pre_ping': True
}

CORS(app)
db = SQLAlchemy(app)


# ============ MODELS ============

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    barcode = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    unit = db.Column(db.String(20), default='cái')
    cost_price = db.Column(db.Float, default=0)
    selling_price = db.Column(db.Float, default=0)
    supplier_id = db.Column(db.Integer, nullable=True)
    manufacturing_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'barcode': self.barcode,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'unit': self.unit,
            'cost_price': self.cost_price,
            'selling_price': self.selling_price,
            'supplier_id': self.supplier_id,
            'manufacturing_date': self.manufacturing_date.isoformat() if self.manufacturing_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ============ ROUTES ============

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'product_service',
        'port': 5001,
        'database': 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in products],
        'count': len(products)
    }), 200


@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': product.to_dict()
    }), 200


@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    if not data.get('name') or not data.get('sku'):
        return jsonify({'success': False, 'message': 'Tên và SKU là bắt buộc'}), 400
    
    # Parse dates
    mfg_date = None
    exp_date = None
    if data.get('manufacturing_date'):
        try:
            mfg_date = datetime.strptime(data['manufacturing_date'], '%Y-%m-%d').date()
        except:
            pass
    if data.get('expiry_date'):
        try:
            exp_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        except:
            pass
    
    product = Product(
        sku=data['sku'],
        barcode=data.get('barcode'),
        name=data['name'],
        description=data.get('description'),
        category=data.get('category'),
        unit=data.get('unit', 'cái'),
        cost_price=data.get('cost_price') or data.get('cost', 0),
        selling_price=data.get('selling_price') or data.get('price', 0),
        supplier_id=data.get('supplier_id'),
        manufacturing_date=mfg_date,
        expiry_date=exp_date
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Tạo sản phẩm thành công',
        'data': product.to_dict()
    }), 201


@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'category' in data:
        product.category = data['category']
    if 'unit' in data:
        product.unit = data['unit']
    if 'cost_price' in data or 'cost' in data:
        product.cost_price = data.get('cost_price') or data.get('cost', 0)
    if 'selling_price' in data or 'price' in data:
        product.selling_price = data.get('selling_price') or data.get('price', 0)
    if 'barcode' in data:
        product.barcode = data['barcode']
    if 'supplier_id' in data:
        product.supplier_id = data['supplier_id']
    if 'manufacturing_date' in data:
        if data['manufacturing_date']:
            try:
                product.manufacturing_date = datetime.strptime(data['manufacturing_date'], '%Y-%m-%d').date()
            except:
                pass
        else:
            product.manufacturing_date = None
    if 'expiry_date' in data:
        if data['expiry_date']:
            try:
                product.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
            except:
                pass
        else:
            product.expiry_date = None
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Cập nhật sản phẩm thành công',
        'data': product.to_dict()
    }), 200


@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    product.is_active = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Xóa sản phẩm thành công'
    }), 200


@app.route('/api/products/by-barcode/<barcode>', methods=['GET'])
def get_by_barcode(barcode):
    product = Product.query.filter_by(barcode=barcode, is_active=True).first()
    if not product:
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    return jsonify({'success': True, 'data': product.to_dict()}), 200


@app.route('/api/products/by-sku/<sku>', methods=['GET'])
def get_by_sku(sku):
    product = Product.query.filter_by(sku=sku, is_active=True).first()
    if not product:
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    return jsonify({'success': True, 'data': product.to_dict()}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'message': 'Lỗi server'}), 500


# ============ MAIN ============

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Đăng ký với Consul
    try:
        from shared.consul_utils import register_flask_service
        register_flask_service(app, 'product_service', 5001, ['product', 'catalog'])
    except Exception as e:
        print(f"Warning: Could not register with Consul: {e}")
    
    db_type = 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    print("=" * 50)
    print(f"  Product Service running on port 5001")
    print(f"  Database: {db_type}")
    print("=" * 50)
    app.run(debug=True, port=5001, host='0.0.0.0')
