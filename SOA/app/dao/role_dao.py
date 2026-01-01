# Role Data Access Object
from app.extensions import db
from app.models.role import Role


class RoleDAO:
    """Data Access Object for Role operations"""
    
    @staticmethod
    def create(name, description=None, permissions=None):
        """Create a new role"""
        role = Role(name=name, description=description, permissions=permissions)
        db.session.add(role)
        db.session.commit()
        return role
    
    @staticmethod
    def get_by_id(role_id):
        """Get role by ID"""
        return Role.query.get(role_id)
    
    @staticmethod
    def get_by_name(name):
        """Get role by name"""
        return Role.query.filter_by(name=name).first()
    
    @staticmethod
    def get_all():
        """Get all roles"""
        return Role.query.all()
    
    @staticmethod
    def update(role_id, **kwargs):
        """Update role information"""
        role = Role.query.get(role_id)
        if role:
            for key, value in kwargs.items():
                if hasattr(role, key):
                    setattr(role, key, value)
            db.session.commit()
        return role
    
    @staticmethod
    def delete(role_id):
        """Delete a role"""
        role = Role.query.get(role_id)
        if role:
            db.session.delete(role)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def exists(name):
        """Check if role exists by name"""
        return Role.query.filter_by(name=name).first() is not None
    
    @staticmethod
    def get_default_role():
        """Get the default customer role"""
        return Role.query.filter_by(name=Role.CUSTOMER).first()
