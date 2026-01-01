# Authentication Service - Business logic for login/register
import re
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity

from app.dao.user_dao import UserDAO
from app.dao.role_dao import RoleDAO
from app.models.role import Role


class AuthService:
    """Service layer for authentication operations"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength
        - At least 6 characters
        - Contains at least one letter and one number
        """
        if len(password) < 6:
            return False, 'Mật khẩu phải có ít nhất 6 ký tự'
        if not re.search(r'[A-Za-z]', password):
            return False, 'Mật khẩu phải chứa ít nhất một chữ cái'
        if not re.search(r'\d', password):
            return False, 'Mật khẩu phải chứa ít nhất một chữ số'
        return True, ''
    
    @staticmethod
    def validate_username(username):
        """
        Validate username
        - 3-80 characters
        - Only letters, numbers, and underscores
        """
        if len(username) < 3 or len(username) > 80:
            return False, 'Username phải có từ 3 đến 80 ký tự'
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, 'Username chỉ được chứa chữ cái, số và dấu gạch dưới'
        return True, ''
    
    @staticmethod
    def register(username, email, password, **kwargs):
        """
        Register a new user
        
        Args:
            username: User's username
            email: User's email
            password: User's password
            **kwargs: Additional user information (full_name, phone, address)
        
        Returns:
            dict with success status and message/data
        """
        # Validate username
        valid, message = AuthService.validate_username(username)
        if not valid:
            return {'success': False, 'message': message}
        
        # Validate email
        if not AuthService.validate_email(email):
            return {'success': False, 'message': 'Email không hợp lệ'}
        
        # Validate password
        valid, message = AuthService.validate_password(password)
        if not valid:
            return {'success': False, 'message': message}
        
        # Check if username exists
        if UserDAO.username_exists(username):
            return {'success': False, 'message': 'Username đã được sử dụng'}
        
        # Check if email exists
        if UserDAO.email_exists(email):
            return {'success': False, 'message': 'Email đã được sử dụng'}
        
        # Get default customer role
        default_role = RoleDAO.get_by_name(Role.CUSTOMER)
        if not default_role:
            return {'success': False, 'message': 'Lỗi hệ thống: Không tìm thấy role mặc định'}
        
        # Create user
        try:
            user = UserDAO.create(
                username=username,
                email=email,
                password=password,
                role_id=default_role.id,
                **kwargs
            )
            
            # Generate tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return {
                'success': True,
                'message': 'Đăng ký thành công',
                'data': {
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'Lỗi đăng ký: {str(e)}'}
    
    @staticmethod
    def login(username_or_email, password):
        """
        Authenticate user and generate JWT tokens
        
        Args:
            username_or_email: Username or email
            password: User's password
        
        Returns:
            dict with success status and tokens/user data
        """
        # Find user by username or email
        user = UserDAO.get_by_username(username_or_email)
        if not user:
            user = UserDAO.get_by_email(username_or_email)
        
        if not user:
            return {
                'success': False,
                'message': 'Tài khoản không tồn tại'
            }
        
        # Check if user is active
        if not user.is_active:
            return {
                'success': False,
                'message': 'Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ admin'
            }
        
        # Verify password
        if not user.check_password(password):
            return {
                'success': False,
                'message': 'Mật khẩu không chính xác'
            }
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'success': True,
            'message': 'Đăng nhập thành công',
            'data': {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }
    
    @staticmethod
    def refresh_token():
        """
        Refresh access token using refresh token
        
        Returns:
            dict with new access token
        """
        try:
            current_user_id = get_jwt_identity()
            user = UserDAO.get_by_id(current_user_id)
            
            if not user or not user.is_active:
                return {
                    'success': False,
                    'message': 'Không thể làm mới token'
                }
            
            new_access_token = create_access_token(identity=current_user_id)
            
            return {
                'success': True,
                'message': 'Làm mới token thành công',
                'data': {
                    'access_token': new_access_token
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi làm mới token: {str(e)}'
            }
    
    @staticmethod
    def get_current_user(user_id):
        """Get current authenticated user"""
        user = UserDAO.get_by_id(user_id)
        if user and user.is_active:
            return user
        return None
    
    @staticmethod
    def register_admin(username, email, password, admin_secret, **kwargs):
        """
        Register an admin user (requires admin secret key)
        
        Args:
            username: Admin's username
            email: Admin's email
            password: Admin's password
            admin_secret: Secret key to verify admin registration
            **kwargs: Additional user information
        
        Returns:
            dict with success status and message/data
        """
        # Verify admin secret (should be stored securely in production)
        import os
        expected_secret = os.environ.get('ADMIN_SECRET') or 'admin-secret-key'
        
        if admin_secret != expected_secret:
            return {'success': False, 'message': 'Admin secret không hợp lệ'}
        
        # Validate inputs
        valid, message = AuthService.validate_username(username)
        if not valid:
            return {'success': False, 'message': message}
        
        if not AuthService.validate_email(email):
            return {'success': False, 'message': 'Email không hợp lệ'}
        
        valid, message = AuthService.validate_password(password)
        if not valid:
            return {'success': False, 'message': message}
        
        # Check uniqueness
        if UserDAO.username_exists(username):
            return {'success': False, 'message': 'Username đã được sử dụng'}
        
        if UserDAO.email_exists(email):
            return {'success': False, 'message': 'Email đã được sử dụng'}
        
        # Get admin role
        admin_role = RoleDAO.get_by_name(Role.ADMIN)
        if not admin_role:
            return {'success': False, 'message': 'Lỗi hệ thống: Không tìm thấy role admin'}
        
        # Create admin user
        try:
            user = UserDAO.create(
                username=username,
                email=email,
                password=password,
                role_id=admin_role.id,
                **kwargs
            )
            
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return {
                'success': True,
                'message': 'Đăng ký admin thành công',
                'data': {
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'Lỗi đăng ký: {str(e)}'}
