"""
Employee Service - Utility Functions
"""
from models import db, Role, WorkShift


def init_defaults():
    """Khởi tạo dữ liệu mặc định cho roles và ca làm việc"""
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


def parse_date(date_str):
    """Parse date string to date object"""
    from datetime import datetime
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            pass
    return None
