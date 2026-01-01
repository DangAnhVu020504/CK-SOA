"""
Employee Service Routes - API Endpoints
"""
from flask import Blueprint, request, jsonify
from models import db, Employee, Role, WorkShift, EmployeeShift
from datetime import datetime, date, timedelta

employee_bp = Blueprint('employee', __name__)


# =====================================================
# EMPLOYEE ENDPOINTS
# =====================================================

@employee_bp.route('/api/employees', methods=['GET'])
def get_employees():
    """Lấy danh sách tất cả nhân viên"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        role_id = request.args.get('role_id', type=int)
        
        query = Employee.query
        
        if status:
            query = query.filter_by(status=status)
        if role_id:
            query = query.filter_by(role_id=role_id)
        
        employees = query.order_by(Employee.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [e.to_dict() for e in employees.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': employees.total,
                'pages': employees.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/employees/<int:id>', methods=['GET'])
def get_employee(id):
    """Lấy thông tin chi tiết một nhân viên"""
    try:
        include_shifts = request.args.get('include_shifts', 'false').lower() == 'true'
        employee = Employee.query.get_or_404(id)
        return jsonify({
            'success': True,
            'data': employee.to_dict(include_shifts=include_shifts)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404


@employee_bp.route('/api/employees', methods=['POST'])
def create_employee():
    """Thêm nhân viên mới"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['full_name', 'phone', 'password', 'role_id', 'hire_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} là bắt buộc'}), 400
        
        # Check if phone already exists
        existing = Employee.query.filter_by(phone=data['phone']).first()
        if existing:
            return jsonify({'success': False, 'error': 'Số điện thoại đã được sử dụng'}), 400
        
        # Check if role exists
        role = Role.query.get(data['role_id'])
        if not role:
            return jsonify({'success': False, 'error': 'Vai trò không tồn tại'}), 400
        
        # Create new employee
        employee = Employee(
            employee_code=Employee.generate_employee_code(),
            full_name=data['full_name'],
            phone=data['phone'],
            email=data.get('email'),
            address=data.get('address'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            gender=data.get('gender', 'other'),
            role_id=data['role_id'],
            salary=data.get('salary', 0),
            hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date(),
            status='active',
            avatar_url=data.get('avatar_url')
        )
        employee.set_password(data['password'])
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Thêm nhân viên thành công',
            'data': employee.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    """Cập nhật thông tin nhân viên"""
    try:
        employee = Employee.query.get_or_404(id)
        data = request.get_json()
        
        # Update fields
        if 'full_name' in data:
            employee.full_name = data['full_name']
        if 'phone' in data:
            existing = Employee.query.filter(Employee.phone == data['phone'], Employee.id != id).first()
            if existing:
                return jsonify({'success': False, 'error': 'Số điện thoại đã được sử dụng'}), 400
            employee.phone = data['phone']
        if 'email' in data:
            employee.email = data['email']
        if 'address' in data:
            employee.address = data['address']
        if 'date_of_birth' in data:
            employee.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data['date_of_birth'] else None
        if 'gender' in data:
            employee.gender = data['gender']
        if 'role_id' in data:
            role = Role.query.get(data['role_id'])
            if not role:
                return jsonify({'success': False, 'error': 'Vai trò không tồn tại'}), 400
            employee.role_id = data['role_id']
        if 'salary' in data:
            employee.salary = data['salary']
        if 'status' in data:
            employee.status = data['status']
        if 'avatar_url' in data:
            employee.avatar_url = data['avatar_url']
        if 'password' in data and data['password']:
            employee.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật thành công',
            'data': employee.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    """Xóa nhân viên"""
    try:
        employee = Employee.query.get_or_404(id)
        
        # Option 1: Soft delete (set status to inactive)
        # employee.status = 'inactive'
        
        # Option 2: Hard delete
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Xóa nhân viên thành công'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/employees/search', methods=['GET'])
def search_employees():
    """Tìm kiếm nhân viên"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Vui lòng nhập từ khóa tìm kiếm'}), 400
        
        employees = Employee.query.filter(
            (Employee.full_name.ilike(f'%{query}%')) |
            (Employee.phone.ilike(f'%{query}%')) |
            (Employee.employee_code.ilike(f'%{query}%')) |
            (Employee.email.ilike(f'%{query}%'))
        ).all()
        
        return jsonify({
            'success': True,
            'data': [e.to_dict() for e in employees],
            'count': len(employees)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# AUTHENTICATION ENDPOINTS
# =====================================================

@employee_bp.route('/api/employees/login', methods=['POST'])
def login():
    """Đăng nhập nhân viên"""
    try:
        data = request.get_json()
        
        if not data.get('phone') or not data.get('password'):
            return jsonify({'success': False, 'error': 'Số điện thoại và mật khẩu là bắt buộc'}), 400
        
        employee = Employee.query.filter_by(phone=data['phone']).first()
        
        if not employee or not employee.check_password(data['password']):
            return jsonify({'success': False, 'error': 'Số điện thoại hoặc mật khẩu không đúng'}), 401
        
        if employee.status != 'active':
            return jsonify({'success': False, 'error': 'Tài khoản đã bị vô hiệu hóa'}), 403
        
        return jsonify({
            'success': True,
            'message': 'Đăng nhập thành công',
            'data': employee.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/employees/<int:id>/check-permission', methods=['POST'])
def check_permission(id):
    """Kiểm tra quyền của nhân viên"""
    try:
        employee = Employee.query.get_or_404(id)
        data = request.get_json()
        
        permission = data.get('permission')
        if not permission:
            return jsonify({'success': False, 'error': 'Permission là bắt buộc'}), 400
        
        has_permission = employee.has_permission(permission)
        
        return jsonify({
            'success': True,
            'data': {
                'employee_id': id,
                'permission': permission,
                'has_permission': has_permission,
                'role': employee.role.to_dict() if employee.role else None
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# ROLE ENDPOINTS
# =====================================================

@employee_bp.route('/api/roles', methods=['GET'])
def get_roles():
    """Lấy danh sách các vai trò"""
    try:
        roles = Role.query.all()
        return jsonify({
            'success': True,
            'data': [r.to_dict() for r in roles]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/roles/<int:id>', methods=['GET'])
def get_role(id):
    """Lấy thông tin một vai trò"""
    try:
        role = Role.query.get_or_404(id)
        employees_count = Employee.query.filter_by(role_id=id).count()
        
        data = role.to_dict()
        data['employees_count'] = employees_count
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/roles', methods=['POST'])
def create_role():
    """Tạo vai trò mới"""
    try:
        data = request.get_json()
        
        if not data.get('role_name') or not data.get('role_code'):
            return jsonify({'success': False, 'error': 'Tên và mã vai trò là bắt buộc'}), 400
        
        # Check if role_code already exists
        existing = Role.query.filter_by(role_code=data['role_code']).first()
        if existing:
            return jsonify({'success': False, 'error': 'Mã vai trò đã tồn tại'}), 400
        
        role = Role(
            role_name=data['role_name'],
            role_code=data['role_code'],
            description=data.get('description'),
            permissions=data.get('permissions', {})
        )
        
        db.session.add(role)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tạo vai trò thành công',
            'data': role.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/roles/<int:id>', methods=['PUT'])
def update_role(id):
    """Cập nhật vai trò"""
    try:
        role = Role.query.get_or_404(id)
        data = request.get_json()
        
        if 'role_name' in data:
            role.role_name = data['role_name']
        if 'description' in data:
            role.description = data['description']
        if 'permissions' in data:
            role.permissions = data['permissions']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật vai trò thành công',
            'data': role.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# WORK SHIFT ENDPOINTS
# =====================================================

@employee_bp.route('/api/shifts', methods=['GET'])
def get_shifts():
    """Lấy danh sách các ca làm việc"""
    try:
        shifts = WorkShift.query.all()
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in shifts]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/shifts', methods=['POST'])
def create_shift():
    """Tạo ca làm việc mới"""
    try:
        data = request.get_json()
        
        if not data.get('shift_name') or not data.get('start_time') or not data.get('end_time'):
            return jsonify({'success': False, 'error': 'Tên ca, giờ bắt đầu và giờ kết thúc là bắt buộc'}), 400
        
        shift = WorkShift(
            shift_name=data['shift_name'],
            start_time=datetime.strptime(data['start_time'], '%H:%M:%S').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M:%S').time(),
            description=data.get('description')
        )
        
        db.session.add(shift)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tạo ca làm việc thành công',
            'data': shift.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# EMPLOYEE SHIFT ASSIGNMENT ENDPOINTS
# =====================================================

@employee_bp.route('/api/employee-shifts', methods=['GET'])
def get_employee_shifts():
    """Lấy danh sách phân công ca làm việc"""
    try:
        employee_id = request.args.get('employee_id', type=int)
        shift_id = request.args.get('shift_id', type=int)
        work_date = request.args.get('work_date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        
        query = EmployeeShift.query
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if shift_id:
            query = query.filter_by(shift_id=shift_id)
        if work_date:
            query = query.filter_by(work_date=datetime.strptime(work_date, '%Y-%m-%d').date())
        if start_date:
            query = query.filter(EmployeeShift.work_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(EmployeeShift.work_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        if status:
            query = query.filter_by(status=status)
        
        shifts = query.order_by(EmployeeShift.work_date.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [s.to_dict(include_employee=True) for s in shifts],
            'count': len(shifts)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/employee-shifts', methods=['POST'])
def assign_shift():
    """Phân công ca làm việc cho nhân viên"""
    try:
        data = request.get_json()
        
        if not data.get('employee_id') or not data.get('shift_id') or not data.get('work_date'):
            return jsonify({'success': False, 'error': 'Employee ID, Shift ID và ngày làm việc là bắt buộc'}), 400
        
        # Check if employee exists
        employee = Employee.query.get(data['employee_id'])
        if not employee:
            return jsonify({'success': False, 'error': 'Nhân viên không tồn tại'}), 400
        
        # Check if shift exists
        shift = WorkShift.query.get(data['shift_id'])
        if not shift:
            return jsonify({'success': False, 'error': 'Ca làm việc không tồn tại'}), 400
        
        work_date = datetime.strptime(data['work_date'], '%Y-%m-%d').date()
        
        # Check if already assigned
        existing = EmployeeShift.query.filter_by(
            employee_id=data['employee_id'],
            shift_id=data['shift_id'],
            work_date=work_date
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': 'Nhân viên đã được phân công ca này trong ngày'}), 400
        
        employee_shift = EmployeeShift(
            employee_id=data['employee_id'],
            shift_id=data['shift_id'],
            work_date=work_date,
            status='scheduled',
            note=data.get('note')
        )
        
        db.session.add(employee_shift)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Phân công ca làm việc thành công',
            'data': employee_shift.to_dict(include_employee=True)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/employee-shifts/<int:id>/check-in', methods=['POST'])
def check_in(id):
    """Chấm công vào ca"""
    try:
        employee_shift = EmployeeShift.query.get_or_404(id)
        
        if employee_shift.status not in ['scheduled']:
            return jsonify({'success': False, 'error': 'Không thể chấm công vào ca này'}), 400
        
        status = employee_shift.check_in()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Chấm công vào ca thành công' if status == 'checked_in' else 'Chấm công muộn',
            'data': employee_shift.to_dict(include_employee=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/employee-shifts/<int:id>/check-out', methods=['POST'])
def check_out(id):
    """Chấm công ra ca"""
    try:
        employee_shift = EmployeeShift.query.get_or_404(id)
        
        if employee_shift.status not in ['checked_in', 'late']:
            return jsonify({'success': False, 'error': 'Chưa chấm công vào ca'}), 400
        
        employee_shift.check_out()
        worked_hours = employee_shift.calculate_worked_hours()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Chấm công ra ca thành công',
            'data': {
                'shift': employee_shift.to_dict(include_employee=True),
                'worked_hours': worked_hours
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/employee-shifts/<int:id>/mark-absent', methods=['POST'])
def mark_absent(id):
    """Đánh dấu vắng mặt"""
    try:
        employee_shift = EmployeeShift.query.get_or_404(id)
        data = request.get_json() or {}
        
        employee_shift.status = 'absent'
        employee_shift.note = data.get('note', 'Vắng mặt không phép')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Đã đánh dấu vắng mặt',
            'data': employee_shift.to_dict(include_employee=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# SCHEDULE ENDPOINTS (Week/Month View)
# =====================================================

@employee_bp.route('/api/schedule/weekly', methods=['GET'])
def get_weekly_schedule():
    """Lấy lịch làm việc theo tuần"""
    try:
        start_date = request.args.get('start_date')
        if not start_date:
            # Default to current week (Monday)
            today = date.today()
            start_date = today - timedelta(days=today.weekday())
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        end_date = start_date + timedelta(days=6)
        
        shifts = EmployeeShift.query.filter(
            EmployeeShift.work_date >= start_date,
            EmployeeShift.work_date <= end_date
        ).order_by(EmployeeShift.work_date, EmployeeShift.shift_id).all()
        
        # Group by date
        schedule = {}
        for shift in shifts:
            date_str = shift.work_date.isoformat()
            if date_str not in schedule:
                schedule[date_str] = []
            schedule[date_str].append(shift.to_dict(include_employee=True))
        
        return jsonify({
            'success': True,
            'data': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'schedule': schedule
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employee_bp.route('/api/employees/<int:id>/schedule', methods=['GET'])
def get_employee_schedule(id):
    """Lấy lịch làm việc của một nhân viên"""
    try:
        employee = Employee.query.get_or_404(id)
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = EmployeeShift.query.filter_by(employee_id=id)
        
        if start_date:
            query = query.filter(EmployeeShift.work_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(EmployeeShift.work_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        shifts = query.order_by(EmployeeShift.work_date.desc()).all()
        
        # Calculate statistics
        total_shifts = len(shifts)
        completed_shifts = len([s for s in shifts if s.status == 'checked_out'])
        late_shifts = len([s for s in shifts if s.status == 'late'])
        absent_shifts = len([s for s in shifts if s.status == 'absent'])
        
        total_hours = sum(s.calculate_worked_hours() for s in shifts if s.status == 'checked_out')
        
        return jsonify({
            'success': True,
            'data': {
                'employee': employee.to_dict(),
                'shifts': [s.to_dict() for s in shifts],
                'statistics': {
                    'total_shifts': total_shifts,
                    'completed_shifts': completed_shifts,
                    'late_shifts': late_shifts,
                    'absent_shifts': absent_shifts,
                    'total_worked_hours': round(total_hours, 2)
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# STATISTICS ENDPOINTS
# =====================================================

@employee_bp.route('/api/statistics/employees', methods=['GET'])
def get_employee_statistics():
    """Thống kê nhân viên"""
    try:
        total_employees = Employee.query.count()
        active_employees = Employee.query.filter_by(status='active').count()
        inactive_employees = Employee.query.filter_by(status='inactive').count()
        on_leave_employees = Employee.query.filter_by(status='on_leave').count()
        
        # Count by role
        roles = Role.query.all()
        role_stats = []
        for role in roles:
            count = Employee.query.filter_by(role_id=role.id, status='active').count()
            role_stats.append({
                'role': role.to_dict(),
                'count': count
            })
        
        # Today's attendance
        today = date.today()
        today_shifts = EmployeeShift.query.filter_by(work_date=today).all()
        attendance = {
            'scheduled': len([s for s in today_shifts if s.status == 'scheduled']),
            'checked_in': len([s for s in today_shifts if s.status == 'checked_in']),
            'checked_out': len([s for s in today_shifts if s.status == 'checked_out']),
            'late': len([s for s in today_shifts if s.status == 'late']),
            'absent': len([s for s in today_shifts if s.status == 'absent'])
        }
        
        return jsonify({
            'success': True,
            'data': {
                'total_employees': total_employees,
                'active_employees': active_employees,
                'inactive_employees': inactive_employees,
                'on_leave_employees': on_leave_employees,
                'role_statistics': role_stats,
                'today_attendance': attendance
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
