"""
Supplier Models
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from shared.database import db, TimestampMixin, StatusMixin
from datetime import datetime
from decimal import Decimal

class Supplier(db.Model, TimestampMixin, StatusMixin):
    """Model nhà cung cấp"""
    __tablename__ = 'suppliers'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Thông tin liên hệ
    contact_person = db.Column(db.String(255))
    contact_phone = db.Column(db.String(20))
    
    # Thông tin thanh toán
    bank_account = db.Column(db.String(50))
    bank_name = db.Column(db.String(255))
    
    # Điều khoản
    payment_terms = db.Column(db.String(100))  # NET30, NET60, COD
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    
    # Relationship
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Supplier {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'bank_account': self.bank_account,
            'bank_name': self.bank_name,
            'payment_terms': self.payment_terms,
            'shipping_cost': float(self.shipping_cost),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PurchaseOrder(db.Model, TimestampMixin, StatusMixin):
    """Model đơn nhập hàng"""
    __tablename__ = 'purchase_orders'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # Ngày
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expected_delivery_date = db.Column(db.DateTime)
    actual_delivery_date = db.Column(db.DateTime)
    
    # Tiền tệ
    subtotal = db.Column(db.Numeric(12, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    tax = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Thanh toán
    paid_amount = db.Column(db.Numeric(12, 2), default=0)
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid
    
    # Ghi chú
    notes = db.Column(db.Text)
    
    # Relationship
    details = db.relationship('PurchaseOrderDetail', backref='purchase_order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PurchaseOrder {self.po_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'po_number': self.po_number,
            'supplier_id': self.supplier_id,
            'order_date': self.order_date.isoformat(),
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'subtotal': float(self.subtotal),
            'shipping_cost': float(self.shipping_cost),
            'tax': float(self.tax),
            'total_amount': float(self.total_amount),
            'paid_amount': float(self.paid_amount),
            'payment_status': self.payment_status,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class PurchaseOrderDetail(db.Model, TimestampMixin):
    """Model chi tiết đơn nhập hàng"""
    __tablename__ = 'purchase_order_details'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    
    # Sản phẩm
    product_name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(50))
    
    # Số lượng
    ordered_quantity = db.Column(db.Integer, nullable=False)
    received_quantity = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Hạn sử dụng
    expiry_date = db.Column(db.DateTime)
    batch_number = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<PurchaseOrderDetail PO:{self.purchase_order_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'purchase_order_id': self.purchase_order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'sku': self.sku,
            'ordered_quantity': self.ordered_quantity,
            'received_quantity': self.received_quantity,
            'unit_price': float(self.unit_price),
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'batch_number': self.batch_number,
            'created_at': self.created_at.isoformat()
        }
