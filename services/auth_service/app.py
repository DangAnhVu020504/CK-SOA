"""
Auth Service - Xác thực và phân quyền
Port: 5100
Database: MySQL (auth_db)
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(services_dir)
sys.path.insert(0, root_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(root_dir, '.env'))

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'auth-service-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'AUTH_DB_URL',
    f'sqlite:///{current_dir}/auth_service.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280, 'pool_pre_ping': True}

CORS(app)
db = SQLAlchemy(app)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)
    
    def to_dict(self):
        perms = {}
        if self.permissions:
            try:
                perms = json.loads(self.permissions)
            except:
                pass
        return {'id': self.id, 'name': self.name, 'description': self.description, 'permissions': perms}


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    role = db.relationship('Role', backref='users')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id, 'username': self.username, 'email': self.email,
            'full_name': self.full_name, 'role': self.role.name if self.role else None,
            'is_active': self.is_active
        }


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 'service': 'auth_service', 'port': 5100,
        'database': 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Username và password là bắt buộc'}), 400
    
    user = User.query.filter_by(username=data['username'], is_active=True).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': 'Sai username hoặc password'}), 401
    
    token = f"token_{user.id}_{datetime.utcnow().timestamp()}"
    return jsonify({'success': True, 'data': {'user': user.to_dict(), 'token': token}}), 200


@app.route('/api/auth/register', methods=['POST'])
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
        username=data['username'], email=data['email'],
        full_name=data.get('full_name'),
        role_id=default_role.id if default_role else None
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'data': user.to_dict()}), 201


@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    return jsonify({'success': True, 'message': 'Token valid'}), 200


@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.filter_by(is_active=True).all()
    return jsonify({'success': True, 'data': [u.to_dict() for u in users]}), 200


@app.route('/api/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in roles]}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404


def init_default_roles():
    defaults = [
        {'name': 'admin', 'description': 'Administrator', 'permissions': '{"all": true}'},
        {'name': 'manager', 'description': 'Manager', 'permissions': '{"read": true, "write": true}'},
        {'name': 'staff', 'description': 'Staff', 'permissions': '{"read": true}'},
        {'name': 'customer', 'description': 'Customer', 'permissions': '{"read": true}'}
    ]
    for r in defaults:
        if not Role.query.filter_by(name=r['name']).first():
            db.session.add(Role(**r))
    db.session.commit()


def init_default_admin():
    """Create or update default admin account"""
    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role:
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@supermarket.local',
                full_name='Administrator',
                role_id=admin_role.id,
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("  Default admin user created: admin / admin123")
        else:
            # Ensure admin has correct role and password
            admin_user.role_id = admin_role.id
            admin_user.set_password('admin123')
            db.session.commit()
            print("  Admin password reset: admin / admin123")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_default_roles()
        init_default_admin()
    
    try:
        from shared.consul_utils import register_flask_service
        register_flask_service(app, 'auth_service', 5100, ['auth', 'jwt'])
    except Exception as e:
        print(f"Warning: Could not register with Consul: {e}")
    
    db_type = 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    print("=" * 50)
    print(f"  Auth Service running on port 5100")
    print(f"  Database: {db_type}")
    print("=" * 50)
    app.run(debug=True, port=5100, host='0.0.0.0')
