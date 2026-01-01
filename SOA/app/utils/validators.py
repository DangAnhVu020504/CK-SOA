# Request validators
from functools import wraps
from flask import request, jsonify


def validate_request_json(required_fields):
    """
    Decorator to validate required JSON fields in request
    
    Usage:
        @validate_request_json(['username', 'password'])
        def login():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Content-Type phải là application/json'
                }), 400
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body không được để trống'
                }), 400
            
            missing_fields = []
            for field in required_fields:
                if field not in data or data[field] is None or data[field] == '':
                    missing_fields.append(field)
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'message': f'Thiếu các trường bắt buộc: {", ".join(missing_fields)}'
                }), 400
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def validate_pagination_params(fn):
    """
    Decorator to validate and parse pagination parameters
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 10
            
            kwargs['page'] = page
            kwargs['per_page'] = per_page
            
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Tham số phân trang không hợp lệ'
            }), 400
        
        return fn(*args, **kwargs)
    return wrapper
