"""
Product Model
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from shared.database import db, TimestampMixin, StatusMixin
from decimal import Decimal

class Product(db.Model, TimestampMixin, StatusMixin):
    """Model sản phẩm"""
    __tablename__ = 'products'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)  # Mã SKU
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost = db.Column(db.Numeric(10, 2))  # Giá vốn
    barcode = db.Column(db.String(100), unique=True, nullable=False)
    unit = db.Column(db.String(50), default='cái')  # Đơn vị tính
    supplier_id = db.Column(db.Integer)  # ID nhà cung cấp
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': float(self.price),
            'cost': float(self.cost) if self.cost else None,
            'barcode': self.barcode,
            'unit': self.unit,
            'supplier_id': self.supplier_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
