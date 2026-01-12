"""
Product Service - Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    barcode = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    unit = db.Column(db.String(20), default='cái')
    cost_price = db.Column(db.Float, default=0)
    selling_price = db.Column(db.Float, default=0)
    quantity = db.Column(db.Integer, default=0)  # Số lượng tồn kho
    supplier_id = db.Column(db.Integer, nullable=True)
    manufacturing_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ngưỡng cảnh báo sắp hết hàng (mặc định 50)
    LOW_STOCK_THRESHOLD = 50
    
    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'barcode': self.barcode,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'unit': self.unit,
            'cost_price': self.cost_price,
            'selling_price': self.selling_price,
            'quantity': self.quantity,
            'supplier_id': self.supplier_id,
            'manufacturing_date': self.manufacturing_date.isoformat() if self.manufacturing_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_active': self.is_active,
            'is_low_stock': self.quantity <= self.LOW_STOCK_THRESHOLD and self.quantity > 0,
            'is_out_of_stock': self.quantity <= 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
