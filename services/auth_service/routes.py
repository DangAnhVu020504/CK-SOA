"""
Auth Service - API Routes
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from models import db, User, Role

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/health', methods=['GET'])
def health_check():
    from flask import current_app
    return jsonify({
        'status': 'healthy',
        'service': 'auth_service',
        'port': 5100,
        'database': 'MySQL' if 'mysql' in current_app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Username và password là bắt buộc'}), 400
    
    user = User.query.filter_by(username=data['username'], is_active=True).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': 'Sai username hoặc password'}), 401
    
    token = f"token_{user.id}_{datetime.utcnow().timestamp()}"
    return jsonify({'success': True, 'data': {'user': user.to_dict(), 'token': token}}), 200


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Thiếu thông tin bắt buộc'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': 'Username đã tồn tại'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email đã tồn tại'}), 400
    
    default_role = Role.query.filter_by(name='staff').first()
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name'),
        role_id=default_role.id if default_role else None
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'data': user.to_dict()}), 201


@auth_bp.route('/api/auth/me', methods=['GET'])
def get_current_user():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    return jsonify({'success': True, 'message': 'Token valid'}), 200


@auth_bp.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.filter_by(is_active=True).all()
    return jsonify({'success': True, 'data': [u.to_dict() for u in users]}), 200


@auth_bp.route('/api/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in roles]}), 200


@auth_bp.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
