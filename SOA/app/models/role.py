# Role Model
from datetime import datetime
from app.extensions import db


class Role(db.Model):
    """Role model for user authorization"""
    
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    permissions = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with users
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    # Default role constants
    ADMIN = 'admin'
    MANAGER = 'manager'
    STAFF = 'staff'
    CUSTOMER = 'customer'
    
    def __init__(self, name, description=None, permissions=None):
        self.name = name
        self.description = description
        self.permissions = permissions or []
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        """Convert role to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def has_permission(self, permission):
        """Check if role has a specific permission"""
        if 'all' in self.permissions:
            return True
        return permission in self.permissions
    
    @staticmethod
    def get_default_roles():
        """Get default roles configuration"""
        return [
            {
                'name': Role.ADMIN,
                'description': 'Quản trị viên hệ thống - Toàn quyền',
                'permissions': ['all']
            },
            {
                'name': Role.MANAGER,
                'description': 'Quản lý cửa hàng - Quản lý nhân viên và hàng hóa',
                'permissions': ['read', 'write', 'manage_staff', 'manage_products', 'view_reports']
            },
            {
                'name': Role.STAFF,
                'description': 'Nhân viên bán hàng',
                'permissions': ['read', 'write', 'sell_products']
            },
            {
                'name': Role.CUSTOMER,
                'description': 'Khách hàng',
                'permissions': ['read', 'view_products', 'purchase']
            }
        ]
