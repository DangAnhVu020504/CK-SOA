"""
Employee Service Models
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()


class Role(db.Model):
    """Model cho bảng vai trò/quyền"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    role_code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employees = db.relationship('Employee', backref='role', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'role_name': self.role_name,
            'role_code': self.role_code,
            'description': self.description,
            'permissions': self.permissions if self.permissions else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def has_permission(self, permission):
        """Kiểm tra quyền"""
        if self.permissions:
            return self.permissions.get(permission, False)
        return False


class Employee(db.Model):
    """Model cho bảng nhân viên"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('male', 'female', 'other'), default='other')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    salary = db.Column(db.Numeric(12, 2), default=0)
    hire_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('active', 'inactive', 'on_leave'), default='active')
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shifts = db.relationship('EmployeeShift', backref='employee', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Mã hóa mật khẩu"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Kiểm tra mật khẩu"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_role=True, include_shifts=False):
        data = {
            'id': self.id,
            'employee_code': self.employee_code,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'role_id': self.role_id,
            'salary': float(self.salary) if self.salary else 0,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'status': self.status,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_role and self.role:
            data['role'] = self.role.to_dict()
            
        if include_shifts:
            data['shifts'] = [s.to_dict() for s in self.shifts]
            
        return data
    
    def has_permission(self, permission):
        """Kiểm tra quyền của nhân viên"""
        if self.role:
            return self.role.has_permission(permission)
        return False
    
    @staticmethod
    def generate_employee_code():
        """Tạo mã nhân viên tự động"""
        last_employee = Employee.query.order_by(Employee.id.desc()).first()
        if last_employee:
            last_number = int(last_employee.employee_code[2:])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"NV{new_number:06d}"


class WorkShift(db.Model):
    """Model cho bảng ca làm việc"""
    __tablename__ = 'work_shifts'
    
    id = db.Column(db.Integer, primary_key=True)
    shift_name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee_shifts = db.relationship('EmployeeShift', backref='shift', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'shift_name': self.shift_name,
            'start_time': self.start_time.strftime('%H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M:%S') if self.end_time else None,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class EmployeeShift(db.Model):
    """Model cho bảng phân công ca làm việc"""
    __tablename__ = 'employee_shifts'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('work_shifts.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    status = db.Column(db.Enum('scheduled', 'checked_in', 'checked_out', 'absent', 'late'), default='scheduled')
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_shift=True, include_employee=False):
        data = {
            'id': self.id,
            'employee_id': self.employee_id,
            'shift_id': self.shift_id,
            'work_date': self.work_date.isoformat() if self.work_date else None,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'status': self.status,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_shift and self.shift:
            data['shift'] = self.shift.to_dict()
            
        if include_employee and self.employee:
            data['employee'] = self.employee.to_dict(include_role=True, include_shifts=False)
            
        return data
    
    def check_in(self):
        """Chấm công vào ca"""
        self.check_in_time = datetime.now()
        
        # Check if late (more than 15 minutes after shift start)
        if self.shift:
            from datetime import time, timedelta
            shift_start = datetime.combine(self.work_date, self.shift.start_time)
            grace_period = timedelta(minutes=15)
            
            if self.check_in_time > shift_start + grace_period:
                self.status = 'late'
            else:
                self.status = 'checked_in'
        else:
            self.status = 'checked_in'
        
        return self.status
    
    def check_out(self):
        """Chấm công ra ca"""
        self.check_out_time = datetime.now()
        self.status = 'checked_out'
        return self.status
    
    def calculate_worked_hours(self):
        """Tính số giờ làm việc"""
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            return round(delta.total_seconds() / 3600, 2)
        return 0
