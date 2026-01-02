"""
Employee Service - API Routes
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from models import db, Employee, Role, WorkShift
from utils import parse_date

employee_bp = Blueprint('employee', __name__)


@employee_bp.route('/health', methods=['GET'])
def health_check():
    from flask import current_app
    return jsonify({
        'status': 'healthy',
        'service': 'employee_service',
        'port': 5006,
        'database': 'MySQL' if 'mysql' in current_app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@employee_bp.route('/api/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.filter_by(is_active=True).all()
    return jsonify({'success': True, 'data': [e.to_dict() for e in employees]}), 200


@employee_bp.route('/api/employees/<int:id>', methods=['GET'])
def get_employee(id):
    employee = Employee.query.get_or_404(id)
    return jsonify({'success': True, 'data': employee.to_dict()}), 200


@employee_bp.route('/api/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    if not data.get('full_name'):
        return jsonify({'success': False, 'message': 'Tên là bắt buộc'}), 400
    
    employee = Employee(
        code=data.get('employee_code') or f"NV{datetime.now().strftime('%Y%m%d%H%M%S')}",
        full_name=data['full_name'],
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        date_of_birth=parse_date(data.get('date_of_birth')),
        gender=data.get('gender'),
        id_card=data.get('id_card'),
        hire_date=parse_date(data.get('hire_date')),
        role_id=data.get('role_id', 1),
        base_salary=data.get('base_salary', 0)
    )
    if data.get('password'):
        employee.set_password(data['password'])
    db.session.add(employee)
    db.session.commit()
    return jsonify({'success': True, 'data': employee.to_dict()}), 201


@employee_bp.route('/api/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    employee = Employee.query.get_or_404(id)
    data = request.get_json()
    
    # Handle regular fields
    for field in ['full_name', 'phone', 'email', 'address', 'gender', 'id_card', 'role_id', 'base_salary']:
        if field in data:
            setattr(employee, field, data[field])
    
    # Handle date fields
    if 'date_of_birth' in data and data['date_of_birth']:
        employee.date_of_birth = parse_date(data['date_of_birth'])
    if 'hire_date' in data and data['hire_date']:
        employee.hire_date = parse_date(data['hire_date'])
    
    db.session.commit()
    return jsonify({'success': True, 'data': employee.to_dict()}), 200


@employee_bp.route('/api/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    employee.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Xóa thành công'}), 200


@employee_bp.route('/api/employees/login', methods=['POST'])
def login():
    data = request.get_json()
    employee = Employee.query.filter_by(code=data.get('code'), is_active=True).first()
    if not employee or not employee.check_password(data.get('password', '')):
        return jsonify({'success': False, 'message': 'Sai mã NV hoặc mật khẩu'}), 401
    return jsonify({'success': True, 'data': employee.to_dict()}), 200


@employee_bp.route('/api/employees/roles', methods=['GET'])
def get_roles():
    roles = Role.query.all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in roles]}), 200


@employee_bp.route('/api/employees/shifts', methods=['GET'])
def get_shifts():
    shifts = WorkShift.query.all()
    return jsonify({'success': True, 'data': [s.to_dict() for s in shifts]}), 200


@employee_bp.route('/api/employees/statistics', methods=['GET'])
def get_statistics():
    total = Employee.query.filter_by(is_active=True).count()
    return jsonify({'success': True, 'data': {'total_employees': total}}), 200


@employee_bp.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
