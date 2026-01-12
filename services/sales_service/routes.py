"""
Sales Service - API Routes
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from sqlalchemy import func
from models import db, Invoice, InvoiceDetail
from utils import generate_invoice_number
import requests

sales_bp = Blueprint('sales', __name__)

# Service URLs
INVENTORY_SERVICE_URL = 'http://localhost:5002'
PRODUCT_SERVICE_URL = 'http://localhost:5001'



@sales_bp.route('/health', methods=['GET'])
def health_check():
    from flask import current_app
    return jsonify({
        'status': 'healthy',
        'service': 'sales_service',
        'port': 5003,
        'database': 'MySQL' if 'mysql' in current_app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@sales_bp.route('/api/sales/invoices', methods=['GET'])
def get_invoices():
    invoices = Invoice.query.order_by(Invoice.id.desc()).limit(100).all()
    return jsonify({'success': True, 'data': [i.to_dict() for i in invoices]}), 200


@sales_bp.route('/api/sales/invoices', methods=['POST'])
def create_invoice():
    data = request.get_json() or {}
    
    # Calculate subtotal from items
    items = data.get('items', [])
    subtotal = sum(item.get('line_total', item.get('quantity', 1) * item.get('unit_price', 0)) for item in items)
    discount = data.get('discount', 0)
    tax = data.get('tax', 0)
    total = subtotal - discount + tax
    
    # Use provided invoice_number or generate new one
    invoice_number = data.get('invoice_number') or generate_invoice_number()
    
    invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=data.get('customer_id'),
        customer_phone=data.get('customer_phone'),
        employee_id=data.get('employee_id'),
        subtotal=subtotal,
        discount=discount,
        tax=tax,
        total=total,
        payment_method=data.get('payment_method', 'cash'),
        status='completed',  # POS checkout = completed
        note=data.get('note'),
        completed_at=datetime.utcnow()
    )
    db.session.add(invoice)
    db.session.flush()  # Get invoice.id before adding items
    
    # Add invoice items
    for item in items:
        detail = InvoiceDetail(
            invoice_id=invoice.id,
            product_id=item.get('product_id'),
            product_name=item.get('product_name', 'Unknown'),
            quantity=item.get('quantity', 1),
            unit_price=item.get('unit_price', 0),
            total_price=item.get('line_total', item.get('quantity', 1) * item.get('unit_price', 0))
        )
        db.session.add(detail)
    
    db.session.commit()
    
    # Trừ số lượng trong Inventory và Product sau khi tạo hóa đơn thành công
    for item in items:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)
        
        # Trừ số lượng trong Inventory
        try:
            requests.post(f'{INVENTORY_SERVICE_URL}/api/inventory/deduct', json={
                'product_id': product_id,
                'quantity': quantity,
                'reference': invoice_number
            }, timeout=5)
        except Exception as e:
            print(f'Warning: Could not deduct inventory for product {product_id}: {e}')
        
        # Trừ số lượng trong Product
        try:
            requests.put(f'{PRODUCT_SERVICE_URL}/api/products/{product_id}/update-quantity', json={
                'operation': 'subtract',
                'quantity_change': quantity
            }, timeout=5)
        except Exception as e:
            print(f'Warning: Could not update product quantity for product {product_id}: {e}')
    
    return jsonify({
        'success': True,
        'message': 'Tạo hóa đơn thành công',
        'data': invoice.to_dict()
    }), 201


@sales_bp.route('/api/sales/invoices/<int:id>', methods=['GET'])
def get_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    return jsonify({'success': True, 'data': invoice.to_dict()}), 200


@sales_bp.route('/api/sales/invoices/<int:id>/add-item', methods=['POST'])
def add_item(id):
    invoice = Invoice.query.get_or_404(id)
    if invoice.status != 'pending':
        return jsonify({'success': False, 'message': 'Hóa đơn đã hoàn thành'}), 400
    
    data = request.get_json()
    item = InvoiceDetail(
        invoice_id=id,
        product_id=data.get('product_id'),
        product_name=data.get('product_name', 'Unknown'),
        quantity=data.get('quantity', 1),
        unit_price=data.get('unit_price', 0),
        total_price=data.get('quantity', 1) * data.get('unit_price', 0)
    )
    db.session.add(item)
    invoice.subtotal += item.total_price
    invoice.total = invoice.subtotal - invoice.discount + invoice.tax
    db.session.commit()
    
    return jsonify({'success': True, 'data': invoice.to_dict()}), 200


@sales_bp.route('/api/sales/invoices/<int:id>/checkout', methods=['PUT'])
def checkout(id):
    invoice = Invoice.query.get_or_404(id)
    if invoice.status != 'pending':
        return jsonify({'success': False, 'message': 'Hóa đơn đã xử lý'}), 400
    
    data = request.get_json() or {}
    invoice.payment_method = data.get('payment_method', 'cash')
    invoice.discount = data.get('discount', 0)
    invoice.total = invoice.subtotal - invoice.discount + invoice.tax
    invoice.status = 'completed'
    invoice.completed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Thanh toán thành công',
        'data': invoice.to_dict()
    }), 200


@sales_bp.route('/api/sales/revenue', methods=['GET'])
def get_revenue():
    from datetime import timedelta
    today = datetime.utcnow().date()
    
    # Today's revenue
    today_revenue = db.session.query(func.sum(Invoice.total)).filter(
        func.date(Invoice.completed_at) == today,
        Invoice.status == 'completed'
    ).scalar() or 0
    
    # Today's invoice count
    today_invoice_count = Invoice.query.filter(
        func.date(Invoice.completed_at) == today,
        Invoice.status == 'completed'
    ).count()
    
    # Monthly revenue (current month)
    first_day_of_month = today.replace(day=1)
    monthly_revenue = db.session.query(func.sum(Invoice.total)).filter(
        func.date(Invoice.completed_at) >= first_day_of_month,
        Invoice.status == 'completed'
    ).scalar() or 0
    
    # Total completed invoices (all time)
    total_invoices = Invoice.query.filter_by(status='completed').count()
    
    # 7-day revenue data for chart
    chart_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        day_revenue = db.session.query(func.sum(Invoice.total)).filter(
            func.date(Invoice.completed_at) == date,
            Invoice.status == 'completed'
        ).scalar() or 0
        chart_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(day_revenue)
        })
    
    return jsonify({
        'success': True,
        'data': {
            'today_revenue': float(today_revenue),
            'total_revenue': float(today_revenue),
            'monthly_revenue': float(monthly_revenue),
            'total_invoices': total_invoices,
            'invoice_count': today_invoice_count,
            'chart_data': chart_data
        }
    }), 200


@sales_bp.route('/api/sales/invoices/<int:id>', methods=['PUT'])
def update_invoice(id):
    """Update an invoice (for admin management)"""
    invoice = Invoice.query.get_or_404(id)
    data = request.get_json() or {}
    
    # Allow updating these fields
    if 'discount' in data:
        invoice.discount = data['discount']
        invoice.total = invoice.subtotal - invoice.discount + invoice.tax
    if 'payment_method' in data:
        invoice.payment_method = data['payment_method']
    if 'status' in data:
        invoice.status = data['status']
        if data['status'] == 'completed' and not invoice.completed_at:
            invoice.completed_at = datetime.utcnow()
    if 'note' in data:
        invoice.note = data['note']
    if 'customer_phone' in data:
        invoice.customer_phone = data['customer_phone']
    
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Cập nhật hóa đơn thành công',
        'data': invoice.to_dict()
    }), 200


@sales_bp.route('/api/sales/invoices/<int:id>', methods=['DELETE'])
def delete_invoice(id):
    """Delete an invoice (for admin management)"""
    invoice = Invoice.query.get_or_404(id)
    db.session.delete(invoice)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Xóa hóa đơn thành công'
    }), 200


@sales_bp.route('/api/sales/invoices/search', methods=['GET'])
def search_invoices():
    """Search and filter invoices"""
    query = Invoice.query
    
    # Filter by invoice_number
    invoice_number = request.args.get('invoice_number', '').strip()
    if invoice_number:
        query = query.filter(Invoice.invoice_number.ilike(f'%{invoice_number}%'))
    
    # Filter by date range
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    if from_date:
        query = query.filter(Invoice.created_at >= from_date)
    if to_date:
        query = query.filter(Invoice.created_at <= to_date + ' 23:59:59')
    
    # Filter by status
    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Invoice.status == status)
    
    # Filter by payment method
    payment_method = request.args.get('payment_method', '').strip()
    if payment_method:
        query = query.filter(Invoice.payment_method == payment_method)
    
    # Order by id desc (newest first)
    invoices = query.order_by(Invoice.id.desc()).limit(100).all()
    
    return jsonify({
        'success': True,
        'data': [i.to_dict() for i in invoices]
    }), 200


@sales_bp.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
