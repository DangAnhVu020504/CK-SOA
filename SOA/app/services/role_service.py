# Role Service - Business logic for role management
from app.dao.role_dao import RoleDAO
from app.models.role import Role


class RoleService:
    """Service layer for role management and authorization"""
    
    @staticmethod
    def initialize_default_roles():
        """Initialize default roles in the database"""
        default_roles = Role.get_default_roles()
        
        for role_data in default_roles:
            if not RoleDAO.exists(role_data['name']):
                RoleDAO.create(
                    name=role_data['name'],
                    description=role_data['description'],
                    permissions=role_data['permissions']
                )
        
        return True
    
    @staticmethod
    def get_all_roles():
        """Get all roles"""
        roles = RoleDAO.get_all()
        return [role.to_dict() for role in roles]
    
    @staticmethod
    def get_role_by_id(role_id):
        """Get role by ID"""
        role = RoleDAO.get_by_id(role_id)
        if role:
            return role.to_dict()
        return None
    
    @staticmethod
    def get_role_by_name(name):
        """Get role by name"""
        role = RoleDAO.get_by_name(name)
        if role:
            return role.to_dict()
        return None
    
    @staticmethod
    def create_role(name, description=None, permissions=None):
        """Create a new role"""
        # Check if role already exists
        if RoleDAO.exists(name):
            return {
                'success': False,
                'message': f'Role "{name}" đã tồn tại'
            }
        
        role = RoleDAO.create(
            name=name,
            description=description,
            permissions=permissions or []
        )
        
        return {
            'success': True,
            'message': 'Tạo role thành công',
            'data': role.to_dict()
        }
    
    @staticmethod
    def update_role(role_id, **kwargs):
        """Update role information"""
        role = RoleDAO.update(role_id, **kwargs)
        if role:
            return {
                'success': True,
                'message': 'Cập nhật role thành công',
                'data': role.to_dict()
            }
        return {
            'success': False,
            'message': 'Không tìm thấy role'
        }
    
    @staticmethod
    def delete_role(role_id):
        """Delete a role"""
        # Prevent deleting default roles
        role = RoleDAO.get_by_id(role_id)
        if role and role.name in [Role.ADMIN, Role.MANAGER, Role.STAFF, Role.CUSTOMER]:
            return {
                'success': False,
                'message': 'Không thể xóa role mặc định của hệ thống'
            }
        
        if RoleDAO.delete(role_id):
            return {
                'success': True,
                'message': 'Xóa role thành công'
            }
        return {
            'success': False,
            'message': 'Không tìm thấy role'
        }
    
    @staticmethod
    def check_permission(user, permission):
        """Check if user has a specific permission"""
        if user and user.role:
            return user.role.has_permission(permission)
        return False
    
    @staticmethod
    def get_user_permissions(user):
        """Get all permissions for a user"""
        if user and user.role:
            return user.role.permissions
        return []
