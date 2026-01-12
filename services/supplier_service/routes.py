"""
Supplier Service - API Routes
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, date
from models import db, Supplier, PurchaseOrder, PurchaseOrderDetail
from utils import generate_order_number, parse_date
import requests

supplier_bp = Blueprint('supplier', __name__)

# Service URLs
INVENTORY_SERVICE_URL = 'http://localhost:5002'
PRODUCT_SERVICE_URL = 'http://localhost:5001'


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
    
    # Parse import_date if provided
    import_date = None
    if data.get('import_date'):
        try:
            import_date = datetime.strptime(data['import_date'], '%Y-%m-%d').date()
        except:
            import_date = date.today()
    
    # Calculate total from items if provided
    items = data.get('items', [])
    total_amount = data.get('total_amount', 0)
    if items and total_amount == 0:
        total_amount = sum(item.get('total_price', item.get('quantity', 1) * item.get('unit_price', 0)) for item in items)
    
    order = PurchaseOrder(
        order_number=data.get('order_number') or generate_order_number(),
        supplier_id=data['supplier_id'],
        total_amount=total_amount,
        note=data.get('note'),
        import_date=import_date,
        status=data.get('status', 'pending'),
        payment_status=data.get('payment_status', 'unpaid')
    )
    db.session.add(order)
    db.session.flush()  # Get order.id before adding items
    
    # Add order items
    for item in items:
        detail = PurchaseOrderDetail(
            order_id=order.id,
            product_id=item.get('product_id'),
            product_name=item.get('product_name', 'Unknown'),
            quantity=item.get('quantity', 1),
            unit_price=item.get('unit_price', 0),
            total_price=item.get('total_price', item.get('quantity', 1) * item.get('unit_price', 0))
        )
        db.session.add(detail)
    
    db.session.commit()
    return jsonify({'success': True, 'data': order.to_dict()}), 201


@supplier_bp.route('/api/suppliers/purchase-orders/<int:id>', methods=['PUT'])
def update_purchase_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    data = request.get_json()
    
    # Lưu status cũ để kiểm tra
    old_status = order.status
    
    # Update regular fields
    for field in ['total_amount', 'note', 'status', 'payment_status']:
        if field in data:
            setattr(order, field, data[field])
    
    # Update timestamps based on status
    if data.get('status') == 'received' and not order.received_at:
        order.received_at = datetime.utcnow()
        
        # Nếu chuyển sang "received" và trước đó chưa received, cộng số lượng vào kho
        if old_status != 'received':
            for item in order.items:
                product_id = item.product_id
                quantity = item.quantity
                
                # Cộng số lượng vào Inventory
                try:
                    requests.post(f'{INVENTORY_SERVICE_URL}/api/inventory/adjust', json={
                        'product_id': product_id,
                        'quantity': quantity,
                        'type': 'in',
                        'reference': order.order_number,
                        'note': f'Nhập hàng - Đơn {order.order_number}'
                    }, timeout=5)
                except Exception as e:
                    print(f'Warning: Could not add inventory for product {product_id}: {e}')
                
                # Cộng số lượng vào Product
                try:
                    requests.put(f'{PRODUCT_SERVICE_URL}/api/products/{product_id}/update-quantity', json={
                        'operation': 'add',
                        'quantity_change': quantity
                    }, timeout=5)
                except Exception as e:
                    print(f'Warning: Could not update product quantity for product {product_id}: {e}')
                
                # Cập nhật received_quantity
                item.received_quantity = quantity
    
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
    """Nhận hàng - cộng số lượng vào Inventory và Product"""
    order = PurchaseOrder.query.get_or_404(id)
    order.status = 'received'
    order.received_at = datetime.utcnow()
    
    # Cộng số lượng vào Inventory và Product cho từng sản phẩm
    for item in order.items:
        product_id = item.product_id
        quantity = item.quantity
        
        # Cộng số lượng vào Inventory
        try:
            requests.post(f'{INVENTORY_SERVICE_URL}/api/inventory/adjust', json={
                'product_id': product_id,
                'quantity': quantity,
                'type': 'in',
                'reference': order.order_number,
                'note': f'Nhập hàng - Đơn {order.order_number}'
            }, timeout=5)
        except Exception as e:
            print(f'Warning: Could not add inventory for product {product_id}: {e}')
        
        # Cộng số lượng vào Product
        try:
            requests.put(f'{PRODUCT_SERVICE_URL}/api/products/{product_id}/update-quantity', json={
                'operation': 'add',
                'quantity_change': quantity
            }, timeout=5)
        except Exception as e:
            print(f'Warning: Could not update product quantity for product {product_id}: {e}')
        
        # Cập nhật received_quantity
        item.received_quantity = quantity
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Nhận hàng thành công', 'data': order.to_dict()}), 200


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
