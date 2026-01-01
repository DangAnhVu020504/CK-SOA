"""
Inventory Models
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from shared.database import db, TimestampMixin, StatusMixin
from datetime import datetime

class Inventory(db.Model, TimestampMixin, StatusMixin):
    """Model tồn kho"""
    __tablename__ = 'inventories'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, nullable=False)  # Tham chiếu đến Product Service
    quantity_on_hand = db.Column(db.Integer, default=0)  # Số lượng hiện có
    quantity_reserved = db.Column(db.Integer, default=0)  # Số lượng đã đặt
    quantity_available = db.Column(db.Integer, default=0)  # Số lượng có thể bán
    reorder_level = db.Column(db.Integer, default=10)  # Mức tái đặt hàng
    location = db.Column(db.String(100))  # Vị trí trong kho
    
    def __repr__(self):
        return f'<Inventory Product:{self.product_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity_on_hand': self.quantity_on_hand,
            'quantity_reserved': self.quantity_reserved,
            'quantity_available': self.quantity_available,
            'reorder_level': self.reorder_level,
            'location': self.location,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class InventoryMovement(db.Model, TimestampMixin):
    """Model theo dõi nhập/xuất kho"""
    __tablename__ = 'inventory_movements'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # IN (nhập), OUT (xuất), ADJUST (điều chỉnh)
    quantity = db.Column(db.Integer, nullable=False)
    reference_id = db.Column(db.String(100))  # ID của PO hoặc Invoice
    reference_type = db.Column(db.String(50))  # PurchaseOrder, Sale, Adjustment
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer)  # ID nhân viên thực hiện
    
    def __repr__(self):
        return f'<InventoryMovement {self.movement_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'inventory_id': self.inventory_id,
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'reference_id': self.reference_id,
            'reference_type': self.reference_type,
            'notes': self.notes,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }

class ExpiryWarning(db.Model, TimestampMixin, StatusMixin):
    """Model cảnh báo hạn sử dụng"""
    __tablename__ = 'expiry_warnings'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, nullable=False)
    batch_number = db.Column(db.String(100))
    expiry_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer)
    warning_level = db.Column(db.String(20))  # critical (< 7 ngày), warning (7-30 ngày)
    warning_sent = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ExpiryWarning Product:{self.product_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'batch_number': self.batch_number,
            'expiry_date': self.expiry_date.isoformat(),
            'quantity': self.quantity,
            'warning_level': self.warning_level,
            'warning_sent': self.warning_sent,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
