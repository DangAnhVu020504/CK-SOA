"""
Supplier Service - Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    total_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, approved, received, cancelled
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, partial, paid
    note = db.Column(db.Text)
    import_date = db.Column(db.Date, nullable=True)  # Ngày nhập hàng
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    received_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    
    supplier = db.relationship('Supplier', backref='orders')
    items = db.relationship('PurchaseOrderDetail', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'total_amount': self.total_amount,
            'status': self.status,
            'payment_status': self.payment_status,
            'note': self.note,
            'import_date': self.import_date.isoformat() if self.import_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class PurchaseOrderDetail(db.Model):
    """Chi tiết sản phẩm trong đơn nhập hàng"""
    __tablename__ = 'purchase_order_details'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(200))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0)
    total_price = db.Column(db.Float, default=0)
    received_quantity = db.Column(db.Integer, default=0)  # Số lượng đã nhận
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'received_quantity': self.received_quantity
        }

