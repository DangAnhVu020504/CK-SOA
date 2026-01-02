"""
Supplier Service - API Routes
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from models import db, Supplier, PurchaseOrder
from utils import generate_order_number

supplier_bp = Blueprint('supplier', __name__)


@supplier_bp.route('/health', methods=['GET'])
def health_check():
    from flask import current_app
    return jsonify({
        'status': 'healthy',
        'service': 'supplier_service',
        'port': 5004,
        'database': 'MySQL' if 'mysql' in current_app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


# ============ SUPPLIER ROUTES ============

@supplier_bp.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    suppliers = Supplier.query.filter_by(is_active=True).all()
    return jsonify({'success': True, 'data': [s.to_dict() for s in suppliers]}), 200


@supplier_bp.route('/api/suppliers/<int:id>', methods=['GET'])
def get_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    return jsonify({'success': True, 'data': supplier.to_dict()}), 200


@supplier_bp.route('/api/suppliers', methods=['POST'])
def create_supplier():
    data = request.get_json()
    if not data.get('name') or not data.get('code'):
        return jsonify({'success': False, 'message': 'Tên và mã là bắt buộc'}), 400
    
    supplier = Supplier(
        code=data['code'],
        name=data['name'],
        contact_person=data.get('contact_person'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address')
    )
    db.session.add(supplier)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Tạo thành công', 'data': supplier.to_dict()}), 201


@supplier_bp.route('/api/suppliers/<int:id>', methods=['PUT'])
def update_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    data = request.get_json()
    for field in ['name', 'contact_person', 'phone', 'email', 'address']:
        if field in data:
            setattr(supplier, field, data[field])
    db.session.commit()
    return jsonify({'success': True, 'data': supplier.to_dict()}), 200


@supplier_bp.route('/api/suppliers/<int:id>', methods=['DELETE'])
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    supplier.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Xóa thành công'}), 200


# ============ PURCHASE ORDER ROUTES ============

@supplier_bp.route('/api/suppliers/purchase-orders', methods=['GET'])
def get_purchase_orders():
    orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'data': [o.to_dict() for o in orders]}), 200


@supplier_bp.route('/api/suppliers/purchase-orders/<int:id>', methods=['GET'])
def get_purchase_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    return jsonify({'success': True, 'data': order.to_dict()}), 200


@supplier_bp.route('/api/suppliers/purchase-orders', methods=['POST'])
def create_purchase_order():
    data = request.get_json()
    if not data.get('supplier_id'):
        return jsonify({'success': False, 'message': 'supplier_id là bắt buộc'}), 400
    
    order = PurchaseOrder(
        order_number=data.get('order_number') or generate_order_number(),
        supplier_id=data['supplier_id'],
        total_amount=data.get('total_amount', 0),
        note=data.get('note'),
        status=data.get('status', 'pending'),
        payment_status=data.get('payment_status', 'unpaid')
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'success': True, 'data': order.to_dict()}), 201


@supplier_bp.route('/api/suppliers/purchase-orders/<int:id>', methods=['PUT'])
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


@supplier_bp.route('/api/suppliers/purchase-orders/<int:id>', methods=['DELETE'])
def delete_purchase_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Xóa thành công'}), 200


@supplier_bp.route('/api/suppliers/purchase-orders/<int:id>/receive', methods=['PUT'])
def receive_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    order.status = 'received'
    order.received_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'data': order.to_dict()}), 200


@supplier_bp.route('/api/suppliers/purchase-orders/<int:id>/pay', methods=['PUT'])
def pay_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    order.payment_status = 'paid'
    order.paid_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'data': order.to_dict()}), 200


@supplier_bp.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
