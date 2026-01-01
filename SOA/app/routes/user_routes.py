# User Management Routes
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.dao.user_dao import UserDAO
from app.utils.decorators import admin_required, role_required, manager_or_admin_required
from app.utils.validators import validate_request_json, validate_pagination_params

user_bp = Blueprint('users', __name__)


# =====================
# Current User Endpoints
# =====================

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    """
    Get current user's profile
    """
    user_id = get_jwt_identity()
    result = UserService.get_user_profile(user_id)
    
    status_code = 200 if result['success'] else 404
    return jsonify(result), status_code


@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_my_profile():
    """
    Update current user's profile
    
    Request Body:
    {
        "full_name": "string" (optional),
        "phone": "string" (optional),
        "address": "string" (optional),
        "email": "string" (optional)
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    result = UserService.update_profile(user_id, **data)
    
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code


# =====================
# Admin/Manager Endpoints
# =====================

@user_bp.route('', methods=['GET'])
@jwt_required()
@role_required(['admin', 'manager'])
@validate_pagination_params
def get_all_users(page=1, per_page=10):
    """
    Get all users with pagination (admin/manager only)
    
    Query Params:
        page: int (default 1)
        per_page: int (default 10, max 100)
        include_inactive: bool (default false)
    """
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    # Only admin can see inactive users
    user = UserDAO.get_by_id(get_jwt_identity())
    if not user.is_admin():
        include_inactive = False
    
    result = UserService.get_all_users(
        page=page,
        per_page=per_page,
        include_inactive=include_inactive
    )
    
    return jsonify(result), 200


@user_bp.route('/search', methods=['GET'])
@jwt_required()
@role_required(['admin', 'manager'])
@validate_pagination_params
def search_users(page=1, per_page=10):
    """
    Search users by keyword (admin/manager only)
    
    Query Params:
        q: string (search keyword)
        page: int
        per_page: int
    """
    keyword = request.args.get('q', '')
    
    if not keyword:
        return jsonify({
            'success': False,
            'message': 'Vui lòng nhập từ khóa tìm kiếm'
        }), 400
    
    result = UserService.search_users(
        keyword=keyword,
        page=page,
        per_page=per_page
    )
    
    return jsonify(result), 200


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required(['admin', 'manager'])
def get_user(user_id):
    """
    Get user by ID (admin/manager only)
    """
    result = UserService.get_user_by_id(user_id)
    
    status_code = 200 if result['success'] else 404
    return jsonify(result), status_code


@user_bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required
@validate_request_json(['role_id'])
def assign_user_role(user_id):
    """
    Assign role to user (admin only)
    
    Request Body:
    {
        "role_id": int
    }
    """
    admin_user = UserDAO.get_by_id(get_jwt_identity())
    data = request.get_json()
    
    result = UserService.assign_role(
        user_id=user_id,
        role_id=data['role_id'],
        admin_user=admin_user
    )
    
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code


@user_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@jwt_required()
@admin_required
def deactivate_user(user_id):
    """
    Deactivate a user account (admin only)
    """
    admin_user = UserDAO.get_by_id(get_jwt_identity())
    result = UserService.deactivate_user(user_id, admin_user)
    
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code


@user_bp.route('/<int:user_id>/activate', methods=['POST'])
@jwt_required()
@admin_required
def activate_user(user_id):
    """
    Activate a user account (admin only)
    """
    admin_user = UserDAO.get_by_id(get_jwt_identity())
    result = UserService.activate_user(user_id, admin_user)
    
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code


# =====================
# Role Endpoints
# =====================

@user_bp.route('/roles', methods=['GET'])
@jwt_required()
@role_required(['admin', 'manager'])
def get_all_roles():
    """
    Get all roles (admin/manager only)
    """
    roles = RoleService.get_all_roles()
    
    return jsonify({
        'success': True,
        'data': roles
    }), 200


@user_bp.route('/roles/<int:role_id>', methods=['GET'])
@jwt_required()
@role_required(['admin', 'manager'])
def get_role(role_id):
    """
    Get role by ID (admin/manager only)
    """
    role = RoleService.get_role_by_id(role_id)
    
    if role:
        return jsonify({
            'success': True,
            'data': role
        }), 200
    
    return jsonify({
        'success': False,
        'message': 'Không tìm thấy role'
    }), 404


@user_bp.route('/roles', methods=['POST'])
@jwt_required()
@admin_required
@validate_request_json(['name'])
def create_role():
    """
    Create a new role (admin only)
    
    Request Body:
    {
        "name": "string",
        "description": "string" (optional),
        "permissions": ["string"] (optional)
    }
    """
    data = request.get_json()
    
    result = RoleService.create_role(
        name=data['name'],
        description=data.get('description'),
        permissions=data.get('permissions', [])
    )
    
    status_code = 201 if result['success'] else 400
    return jsonify(result), status_code


@user_bp.route('/by-role/<int:role_id>', methods=['GET'])
@jwt_required()
@role_required(['admin', 'manager'])
@validate_pagination_params
def get_users_by_role(role_id, page=1, per_page=10):
    """
    Get users by role (admin/manager only)
    """
    result = UserService.get_users_by_role(
        role_id=role_id,
        page=page,
        per_page=per_page
    )
    
    return jsonify(result), 200
