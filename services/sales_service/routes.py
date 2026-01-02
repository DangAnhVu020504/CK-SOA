"""
Sales Service - API Routes
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from sqlalchemy import func
from models import db, Invoice, InvoiceDetail
from utils import generate_invoice_number

sales_bp = Blueprint('sales', __name__)


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
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'data': [i.to_dict() for i in invoices]}), 200


@sales_bp.route('/api/sales/invoices', methods=['POST'])
def create_invoice():
    data = request.get_json() or {}
    invoice = Invoice(
        invoice_number=generate_invoice_number(),
        customer_id=data.get('customer_id'),
        customer_phone=data.get('customer_phone'),
        employee_id=data.get('employee_id'),
        note=data.get('note')
    )
    db.session.add(invoice)
    db.session.commit()
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
    today = datetime.utcnow().date()
    today_revenue = db.session.query(func.sum(Invoice.total)).filter(
        func.date(Invoice.completed_at) == today,
        Invoice.status == 'completed'
    ).scalar() or 0
    total_invoices = Invoice.query.filter_by(status='completed').count()
    return jsonify({
        'success': True,
        'data': {
            'today_revenue': today_revenue,
            'total_invoices': total_invoices
        }
    }), 200


@sales_bp.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
