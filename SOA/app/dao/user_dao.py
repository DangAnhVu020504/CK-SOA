# User Data Access Object
from app.extensions import db
from app.models.user import User


class UserDAO:
    """Data Access Object for User operations"""
    
    @staticmethod
    def create(username, email, password, role_id, **kwargs):
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            password=password,
            role_id=role_id,
            full_name=kwargs.get('full_name'),
            phone=kwargs.get('phone'),
            address=kwargs.get('address')
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all(page=1, per_page=10, include_inactive=False):
        """Get all users with pagination"""
        query = User.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_role(role_id, page=1, per_page=10):
        """Get users by role with pagination"""
        return User.query.filter_by(role_id=role_id, is_active=True)\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def update(user_id, **kwargs):
        """Update user information"""
        user = User.query.get(user_id)
        if user:
            for key, value in kwargs.items():
                if key == 'password':
                    user.set_password(value)
                elif hasattr(user, key) and key not in ['id', 'created_at', 'password_hash']:
                    setattr(user, key, value)
            db.session.commit()
        return user
    
    @staticmethod
    def delete(user_id):
        """Soft delete a user (set inactive)"""
        user = User.query.get(user_id)
        if user:
            user.is_active = False
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def hard_delete(user_id):
        """Permanently delete a user"""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def username_exists(username):
        """Check if username already exists"""
        return User.query.filter_by(username=username).first() is not None
    
    @staticmethod
    def email_exists(email):
        """Check if email already exists"""
        return User.query.filter_by(email=email).first() is not None
    
    @staticmethod
    def count_users(include_inactive=False):
        """Count total users"""
        query = User.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.count()
    
    @staticmethod
    def search(keyword, page=1, per_page=10):
        """Search users by username, email, or full_name"""
        search_pattern = f"%{keyword}%"
        return User.query.filter(
            db.or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern)
            ),
            User.is_active == True
        ).paginate(page=page, per_page=per_page, error_out=False)
