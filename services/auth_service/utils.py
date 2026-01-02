"""
Auth Service - Utility Functions
"""
from models import db, Role, User


def init_default_roles():
    """Khởi tạo các role mặc định"""
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
