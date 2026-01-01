"""
Inventory Routes
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from flask import Blueprint, request, jsonify
from shared.utils import handle_exceptions, success_response, error_response
from shared.exceptions import InvalidInput, InsufficientStock, ExpiryDateWarning
from shared.database import db
from models.inventory_model import Inventory, InventoryMovement, ExpiryWarning
from datetime import datetime, timedelta

inventory_bp = Blueprint('inventory', __name__)

# ============ GET Methods ============

@inventory_bp.route('/by-product/<int:product_id>', methods=['GET'])
@handle_exceptions
def get_inventory_by_product(product_id):
    """Lấy tồn kho của sản phẩm"""
    inventory = Inventory.query.filter_by(product_id=product_id, status='active').first()
    
    if not inventory:
        return success_response({
            'product_id': product_id,
            'quantity_on_hand': 0,
            'quantity_reserved': 0,
            'quantity_available': 0
        }, message="Sản phẩm chưa có trong kho")
    
    return success_response(inventory.to_dict(), message="Lấy tồn kho thành công")

@inventory_bp.route('/all', methods=['GET'])
@handle_exceptions
def get_all_inventory():
    """Lấy danh sách tồn kho của tất cả sản phẩm"""
    inventories = Inventory.query.filter_by(status='active').all()
    items = [i.to_dict() for i in inventories]
    
    return success_response({
        'inventories': items,
        'total': len(items)
    }, message="Lấy danh sách tồn kho thành công")

@inventory_bp.route('/low-stock', methods=['GET'])
@handle_exceptions
def get_low_stock():
    """Lấy danh sách sản phẩm sắp hết"""
    low_stock = Inventory.query.filter(
        Inventory.status == 'active',
        Inventory.quantity_available <= Inventory.reorder_level
    ).all()
    
    items = [i.to_dict() for i in low_stock]
    
    return success_response({
        'low_stock_items': items,
        'total': len(items)
    }, message="Lấy danh sách sản phẩm sắp hết thành công")

@inventory_bp.route('/movements/<int:product_id>', methods=['GET'])
@handle_exceptions
def get_movements(product_id):
    """Lấy lịch sử nhập/xuất của sản phẩm"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    inventory = Inventory.query.filter_by(product_id=product_id).first()
    if not inventory:
        raise InvalidInput(f"Sản phẩm {product_id} không tồn tại")
    
    paginated = InventoryMovement.query.filter_by(inventory_id=inventory.id)\
        .order_by(InventoryMovement.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    movements = [m.to_dict() for m in paginated.items]
    
    return success_response({
        'movements': movements,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }, message="Lấy lịch sử nhập/xuất thành công")

@inventory_bp.route('/expiry-warnings', methods=['GET'])
@handle_exceptions
def get_expiry_warnings():
    """Lấy danh sách cảnh báo hạn sử dụng"""
    days = request.args.get('days', 30, type=int)
    future_date = datetime.utcnow() + timedelta(days=days)
    
    warnings = ExpiryWarning.query.filter(
        ExpiryWarning.status == 'active',
        ExpiryWarning.expiry_date <= future_date
    ).order_by(ExpiryWarning.expiry_date).all()
    
    items = [w.to_dict() for w in warnings]
    
    return success_response({
        'warnings': items,
        'total': len(items)
    }, message="Lấy cảnh báo hạn sử dụng thành công")

# ============ POST Methods ============

@inventory_bp.route('/init', methods=['POST'])
@handle_exceptions
def init_inventory():
    """Khởi tạo tồn kho cho sản phẩm mới"""
    data = request.get_json()
    
    required_fields = ['product_id']
    if not all(field in data for field in required_fields):
        raise InvalidInput("Thiếu product_id")
    
    # Kiểm tra đã tồn tại chưa
    existing = Inventory.query.filter_by(product_id=data['product_id']).first()
    if existing:
        raise InvalidInput(f"Sản phẩm {data['product_id']} đã có tồn kho")
    
    inventory = Inventory(
        product_id=data['product_id'],
        quantity_on_hand=data.get('quantity_on_hand', 0),
        quantity_available=data.get('quantity_on_hand', 0),
        reorder_level=data.get('reorder_level', 10),
        location=data.get('location', '')
    )
    
    db.session.add(inventory)
    db.session.commit()
    
    return success_response(inventory.to_dict(), message="Khởi tạo tồn kho thành công", status_code=201)

@inventory_bp.route('/adjust', methods=['POST'])
@handle_exceptions
def adjust_inventory():
    """Điều chỉnh tồn kho"""
    data = request.get_json()
    
    required_fields = ['product_id', 'quantity', 'reason']
    if not all(field in data for field in required_fields):
        raise InvalidInput(f"Thiếu các trường: {', '.join(required_fields)}")
    
    inventory = Inventory.query.filter_by(product_id=data['product_id']).first()
    if not inventory:
        raise InvalidInput(f"Sản phẩm {data['product_id']} không có tồn kho")
    
    # Cập nhật số lượng
    new_quantity = inventory.quantity_on_hand + data['quantity']
    if new_quantity < 0:
        raise InsufficientStock(f"Số lượng không được âm")
    
    inventory.quantity_on_hand = new_quantity
    inventory.quantity_available = new_quantity - inventory.quantity_reserved
    
    # Ghi lại movement
    movement = InventoryMovement(
        inventory_id=inventory.id,
        movement_type='ADJUST',
        quantity=data['quantity'],
        reference_type='Adjustment',
        notes=data.get('reason')
    )
    
    db.session.add(movement)
    db.session.commit()
    
    return success_response(inventory.to_dict(), message="Điều chỉnh tồn kho thành công")

@inventory_bp.route('/add-expiry-warning', methods=['POST'])
@handle_exceptions
def add_expiry_warning():
    """Thêm cảnh báo hạn sử dụng"""
    data = request.get_json()
    
    required_fields = ['product_id', 'expiry_date', 'quantity']
    if not all(field in data for field in required_fields):
        raise InvalidInput(f"Thiếu các trường bắt buộc")
    
    expiry_date = datetime.fromisoformat(data['expiry_date'])
    days_until_expiry = (expiry_date - datetime.utcnow()).days
    
    if days_until_expiry < 0:
        warning_level = 'critical'
    elif days_until_expiry < 7:
        warning_level = 'critical'
    else:
        warning_level = 'warning'
    
    warning = ExpiryWarning(
        product_id=data['product_id'],
        batch_number=data.get('batch_number'),
        expiry_date=expiry_date,
        quantity=data['quantity'],
        warning_level=warning_level
    )
    
    db.session.add(warning)
    db.session.commit()
    
    return success_response(warning.to_dict(), message="Thêm cảnh báo hạn sử dụng thành công", status_code=201)

# ============ PUT Methods ============

@inventory_bp.route('/<int:product_id>', methods=['PUT'])
@handle_exceptions
def update_inventory(product_id):
    """Cập nhật thông tin tồn kho"""
    inventory = Inventory.query.filter_by(product_id=product_id).first()
    
    if not inventory:
        raise InvalidInput(f"Sản phẩm {product_id} không có tồn kho")
    
    data = request.get_json()
    
    if 'reorder_level' in data:
        inventory.reorder_level = data['reorder_level']
    if 'location' in data:
        inventory.location = data['location']
    
    db.session.commit()
    
    return success_response(inventory.to_dict(), message="Cập nhật tồn kho thành công")
