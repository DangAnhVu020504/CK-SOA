"""
Inventory Service - Quản lý tồn kho
Port: 5002
Database: MySQL (inventory_db)
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

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'inventory-service-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'INVENTORY_DB_URL',
    f'sqlite:///{current_dir}/inventory_service.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280, 'pool_pre_ping': True}

CORS(app)
db = SQLAlchemy(app)


# ============ MODELS ============

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    min_quantity = db.Column(db.Integer, default=10)
    max_quantity = db.Column(db.Integer, default=1000)
    location = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'min_quantity': self.min_quantity,
            'max_quantity': self.max_quantity,
            'location': self.location,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'is_low_stock': self.quantity <= self.min_quantity
        }


class InventoryMovement(db.Model):
    __tablename__ = 'inventory_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.String(20))
    quantity = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String(100))
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'reference': self.reference,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============ ROUTES ============

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'inventory_service',
        'port': 5002,
        'database': 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@app.route('/api/inventory/all', methods=['GET'])
def get_all_inventory():
    items = Inventory.query.all()
    return jsonify({
        'success': True,
        'data': [i.to_dict() for i in items],
        'count': len(items)
    }), 200


@app.route('/api/inventory/by-product/<int:product_id>', methods=['GET'])
def get_by_product(product_id):
    item = Inventory.query.filter_by(product_id=product_id).first()
    if not item:
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    return jsonify({'success': True, 'data': item.to_dict()}), 200


@app.route('/api/inventory/low-stock', methods=['GET'])
def get_low_stock():
    items = Inventory.query.filter(Inventory.quantity <= Inventory.min_quantity).all()
    return jsonify({
        'success': True,
        'data': [i.to_dict() for i in items],
        'count': len(items)
    }), 200


@app.route('/api/inventory/init', methods=['POST'])
def init_inventory():
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'success': False, 'message': 'product_id là bắt buộc'}), 400
    
    existing = Inventory.query.filter_by(product_id=product_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Đã tồn tại'}), 400
    
    item = Inventory(
        product_id=product_id,
        quantity=data.get('quantity', 0),
        min_quantity=data.get('min_quantity', 10),
        max_quantity=data.get('max_quantity', 1000),
        location=data.get('location')
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Khởi tạo tồn kho thành công',
        'data': item.to_dict()
    }), 201


@app.route('/api/inventory/adjust', methods=['POST'])
def adjust_inventory():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 0)
    movement_type = data.get('type', 'adjust')
    
    item = Inventory.query.filter_by(product_id=product_id).first()
    if not item:
        return jsonify({'success': False, 'message': 'Không tìm thấy sản phẩm trong kho'}), 404
    
    if movement_type == 'in':
        item.quantity += quantity
    elif movement_type == 'out':
        if item.quantity < quantity:
            return jsonify({'success': False, 'message': 'Không đủ hàng trong kho'}), 400
        item.quantity -= quantity
    else:
        item.quantity = quantity
    
    movement = InventoryMovement(
        product_id=product_id,
        movement_type=movement_type,
        quantity=quantity,
        reference=data.get('reference'),
        note=data.get('note')
    )
    
    db.session.add(movement)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Điều chỉnh tồn kho thành công',
        'data': item.to_dict()
    }), 200


@app.route('/api/inventory/<int:product_id>', methods=['PUT'])
def update_inventory(product_id):
    item = Inventory.query.filter_by(product_id=product_id).first()
    if not item:
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    
    data = request.get_json()
    if 'min_quantity' in data:
        item.min_quantity = data['min_quantity']
    if 'max_quantity' in data:
        item.max_quantity = data['max_quantity']
    if 'location' in data:
        item.location = data['location']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Cập nhật thành công',
        'data': item.to_dict()
    }), 200


@app.route('/api/inventory/expiry-warnings', methods=['GET'])
def get_expiry_warnings():
    """Lấy cảnh báo sản phẩm sắp hết hạn
    Vì inventory_db không lưu expiry_date, cần gọi qua product_service
    Tạm thời trả về dữ liệu giả lập từ products có expiry_date
    """
    days = request.args.get('days', 30, type=int)
    
    # Thử lấy dữ liệu từ product_service
    try:
        import requests
        product_url = os.environ.get('PRODUCT_SERVICE_URL', 'http://localhost:5001')
        response = requests.get(f'{product_url}/api/products', timeout=5)
        if response.status_code == 200:
            products_data = response.json()
            products = products_data.get('data', [])
            
            from datetime import timedelta
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
            
            return jsonify({
                'success': True,
                'data': warnings,
                'count': len(warnings)
            }), 200
    except Exception as e:
        print(f"Error fetching products: {e}")
    
    # Fallback - trả về array rỗng
    return jsonify({
        'success': True,
        'data': [],
        'count': 0
    }), 200


@app.route('/api/inventory/movements', methods=['GET'])
def get_all_movements():
    """Lấy tất cả lịch sử nhập/xuất kho"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    movements = InventoryMovement.query.order_by(InventoryMovement.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': [m.to_dict() for m in movements.items],
        'count': movements.total,
        'pages': movements.pages,
        'current_page': page
    }), 200


@app.route('/api/inventory/movements/<int:product_id>', methods=['GET'])
def get_movements_by_product(product_id):
    """Lấy lịch sử nhập/xuất kho của một sản phẩm"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    movements = InventoryMovement.query.filter_by(product_id=product_id).order_by(
        InventoryMovement.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'success': True,
        'data': [m.to_dict() for m in movements.items],
        'count': movements.total,
        'pages': movements.pages,
        'current_page': page
    }), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    try:
        from shared.consul_utils import register_flask_service
        register_flask_service(app, 'inventory_service', 5002, ['inventory', 'stock'])
    except Exception as e:
        print(f"Warning: Could not register with Consul: {e}")
    
    db_type = 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    print("=" * 50)
    print(f"  Inventory Service running on port 5002")
    print(f"  Database: {db_type}")
    print("=" * 50)
    app.run(debug=True, port=5002, host='0.0.0.0')
