"""
Sales Service - Quản lý bán hàng POS
Port: 5003
Database: MySQL (sales_db)
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
import random
import string

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sales-service-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SALES_DB_URL',
    f'sqlite:///{current_dir}/sales_service.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280, 'pool_pre_ping': True}

CORS(app)
db = SQLAlchemy(app)


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer)
    customer_phone = db.Column(db.String(20))
    employee_id = db.Column(db.Integer)
    subtotal = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    payment_method = db.Column(db.String(50), default='cash')
    status = db.Column(db.String(20), default='pending')
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    items = db.relationship('InvoiceDetail', backref='invoice', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customer_id': self.customer_id,
            'customer_phone': self.customer_phone,
            'subtotal': self.subtotal,
            'discount': self.discount,
            'total': self.total,
            'payment_method': self.payment_method,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [i.to_dict() for i in self.items]
        }


class InvoiceDetail(db.Model):
    __tablename__ = 'invoice_details'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(200))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0)
    total_price = db.Column(db.Float, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price
        }


def generate_invoice_number():
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'sales_service',
        'port': 5003,
        'database': 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@app.route('/api/sales/invoices', methods=['GET'])
def get_invoices():
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'data': [i.to_dict() for i in invoices]}), 200


@app.route('/api/sales/invoices', methods=['POST'])
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
    return jsonify({'success': True, 'message': 'Tạo hóa đơn thành công', 'data': invoice.to_dict()}), 201


@app.route('/api/sales/invoices/<int:id>', methods=['GET'])
def get_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    return jsonify({'success': True, 'data': invoice.to_dict()}), 200


@app.route('/api/sales/invoices/<int:id>/add-item', methods=['POST'])
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


@app.route('/api/sales/invoices/<int:id>/checkout', methods=['PUT'])
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
    
    return jsonify({'success': True, 'message': 'Thanh toán thành công', 'data': invoice.to_dict()}), 200


@app.route('/api/sales/revenue', methods=['GET'])
def get_revenue():
    from sqlalchemy import func
    today = datetime.utcnow().date()
    today_revenue = db.session.query(func.sum(Invoice.total)).filter(
        func.date(Invoice.completed_at) == today,
        Invoice.status == 'completed'
    ).scalar() or 0
    total_invoices = Invoice.query.filter_by(status='completed').count()
    return jsonify({'success': True, 'data': {'today_revenue': today_revenue, 'total_invoices': total_invoices}}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    try:
        from shared.consul_utils import register_flask_service
        register_flask_service(app, 'sales_service', 5003, ['sales', 'pos'])
    except Exception as e:
        print(f"Warning: Could not register with Consul: {e}")
    
    db_type = 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    print("=" * 50)
    print(f"  Sales Service running on port 5003")
    print(f"  Database: {db_type}")
    print("=" * 50)
    app.run(debug=True, port=5003, host='0.0.0.0')
