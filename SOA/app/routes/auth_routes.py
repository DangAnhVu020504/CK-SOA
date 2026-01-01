# Authentication Routes
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService
from app.utils.validators import validate_request_json

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@validate_request_json(['username', 'email', 'password'])
def register():
    """
    Register a new user
    
    Request Body:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "full_name": "string" (optional),
        "phone": "string" (optional),
        "address": "string" (optional)
    }
    """
    data = request.get_json()
    
    result = AuthService.register(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        full_name=data.get('full_name'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    
    status_code = 201 if result['success'] else 400
    return jsonify(result), status_code


@auth_bp.route('/login', methods=['POST'])
@validate_request_json(['username', 'password'])
def login():
    """
    Login with username/email and password
    
    Request Body:
    {
        "username": "string (username or email)",
        "password": "string"
    }
    """
    data = request.get_json()
    
    result = AuthService.login(
        username_or_email=data['username'],
        password=data['password']
    )
    
    status_code = 200 if result['success'] else 401
    return jsonify(result), status_code


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    
    Headers:
        Authorization: Bearer <refresh_token>
    """
    result = AuthService.refresh_token()
    
    status_code = 200 if result['success'] else 401
    return jsonify(result), status_code


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user's information
    
    Headers:
        Authorization: Bearer <access_token>
    """
    user_id = get_jwt_identity()
    user = AuthService.get_current_user(user_id)
    
    if user:
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    
    return jsonify({
        'success': False,
        'message': 'Không tìm thấy người dùng'
    }), 404


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout (client should discard the token)
    
    Note: In a production environment, you might want to implement
    token blacklisting for more secure logout.
    """
    return jsonify({
        'success': True,
        'message': 'Đăng xuất thành công. Vui lòng xóa token ở phía client.'
    }), 200


@auth_bp.route('/register-admin', methods=['POST'])
@validate_request_json(['username', 'email', 'password', 'admin_secret'])
def register_admin():
    """
    Register an admin user (requires admin secret key)
    
    Request Body:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "admin_secret": "string",
        "full_name": "string" (optional)
    }
    """
    data = request.get_json()
    
    result = AuthService.register_admin(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        admin_secret=data['admin_secret'],
        full_name=data.get('full_name')
    )
    
    status_code = 201 if result['success'] else 400
    return jsonify(result), status_code


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@validate_request_json(['old_password', 'new_password'])
def change_password():
    """
    Change password for current user
    
    Request Body:
    {
        "old_password": "string",
        "new_password": "string"
    }
    """
    from app.services.user_service import UserService
    
    user_id = get_jwt_identity()
    data = request.get_json()
    
    result = UserService.change_password(
        user_id=user_id,
        old_password=data['old_password'],
        new_password=data['new_password']
    )
    
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code
