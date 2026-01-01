"""
Supplier Routes
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from flask import Blueprint, request, jsonify
from shared.utils import handle_exceptions, success_response, error_response
from shared.exceptions import SupplierNotFound, InvalidInput
from shared.database import db
from models.supplier_model import Supplier, PurchaseOrder, PurchaseOrderDetail
from datetime import datetime
from decimal import Decimal

supplier_bp = Blueprint('suppliers', __name__)

# ============ SUPPLIER MANAGEMENT ============

@supplier_bp.route('/', methods=['GET'])
@handle_exceptions
def get_all_suppliers():
    """Lấy danh sách nhà cung cấp"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    paginated = Supplier.query.filter_by(status='active').paginate(page=page, per_page=per_page)
    
    suppliers = [s.to_dict() for s in paginated.items]
    
    return success_response({
        'suppliers': suppliers,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }, message="Lấy danh sách nhà cung cấp thành công")

@supplier_bp.route('/<int:supplier_id>', methods=['GET'])
@handle_exceptions
def get_supplier(supplier_id):
    """Lấy chi tiết nhà cung cấp"""
    supplier = Supplier.query.get(supplier_id)
    
    if not supplier or supplier.status == 'deleted':
        raise SupplierNotFound()
    
    return success_response(supplier.to_dict(), message="Lấy chi tiết nhà cung cấp thành công")

@supplier_bp.route('/', methods=['POST'])
@handle_exceptions
def create_supplier():
    """Tạo nhà cung cấp mới"""
    data = request.get_json()
    
    required_fields = ['name', 'code']
    if not all(field in data for field in required_fields):
        raise InvalidInput(f"Thiếu các trường: {', '.join(required_fields)}")
    
    # Kiểm tra code trùng lặp
    if Supplier.query.filter_by(code=data['code']).first():
        raise InvalidInput(f"Mã nhà cung cấp {data['code']} đã tồn tại")
    
    supplier = Supplier(
        name=data['name'],
        code=data['code'],
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        city=data.get('city'),
        postal_code=data.get('postal_code'),
        contact_person=data.get('contact_person'),
        contact_phone=data.get('contact_phone'),
        bank_account=data.get('bank_account'),
        bank_name=data.get('bank_name'),
        payment_terms=data.get('payment_terms', 'NET30'),
        shipping_cost=data.get('shipping_cost', 0)
    )
    
    db.session.add(supplier)
    db.session.commit()
    
    return success_response(supplier.to_dict(), message="Tạo nhà cung cấp thành công", status_code=201)

@supplier_bp.route('/<int:supplier_id>', methods=['PUT'])
@handle_exceptions
def update_supplier(supplier_id):
    """Cập nhật nhà cung cấp"""
    supplier = Supplier.query.get(supplier_id)
    
    if not supplier or supplier.status == 'deleted':
        raise SupplierNotFound()
    
    data = request.get_json()
    
    # Cập nhật các trường
    if 'name' in data:
        supplier.name = data['name']
    if 'email' in data:
        supplier.email = data['email']
    if 'phone' in data:
        supplier.phone = data['phone']
    if 'address' in data:
        supplier.address = data['address']
    if 'city' in data:
        supplier.city = data['city']
    if 'contact_person' in data:
        supplier.contact_person = data['contact_person']
    if 'contact_phone' in data:
        supplier.contact_phone = data['contact_phone']
    if 'payment_terms' in data:
        supplier.payment_terms = data['payment_terms']
    if 'shipping_cost' in data:
        supplier.shipping_cost = data['shipping_cost']
    
    db.session.commit()
    
    return success_response(supplier.to_dict(), message="Cập nhật nhà cung cấp thành công")

@supplier_bp.route('/<int:supplier_id>', methods=['DELETE'])
@handle_exceptions
def delete_supplier(supplier_id):
    """Xóa nhà cung cấp"""
    supplier = Supplier.query.get(supplier_id)
    
    if not supplier:
        raise SupplierNotFound()
    
    supplier.status = 'deleted'
    db.session.commit()
    
    return success_response(None, message="Xóa nhà cung cấp thành công")

# ============ PURCHASE ORDER MANAGEMENT ============

@supplier_bp.route('/purchase-orders', methods=['GET'])
@handle_exceptions
def get_purchase_orders():
    """Lấy danh sách đơn nhập hàng"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    supplier_id = request.args.get('supplier_id', None, type=int)
    status = request.args.get('status', None)
    
    query = PurchaseOrder.query
    
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)
    
    if status:
        query = query.filter_by(status=status)
    
    paginated = query.order_by(PurchaseOrder.order_date.desc()).paginate(page=page, per_page=per_page)
    
    orders = [o.to_dict() for o in paginated.items]
    
    return success_response({
        'purchase_orders': orders,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }, message="Lấy danh sách đơn nhập hàng thành công")

@supplier_bp.route('/purchase-orders/<int:po_id>', methods=['GET'])
@handle_exceptions
def get_purchase_order(po_id):
    """Lấy chi tiết đơn nhập hàng"""
    po = PurchaseOrder.query.get(po_id)
    
    if not po:
        raise InvalidInput("Đơn nhập hàng không tìm thấy")
    
    po_data = po.to_dict()
    po_data['details'] = [d.to_dict() for d in po.details]
    
    return success_response(po_data, message="Lấy chi tiết đơn nhập hàng thành công")

@supplier_bp.route('/purchase-orders', methods=['POST'])
@handle_exceptions
def create_purchase_order():
    """Tạo đơn nhập hàng"""
    data = request.get_json()
    
    required_fields = ['po_number', 'supplier_id', 'items']
    if not all(field in data for field in required_fields):
        raise InvalidInput(f"Thiếu các trường: {', '.join(required_fields)}")
    
    # Kiểm tra PO số trùng lặp
    if PurchaseOrder.query.filter_by(po_number=data['po_number']).first():
        raise InvalidInput(f"Số đơn {data['po_number']} đã tồn tại")
    
    # Kiểm tra nhà cung cấp
    supplier = Supplier.query.get(data['supplier_id'])
    if not supplier:
        raise SupplierNotFound()
    
    # Tính tổng tiền
    subtotal = Decimal(0)
    
    po = PurchaseOrder(
        po_number=data['po_number'],
        supplier_id=data['supplier_id'],
        expected_delivery_date=datetime.fromisoformat(data['expected_delivery_date']) if data.get('expected_delivery_date') else None,
        shipping_cost=Decimal(data.get('shipping_cost', supplier.shipping_cost)),
        tax=Decimal(data.get('tax', 0)),
        notes=data.get('notes', '')
    )
    
    # Thêm chi tiết đơn
    for item in data['items']:
        if not all(field in item for field in ['product_id', 'ordered_quantity', 'unit_price']):
            raise InvalidInput("Thiếu thông tin sản phẩm")
        
        line_total = Decimal(item['ordered_quantity']) * Decimal(item['unit_price'])
        subtotal += line_total
        
        detail = PurchaseOrderDetail(
            product_id=item['product_id'],
            product_name=item.get('product_name', 'N/A'),
            sku=item.get('sku'),
            ordered_quantity=item['ordered_quantity'],
            received_quantity=0,
            unit_price=Decimal(item['unit_price']),
            expiry_date=datetime.fromisoformat(item['expiry_date']) if item.get('expiry_date') else None,
            batch_number=item.get('batch_number')
        )
        po.details.append(detail)
    
    po.subtotal = subtotal
    po.total_amount = subtotal + po.shipping_cost + po.tax
    
    db.session.add(po)
    db.session.commit()
    
    return success_response(po.to_dict(), message="Tạo đơn nhập hàng thành công", status_code=201)

@supplier_bp.route('/purchase-orders/<int:po_id>/receive', methods=['PUT'])
@handle_exceptions
def receive_purchase_order(po_id):
    """Nhận hàng từ đơn nhập"""
    po = PurchaseOrder.query.get(po_id)
    
    if not po:
        raise InvalidInput("Đơn nhập hàng không tìm thấy")
    
    data = request.get_json()
    
    # Cập nhật số lượng đã nhận
    for item_data in data.get('items', []):
        detail = PurchaseOrderDetail.query.get(item_data['id'])
        if detail:
            detail.received_quantity = item_data.get('received_quantity', 0)
    
    po.actual_delivery_date = datetime.utcnow()
    po.status = 'completed'
    
    db.session.commit()
    
    return success_response(po.to_dict(), message="Nhận hàng thành công")

@supplier_bp.route('/purchase-orders/<int:po_id>/pay', methods=['PUT'])
@handle_exceptions
def pay_purchase_order(po_id):
    """Thanh toán đơn nhập hàng"""
    po = PurchaseOrder.query.get(po_id)
    
    if not po:
        raise InvalidInput("Đơn nhập hàng không tìm thấy")
    
    data = request.get_json()
    
    po.paid_amount = Decimal(data.get('amount', 0))
    
    if po.paid_amount >= po.total_amount:
        po.payment_status = 'paid'
    elif po.paid_amount > 0:
        po.payment_status = 'partial'
    
    db.session.commit()
    
    return success_response(po.to_dict(), message="Thanh toán thành công")
