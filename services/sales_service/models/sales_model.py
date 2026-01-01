"""
Sales Models
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from shared.database import db, TimestampMixin, StatusMixin
from datetime import datetime
from decimal import Decimal

class Invoice(db.Model, TimestampMixin, StatusMixin):
    """Model hóa đơn bán hàng"""
    __tablename__ = 'invoices'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    cashier_id = db.Column(db.Integer)  # ID nhân viên thu ngân
    customer_id = db.Column(db.Integer)  # ID khách hàng (nếu có)
    
    # Tiền tệ
    subtotal = db.Column(db.Numeric(12, 2), default=0)  # Tổng tiền hàng
    discount = db.Column(db.Numeric(12, 2), default=0)  # Chiết khấu
    tax = db.Column(db.Numeric(12, 2), default=0)  # Thuế (nếu có)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)  # Tổng tiền
    
    # Thanh toán
    payment_method = db.Column(db.String(50), default='cash')  # cash, card, mobile
    paid_amount = db.Column(db.Numeric(12, 2))  # Số tiền khách trả
    change_amount = db.Column(db.Numeric(12, 2), default=0)  # Tiền thối lại
    
    # Ghi chú
    notes = db.Column(db.Text)
    
    # Relationship
    details = db.relationship('InvoiceDetail', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'cashier_id': self.cashier_id,
            'customer_id': self.customer_id,
            'subtotal': float(self.subtotal),
            'discount': float(self.discount),
            'tax': float(self.tax),
            'total_amount': float(self.total_amount),
            'payment_method': self.payment_method,
            'paid_amount': float(self.paid_amount) if self.paid_amount else None,
            'change_amount': float(self.change_amount),
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class InvoiceDetail(db.Model, TimestampMixin):
    """Model chi tiết hóa đơn"""
    __tablename__ = 'invoice_details'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    
    # Sản phẩm
    product_name = db.Column(db.String(255), nullable=False)
    barcode = db.Column(db.String(100))
    sku = db.Column(db.String(50))
    
    # Số lượng và giá
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)  # quantity * unit_price
    
    def __repr__(self):
        return f'<InvoiceDetail Invoice:{self.invoice_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'barcode': self.barcode,
            'sku': self.sku,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'line_total': float(self.line_total),
            'created_at': self.created_at.isoformat()
        }
