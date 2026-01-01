"""
Utilities cho các services
"""
from functools import wraps
from flask import jsonify
from shared.exceptions import ServiceException

def handle_exceptions(f):
    """Decorator để xử lý exceptions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ServiceException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'data': None
            }), e.status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e),
                'data': None
            }), 500
    return decorated_function

def success_response(data=None, message="Success", status_code=200):
    """Tạo response thành công"""
    return jsonify({
        'success': True,
        'message': message,
        'data': data
    }), status_code

def error_response(message="Error", status_code=400, data=None):
    """Tạo response lỗi"""
    return jsonify({
        'success': False,
        'message': message,
        'data': data
    }), status_code
