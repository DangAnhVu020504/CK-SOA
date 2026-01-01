# User Service - Business logic for user management
from app.dao.user_dao import UserDAO
from app.dao.role_dao import RoleDAO


class UserService:
    """Service layer for user management"""
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        user = UserDAO.get_by_id(user_id)
        if user:
            return {
                'success': True,
                'data': user.to_dict()
            }
        return {
            'success': False,
            'message': 'Không tìm thấy người dùng'
        }
    
    @staticmethod
    def get_user_profile(user_id):
        """Get user profile"""
        return UserService.get_user_by_id(user_id)
    
    @staticmethod
    def get_all_users(page=1, per_page=10, include_inactive=False):
        """Get all users with pagination"""
        pagination = UserDAO.get_all(page, per_page, include_inactive)
        
        return {
            'success': True,
            'data': {
                'users': [user.to_dict() for user in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    
    @staticmethod
    def get_users_by_role(role_id, page=1, per_page=10):
        """Get users by role"""
        pagination = UserDAO.get_by_role(role_id, page, per_page)
        
        return {
            'success': True,
            'data': {
                'users': [user.to_dict() for user in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page
            }
        }
    
    @staticmethod
    def update_profile(user_id, **kwargs):
        """Update user profile"""
        # Remove fields that shouldn't be updated via this method
        protected_fields = ['role_id', 'is_active', 'password']
        for field in protected_fields:
            kwargs.pop(field, None)
        
        user = UserDAO.update(user_id, **kwargs)
        if user:
            return {
                'success': True,
                'message': 'Cập nhật thông tin thành công',
                'data': user.to_dict()
            }
        return {
            'success': False,
            'message': 'Không tìm thấy người dùng'
        }
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password"""
        user = UserDAO.get_by_id(user_id)
        
        if not user:
            return {
                'success': False,
                'message': 'Không tìm thấy người dùng'
            }
        
        if not user.check_password(old_password):
            return {
                'success': False,
                'message': 'Mật khẩu cũ không chính xác'
            }
        
        # Validate new password
        if len(new_password) < 6:
            return {
                'success': False,
                'message': 'Mật khẩu mới phải có ít nhất 6 ký tự'
            }
        
        UserDAO.update(user_id, password=new_password)
        
        return {
            'success': True,
            'message': 'Đổi mật khẩu thành công'
        }
    
    @staticmethod
    def assign_role(user_id, role_id, admin_user):
        """Assign a role to user (admin only)"""
        # Check if admin
        if not admin_user.is_admin():
            return {
                'success': False,
                'message': 'Chỉ admin mới có quyền thay đổi role'
            }
        
        # Check if role exists
        role = RoleDAO.get_by_id(role_id)
        if not role:
            return {
                'success': False,
                'message': 'Role không tồn tại'
            }
        
        user = UserDAO.update(user_id, role_id=role_id)
        if user:
            return {
                'success': True,
                'message': f'Đã gán role "{role.name}" cho người dùng',
                'data': user.to_dict()
            }
        return {
            'success': False,
            'message': 'Không tìm thấy người dùng'
        }
    
    @staticmethod
    def deactivate_user(user_id, admin_user):
        """Deactivate a user (admin only)"""
        if not admin_user.is_admin():
            return {
                'success': False,
                'message': 'Chỉ admin mới có quyền vô hiệu hóa tài khoản'
            }
        
        # Prevent self-deactivation
        if admin_user.id == user_id:
            return {
                'success': False,
                'message': 'Không thể vô hiệu hóa tài khoản của chính mình'
            }
        
        if UserDAO.delete(user_id):
            return {
                'success': True,
                'message': 'Đã vô hiệu hóa tài khoản'
            }
        return {
            'success': False,
            'message': 'Không tìm thấy người dùng'
        }
    
    @staticmethod
    def activate_user(user_id, admin_user):
        """Activate a user (admin only)"""
        if not admin_user.is_admin():
            return {
                'success': False,
                'message': 'Chỉ admin mới có quyền kích hoạt tài khoản'
            }
        
        user = UserDAO.update(user_id, is_active=True)
        if user:
            return {
                'success': True,
                'message': 'Đã kích hoạt tài khoản',
                'data': user.to_dict()
            }
        return {
            'success': False,
            'message': 'Không tìm thấy người dùng'
        }
    
    @staticmethod
    def search_users(keyword, page=1, per_page=10):
        """Search users"""
        pagination = UserDAO.search(keyword, page, per_page)
        
        return {
            'success': True,
            'data': {
                'users': [user.to_dict() for user in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'keyword': keyword
            }
        }
