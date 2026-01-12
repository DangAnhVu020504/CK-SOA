"""
Inventory Service - API Routes
"""
from flask import Blueprint, jsonify, request
from models import db, Inventory, InventoryMovement
from utils import get_expiry_warnings

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/health', methods=['GET'])
def health_check():
    from flask import current_app
    return jsonify({
        'status': 'healthy',
        'service': 'inventory_service',
        'port': 5002,
        'database': 'MySQL' if 'mysql' in current_app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@inventory_bp.route('/api/inventory/all', methods=['GET'])
def get_all_inventory():
    items = Inventory.query.all()
    return jsonify({
        'success': True,
        'data': [i.to_dict() for i in items],
        'count': len(items)
    }), 200


@inventory_bp.route('/api/inventory/by-product/<int:product_id>', methods=['GET'])
def get_by_product(product_id):
    item = Inventory.query.filter_by(product_id=product_id).first()
    if not item:
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    return jsonify({'success': True, 'data': item.to_dict()}), 200


@inventory_bp.route('/api/inventory/low-stock', methods=['GET'])
def get_low_stock():
    """Lấy sản phẩm sắp hết hàng (quantity <= 50 hoặc <= min_quantity)"""
    threshold = request.args.get('threshold', 50, type=int)
    items = Inventory.query.filter(
        db.or_(
            Inventory.quantity <= Inventory.min_quantity,
            Inventory.quantity <= threshold
        ),
        Inventory.quantity > 0
    ).all()
    return jsonify({
        'success': True,
        'data': [i.to_dict() for i in items],
        'count': len(items)
    }), 200


@inventory_bp.route('/api/inventory/out-of-stock', methods=['GET'])
def get_out_of_stock():
    """Lấy sản phẩm hết hàng (quantity = 0)"""
    items = Inventory.query.filter(Inventory.quantity <= 0).all()
    return jsonify({
        'success': True,
        'data': [i.to_dict() for i in items],
        'count': len(items)
    }), 200


@inventory_bp.route('/api/inventory/deduct', methods=['POST'])
def deduct_inventory():
    """Trừ số lượng khi bán hàng - được gọi từ sales_service"""
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 0)
    reference = data.get('reference')  # Số hóa đơn
    
    if not product_id or quantity <= 0:
        return jsonify({'success': False, 'message': 'product_id và quantity là bắt buộc'}), 400
    
    item = Inventory.query.filter_by(product_id=product_id).first()
    if not item:
        return jsonify({'success': False, 'message': 'Không tìm thấy sản phẩm trong kho'}), 404
    
    if item.quantity < quantity:
        return jsonify({'success': False, 'message': 'Không đủ hàng trong kho'}), 400
    
    item.quantity -= quantity
    
    # Ghi lại lịch sử xuất kho
    movement = InventoryMovement(
        product_id=product_id,
        movement_type='out',
        quantity=quantity,
        reference=reference,
        note=f'Bán hàng - Hóa đơn {reference}'
    )
    
    db.session.add(movement)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Trừ tồn kho thành công',
        'data': item.to_dict()
    }), 200


@inventory_bp.route('/api/inventory/init', methods=['POST'])
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


@inventory_bp.route('/api/inventory/adjust', methods=['POST'])
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


@inventory_bp.route('/api/inventory/<int:product_id>', methods=['PUT'])
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


@inventory_bp.route('/api/inventory/expiry-warnings', methods=['GET'])
def get_expiry_warnings_route():
    """Lấy cảnh báo sản phẩm sắp hết hạn"""
    days = request.args.get('days', 30, type=int)
    warnings = get_expiry_warnings(days)
    
    return jsonify({
        'success': True,
        'data': warnings,
        'count': len(warnings)
    }), 200


@inventory_bp.route('/api/inventory/movements', methods=['GET'])
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


@inventory_bp.route('/api/inventory/movements/<int:product_id>', methods=['GET'])
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


@inventory_bp.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
