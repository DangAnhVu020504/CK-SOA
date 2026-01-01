# User Model
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """User model for authentication and authorization"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, username, email, password, role_id, full_name=None, phone=None, address=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role_id = role_id
        self.full_name = full_name
        self.phone = phone
        self.address = address
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set the user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the password against the hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_role=True):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'address': self.address,
            'is_active': self.is_active,
            'role_id': self.role_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_role and self.role:
            data['role'] = self.role.to_dict()
        
        return data
    
    def has_permission(self, permission):
        """Check if user has a specific permission through their role"""
        if self.role:
            return self.role.has_permission(permission)
        return False
    
    def is_admin(self):
        """Check if user is an admin"""
        from app.models.role import Role
        return self.role and self.role.name == Role.ADMIN
    
    def is_manager(self):
        """Check if user is a manager"""
        from app.models.role import Role
        return self.role and self.role.name == Role.MANAGER
    
    def is_staff(self):
        """Check if user is staff"""
        from app.models.role import Role
        return self.role and self.role.name == Role.STAFF
