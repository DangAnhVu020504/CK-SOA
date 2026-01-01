"""
Sales Routes
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from flask import Blueprint, request, jsonify
from shared.utils import handle_exceptions, success_response, error_response
from shared.exceptions import InvalidInput, ProductNotFound
from shared.database import db
from models.sales_model import Invoice, InvoiceDetail
from datetime import datetime
from decimal import Decimal
import requests

sales_bp = Blueprint('sales', __name__)

# Configuration
PRODUCT_SERVICE_URL = 'http://localhost:5001'
INVENTORY_SERVICE_URL = 'http://localhost:5002'

# ============ GET Methods ============

@sales_bp.route('/invoices', methods=['GET'])
@handle_exceptions
def get_invoices():
    """Lấy danh sách hóa đơn"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', None)
    
    query = Invoice.query
    
    if status:
        query = query.filter_by(status=status)
    
    paginated = query.order_by(Invoice.created_at.desc()).paginate(page=page, per_page=per_page)
    
    invoices = [i.to_dict() for i in paginated.items]
    
    return success_response({
        'invoices': invoices,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }, message="Lấy danh sách hóa đơn thành công")

@sales_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@handle_exceptions
def get_invoice(invoice_id):
    """Lấy chi tiết hóa đơn"""
    invoice = Invoice.query.get(invoice_id)
    
    if not invoice:
        raise ProductNotFound("Hóa đơn không tìm thấy")
    
    invoice_data = invoice.to_dict()
    invoice_data['details'] = [d.to_dict() for d in invoice.details]
    
    return success_response(invoice_data, message="Lấy chi tiết hóa đơn thành công")

@sales_bp.route('/invoices/by-number/<invoice_number>', methods=['GET'])
@handle_exceptions
def get_invoice_by_number(invoice_number):
    """Lấy hóa đơn theo số"""
    invoice = Invoice.query.filter_by(invoice_number=invoice_number).first()
    
    if not invoice:
        raise ProductNotFound(f"Hóa đơn {invoice_number} không tìm thấy")
    
    invoice_data = invoice.to_dict()
    invoice_data['details'] = [d.to_dict() for d in invoice.details]
    
    return success_response(invoice_data, message="Lấy hóa đơn thành công")

@sales_bp.route('/revenue', methods=['GET'])
@handle_exceptions
def get_revenue():
    """Thống kê doanh thu"""
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    
    query = Invoice.query.filter_by(status='active')
    
    if start_date:
        start_date_obj = datetime.fromisoformat(start_date)
        query = query.filter(Invoice.created_at >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.fromisoformat(end_date)
        query = query.filter(Invoice.created_at <= end_date_obj)
    
    invoices = query.all()
    
    total_revenue = sum(float(i.total_amount) for i in invoices)
    total_discount = sum(float(i.discount) for i in invoices)
    invoice_count = len(invoices)
    
    return success_response({
        'total_revenue': total_revenue,
        'total_discount': total_discount,
        'invoice_count': invoice_count,
        'average_invoice': total_revenue / invoice_count if invoice_count > 0 else 0
    }, message="Lấy thống kê doanh thu thành công")

# ============ POST Methods ============

@sales_bp.route('/invoices', methods=['POST'])
@handle_exceptions
def create_invoice():
    """Tạo hóa đơn mới"""
    data = request.get_json()
    
    required_fields = ['invoice_number', 'items']
    if not all(field in data for field in required_fields):
        raise InvalidInput(f"Thiếu các trường bắt buộc: {', '.join(required_fields)}")
    
    # Kiểm tra số hóa đơn trùng lặp
    if Invoice.query.filter_by(invoice_number=data['invoice_number']).first():
        raise InvalidInput(f"Số hóa đơn {data['invoice_number']} đã tồn tại")
    
    # Tính tổng tiền
    subtotal = Decimal(0)
    discount = Decimal(data.get('discount', 0))
    
    # Tạo hóa đơn
    invoice = Invoice(
        invoice_number=data['invoice_number'],
        cashier_id=data.get('cashier_id'),
        customer_id=data.get('customer_id'),
        discount=discount,
        payment_method=data.get('payment_method', 'cash'),
        notes=data.get('notes', '')
    )
    
    # Thêm chi tiết hóa đơn
    for item in data['items']:
        if not all(field in item for field in ['product_id', 'quantity', 'unit_price']):
            raise InvalidInput("Thiếu thông tin sản phẩm")
        
        line_total = Decimal(item['quantity']) * Decimal(item['unit_price'])
        subtotal += line_total
        
        detail = InvoiceDetail(
            product_id=item['product_id'],
            product_name=item.get('product_name', 'N/A'),
            barcode=item.get('barcode'),
            sku=item.get('sku'),
            quantity=item['quantity'],
            unit_price=Decimal(item['unit_price']),
            line_total=line_total
        )
        invoice.details.append(detail)
    
    invoice.subtotal = subtotal
    invoice.total_amount = subtotal - discount
    invoice.paid_amount = data.get('paid_amount')
    
    if invoice.paid_amount:
        invoice.change_amount = Decimal(invoice.paid_amount) - invoice.total_amount
    
    db.session.add(invoice)
    db.session.commit()
    
    return success_response(invoice.to_dict(), message="Tạo hóa đơn thành công", status_code=201)

@sales_bp.route('/invoices/<int:invoice_id>/add-item', methods=['POST'])
@handle_exceptions
def add_item_to_invoice(invoice_id):
    """Thêm sản phẩm vào hóa đơn"""
    invoice = Invoice.query.get(invoice_id)
    
    if not invoice:
        raise ProductNotFound("Hóa đơn không tìm thấy")
    
    if invoice.status != 'active':
        raise InvalidInput("Hóa đơn này đã hoàn thành, không thể thêm sản phẩm")
    
    data = request.get_json()
    
    required_fields = ['product_id', 'quantity', 'unit_price']
    if not all(field in data for field in required_fields):
        raise InvalidInput("Thiếu thông tin sản phẩm")
    
    line_total = Decimal(data['quantity']) * Decimal(data['unit_price'])
    
    detail = InvoiceDetail(
        product_id=data['product_id'],
        product_name=data.get('product_name', 'N/A'),
        barcode=data.get('barcode'),
        sku=data.get('sku'),
        quantity=data['quantity'],
        unit_price=Decimal(data['unit_price']),
        line_total=line_total
    )
    
    invoice.details.append(detail)
    
    # Tính lại tổng tiền
    invoice.subtotal = sum(Decimal(d.line_total) for d in invoice.details)
    invoice.total_amount = invoice.subtotal - invoice.discount
    
    db.session.commit()
    
    return success_response(invoice.to_dict(), message="Thêm sản phẩm vào hóa đơn thành công")

# ============ PUT Methods ============

@sales_bp.route('/invoices/<int:invoice_id>/checkout', methods=['PUT'])
@handle_exceptions
def checkout_invoice(invoice_id):
    """Hoàn thành hóa đơn"""
    invoice = Invoice.query.get(invoice_id)
    
    if not invoice:
        raise ProductNotFound("Hóa đơn không tìm thấy")
    
    data = request.get_json()
    
    invoice.paid_amount = data.get('paid_amount', invoice.total_amount)
    invoice.change_amount = Decimal(invoice.paid_amount) - invoice.total_amount
    invoice.payment_method = data.get('payment_method', invoice.payment_method)
    invoice.status = 'completed'
    
    db.session.commit()
    
    return success_response(invoice.to_dict(), message="Hoàn thành hóa đơn thành công")

# ============ DELETE Methods ============

@sales_bp.route('/invoices/<int:invoice_id>', methods=['DELETE'])
@handle_exceptions
def cancel_invoice(invoice_id):
    """Hủy hóa đơn"""
    invoice = Invoice.query.get(invoice_id)
    
    if not invoice:
        raise ProductNotFound("Hóa đơn không tìm thấy")
    
    invoice.status = 'cancelled'
    db.session.commit()
    
    return success_response(None, message="Hủy hóa đơn thành công")
