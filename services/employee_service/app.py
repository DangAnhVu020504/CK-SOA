"""
Employee Service - Quản lý nhân viên & Ca làm
Port: 5006
Database: MySQL (employee_db)
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

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'employee-service-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'EMPLOYEE_DB_URL',
    f'sqlite:///{current_dir}/employee_service.db'
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
    salary_rate = db.Column(db.Float, default=1.0)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description, 'salary_rate': self.salary_rate}


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))  # male, female, other
    id_card = db.Column(db.String(20))  # CMND/CCCD
    hire_date = db.Column(db.Date)
    password_hash = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    base_salary = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    role = db.relationship('Role', backref='employees')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id, 'code': self.code, 'full_name': self.full_name,
            'phone': self.phone, 'email': self.email, 'address': self.address,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender, 'id_card': self.id_card,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'role': self.role.name if self.role else None,
            'role_id': self.role_id,
            'base_salary': self.base_salary, 'is_active': self.is_active
        }


class WorkShift(db.Model):
    __tablename__ = 'work_shifts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'start_time': self.start_time, 'end_time': self.end_time}


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 'service': 'employee_service', 'port': 5006,
        'database': 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@app.route('/api/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.filter_by(is_active=True).all()
    return jsonify({'success': True, 'data': [e.to_dict() for e in employees]}), 200


@app.route('/api/employees/<int:id>', methods=['GET'])
def get_employee(id):
    employee = Employee.query.get_or_404(id)
    return jsonify({'success': True, 'data': employee.to_dict()}), 200


@app.route('/api/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    if not data.get('full_name'):
        return jsonify({'success': False, 'message': 'Tên là bắt buộc'}), 400
    
    # Parse dates
    date_of_birth = None
    hire_date = None
    if data.get('date_of_birth'):
        try:
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except:
            pass
    if data.get('hire_date'):
        try:
            hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
        except:
            pass
    
    employee = Employee(
        code=data.get('employee_code') or f"NV{datetime.now().strftime('%Y%m%d%H%M%S')}",
        full_name=data['full_name'], phone=data.get('phone'),
        email=data.get('email'), address=data.get('address'),
        date_of_birth=date_of_birth, gender=data.get('gender'),
        id_card=data.get('id_card'), hire_date=hire_date,
        role_id=data.get('role_id', 1), base_salary=data.get('base_salary', 0)
    )
    if data.get('password'):
        employee.set_password(data['password'])
    db.session.add(employee)
    db.session.commit()
    return jsonify({'success': True, 'data': employee.to_dict()}), 201


@app.route('/api/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    employee = Employee.query.get_or_404(id)
    data = request.get_json()
    
    # Handle regular fields
    for field in ['full_name', 'phone', 'email', 'address', 'gender', 'id_card', 'role_id', 'base_salary']:
        if field in data:
            setattr(employee, field, data[field])
    
    # Handle date fields
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            employee.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except:
            pass
    if 'hire_date' in data and data['hire_date']:
        try:
            employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
        except:
            pass
    
    db.session.commit()
    return jsonify({'success': True, 'data': employee.to_dict()}), 200


@app.route('/api/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    employee.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Xóa thành công'}), 200


@app.route('/api/employees/login', methods=['POST'])
def login():
    data = request.get_json()
    employee = Employee.query.filter_by(code=data.get('code'), is_active=True).first()
    if not employee or not employee.check_password(data.get('password', '')):
        return jsonify({'success': False, 'message': 'Sai mã NV hoặc mật khẩu'}), 401
    return jsonify({'success': True, 'data': employee.to_dict()}), 200


@app.route('/api/employees/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in roles]}), 200


@app.route('/api/employees/shifts', methods=['GET'])
def get_shifts():
    shifts = WorkShift.query.all()
    return jsonify({'success': True, 'data': [s.to_dict() for s in shifts]}), 200


@app.route('/api/employees/statistics', methods=['GET'])
def get_statistics():
    total = Employee.query.filter_by(is_active=True).count()
    return jsonify({'success': True, 'data': {'total_employees': total}}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404


def init_defaults():
    roles = [
        {'name': 'Quản lý', 'description': 'Quản lý cửa hàng', 'salary_rate': 1.5},
        {'name': 'Thu ngân', 'description': 'Nhân viên thu ngân', 'salary_rate': 1.0},
        {'name': 'Kho', 'description': 'Nhân viên kho', 'salary_rate': 1.0},
        {'name': 'Bán hàng', 'description': 'Nhân viên bán hàng', 'salary_rate': 1.0}
    ]
    for r in roles:
        if not Role.query.filter_by(name=r['name']).first():
            db.session.add(Role(**r))
    
    shifts = [
        {'name': 'Ca sáng', 'start_time': '06:00', 'end_time': '14:00'},
        {'name': 'Ca chiều', 'start_time': '14:00', 'end_time': '22:00'},
        {'name': 'Ca đêm', 'start_time': '22:00', 'end_time': '06:00'}
    ]
    for s in shifts:
        if not WorkShift.query.filter_by(name=s['name']).first():
            db.session.add(WorkShift(**s))
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_defaults()
    
    try:
        from shared.consul_utils import register_flask_service
        register_flask_service(app, 'employee_service', 5006, ['employee', 'hr'])
    except Exception as e:
        print(f"Warning: Could not register with Consul: {e}")
    
    db_type = 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    print("=" * 50)
    print(f"  Employee Service running on port 5006")
    print(f"  Database: {db_type}")
    print("=" * 50)
    app.run(debug=True, port=5006, host='0.0.0.0')
