"""
Customer Service - API Routes
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from models import db, Customer, MemberRank

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/health', methods=['GET'])
def health_check():
    from flask import current_app
    return jsonify({
        'status': 'healthy',
        'service': 'customer_service',
        'port': 5005,
        'database': 'MySQL' if 'mysql' in current_app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@customer_bp.route('/api/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.filter_by(is_active=True).all()
    return jsonify({'success': True, 'data': [c.to_dict() for c in customers]}), 200


@customer_bp.route('/api/customers/by-phone/<phone>', methods=['GET'])
def get_customer_by_phone(phone):
    """Find customer by phone number"""
    customer = Customer.query.filter_by(phone=phone, is_active=True).first()
    if customer:
        return jsonify({'success': True, 'found': True, 'data': customer.to_dict()}), 200
    return jsonify({'success': True, 'found': False, 'data': None}), 200


@customer_bp.route('/api/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({'success': True, 'data': customer.to_dict()}), 200


@customer_bp.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    if not data.get('full_name') or not data.get('phone'):
        return jsonify({'success': False, 'message': 'Tên và SĐT là bắt buộc'}), 400
    
    customer = Customer(
        code=f"KH{datetime.now().strftime('%Y%m%d%H%M%S')}",
        full_name=data['full_name'],
        phone=data['phone'],
        email=data.get('email'),
        address=data.get('address'),
        rank_id=1
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({'success': True, 'data': customer.to_dict()}), 201


@customer_bp.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    for field in ['full_name', 'email', 'address', 'phone', 'points', 'total_spent']:
        if field in data:
            setattr(customer, field, data[field])
    db.session.commit()
    return jsonify({'success': True, 'data': customer.to_dict()}), 200


@customer_bp.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    customer.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Xóa thành công'}), 200


@customer_bp.route('/api/customers/<int:id>/add-points', methods=['POST'])
def add_points(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    customer.points += data.get('points', 0)
    customer.total_spent += data.get('amount', 0)
    
    new_rank = MemberRank.query.filter(
        MemberRank.min_points <= customer.points
    ).order_by(MemberRank.min_points.desc()).first()
    if new_rank:
        customer.rank_id = new_rank.id
    db.session.commit()
    return jsonify({'success': True, 'data': customer.to_dict()}), 200


@customer_bp.route('/api/customers/<int:id>/use-points', methods=['POST'])
def use_points(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    points = data.get('points', 0)
    if customer.points < points:
        return jsonify({'success': False, 'message': 'Không đủ điểm'}), 400
    customer.points -= points
    db.session.commit()
    return jsonify({'success': True, 'data': customer.to_dict()}), 200


@customer_bp.route('/api/customers/ranks', methods=['GET'])
def get_ranks():
    ranks = MemberRank.query.order_by(MemberRank.min_points).all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in ranks]}), 200


@customer_bp.route('/api/customers/statistics', methods=['GET'])
def get_statistics():
    total = Customer.query.filter_by(is_active=True).count()
    return jsonify({'success': True, 'data': {'total_customers': total}}), 200


@customer_bp.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
