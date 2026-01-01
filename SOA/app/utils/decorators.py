# Custom decorators for role-based access control
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.dao.user_dao import UserDAO
from app.models.role import Role


def role_required(allowed_roles):
    """
    Decorator to restrict access to specific roles
    
    Usage:
        @role_required(['admin', 'manager'])
        def some_endpoint():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            
            user_id = get_jwt_identity()
            user = UserDAO.get_by_id(user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Người dùng không tồn tại'
                }), 401
            
            if not user.is_active:
                return jsonify({
                    'success': False,
                    'message': 'Tài khoản đã bị vô hiệu hóa'
                }), 403
            
            if user.role.name not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': 'Bạn không có quyền truy cập chức năng này'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """
    Decorator to restrict access to admin only
    
    Usage:
        @admin_required
        def admin_endpoint():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        
        user_id = get_jwt_identity()
        user = UserDAO.get_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Người dùng không tồn tại'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Tài khoản đã bị vô hiệu hóa'
            }), 403
        
        if not user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Chỉ admin mới có quyền truy cập'
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def permission_required(permission):
    """
    Decorator to check for specific permission
    
    Usage:
        @permission_required('manage_products')
        def manage_products():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            
            user_id = get_jwt_identity()
            user = UserDAO.get_by_id(user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Người dùng không tồn tại'
                }), 401
            
            if not user.is_active:
                return jsonify({
                    'success': False,
                    'message': 'Tài khoản đã bị vô hiệu hóa'
                }), 403
            
            if not user.has_permission(permission):
                return jsonify({
                    'success': False,
                    'message': f'Bạn không có quyền "{permission}"'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def manager_or_admin_required(fn):
    """
    Decorator to restrict access to manager or admin
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        
        user_id = get_jwt_identity()
        user = UserDAO.get_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Người dùng không tồn tại'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Tài khoản đã bị vô hiệu hóa'
            }), 403
        
        if not (user.is_admin() or user.is_manager()):
            return jsonify({
                'success': False,
                'message': 'Chỉ admin hoặc manager mới có quyền truy cập'
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper
