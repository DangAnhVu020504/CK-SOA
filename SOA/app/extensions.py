# Flask extensions initialization
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()


def init_extensions(app):
    """Initialize all Flask extensions with the app"""
    db.init_app(app)
    jwt.init_app(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            'success': False,
            'message': 'Token đã hết hạn',
            'error': 'token_expired'
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'success': False,
            'message': 'Token không hợp lệ',
            'error': 'invalid_token'
        }, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            'success': False,
            'message': 'Yêu cầu xác thực. Vui lòng đăng nhập',
            'error': 'authorization_required'
        }, 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {
            'success': False,
            'message': 'Token đã bị thu hồi',
            'error': 'token_revoked'
        }, 401
