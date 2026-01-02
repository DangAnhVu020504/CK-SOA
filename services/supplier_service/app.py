"""
Supplier Service - Quản lý nhà cung cấp
Port: 5004
Database: MySQL (supplier_db)
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

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supplier-service-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SUPPLIER_DB_URL',
    f'sqlite:///{current_dir}/supplier_service.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280, 'pool_pre_ping': True}

CORS(app)
db = SQLAlchemy(app)


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id, 'code': self.code, 'name': self.name,
            'contact_person': self.contact_person, 'phone': self.phone,
            'email': self.email, 'address': self.address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    total_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, approved, received, cancelled
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, partial, paid
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    received_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    
    supplier = db.relationship('Supplier', backref='orders')
    
    def to_dict(self):
        return {
            'id': self.id, 'order_number': self.order_number,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'total_amount': self.total_amount, 'status': self.status,
            'payment_status': self.payment_status,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 'service': 'supplier_service', 'port': 5004,
        'database': 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    suppliers = Supplier.query.filter_by(is_active=True).all()
    return jsonify({'success': True, 'data': [s.to_dict() for s in suppliers]}), 200


@app.route('/api/suppliers/<int:id>', methods=['GET'])
def get_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    return jsonify({'success': True, 'data': supplier.to_dict()}), 200


@app.route('/api/suppliers', methods=['POST'])
def create_supplier():
    data = request.get_json()
    if not data.get('name') or not data.get('code'):
        return jsonify({'success': False, 'message': 'Tên và mã là bắt buộc'}), 400
    
    supplier = Supplier(
        code=data['code'], name=data['name'],
        contact_person=data.get('contact_person'), phone=data.get('phone'),
        email=data.get('email'), address=data.get('address')
    )
    db.session.add(supplier)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Tạo thành công', 'data': supplier.to_dict()}), 201


@app.route('/api/suppliers/<int:id>', methods=['PUT'])
def update_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    data = request.get_json()
    for field in ['name', 'contact_person', 'phone', 'email', 'address']:
        if field in data:
            setattr(supplier, field, data[field])
    db.session.commit()
    return jsonify({'success': True, 'data': supplier.to_dict()}), 200


@app.route('/api/suppliers/<int:id>', methods=['DELETE'])
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    supplier.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Xóa thành công'}), 200


@app.route('/api/suppliers/purchase-orders', methods=['GET'])
def get_purchase_orders():
    orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'data': [o.to_dict() for o in orders]}), 200


@app.route('/api/suppliers/purchase-orders/<int:id>', methods=['GET'])
def get_purchase_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    return jsonify({'success': True, 'data': order.to_dict()}), 200


@app.route('/api/suppliers/purchase-orders', methods=['POST'])
def create_purchase_order():
    data = request.get_json()
    if not data.get('supplier_id'):
        return jsonify({'success': False, 'message': 'supplier_id là bắt buộc'}), 400
    
    order = PurchaseOrder(
        order_number=data.get('order_number') or f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        supplier_id=data['supplier_id'],
        total_amount=data.get('total_amount', 0),
        note=data.get('note'),
        status=data.get('status', 'pending'),
        payment_status=data.get('payment_status', 'unpaid')
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'success': True, 'data': order.to_dict()}), 201


@app.route('/api/suppliers/purchase-orders/<int:id>', methods=['PUT'])
def update_purchase_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    data = request.get_json()
    
    # Update regular fields
    for field in ['total_amount', 'note', 'status', 'payment_status']:
        if field in data:
            setattr(order, field, data[field])
    
    # Update timestamps based on status
    if data.get('status') == 'received' and not order.received_at:
        order.received_at = datetime.utcnow()
    if data.get('payment_status') == 'paid' and not order.paid_at:
        order.paid_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'success': True, 'data': order.to_dict()}), 200


@app.route('/api/suppliers/purchase-orders/<int:id>', methods=['DELETE'])
def delete_purchase_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Xóa thành công'}), 200


@app.route('/api/suppliers/purchase-orders/<int:id>/receive', methods=['PUT'])
def receive_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    order.status = 'received'
    order.received_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'data': order.to_dict()}), 200


@app.route('/api/suppliers/purchase-orders/<int:id>/pay', methods=['PUT'])
def pay_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    order.payment_status = 'paid'
    order.paid_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'data': order.to_dict()}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    try:
        from shared.consul_utils import register_flask_service
        register_flask_service(app, 'supplier_service', 5004, ['supplier', 'purchase'])
    except Exception as e:
        print(f"Warning: Could not register with Consul: {e}")
    
    db_type = 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    print("=" * 50)
    print(f"  Supplier Service running on port 5004")
    print(f"  Database: {db_type}")
    print("=" * 50)
    app.run(debug=True, port=5004, host='0.0.0.0')
