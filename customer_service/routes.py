"""
Customer Service Routes - API Endpoints
"""
from flask import Blueprint, request, jsonify
from models import db, Customer, MemberRank, PurchaseHistory
from datetime import datetime

customer_bp = Blueprint('customer', __name__)


# =====================================================
# CUSTOMER ENDPOINTS
# =====================================================

@customer_bp.route('/api/customers', methods=['GET'])
def get_customers():
    """Lấy danh sách tất cả khách hàng"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        customers = Customer.query.filter_by(is_active=True)\
            .order_by(Customer.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in customers.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': customers.total,
                'pages': customers.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@customer_bp.route('/api/customers/<int:id>', methods=['GET'])
def get_customer(id):
    """Lấy thông tin chi tiết một khách hàng"""
    try:
        include_history = request.args.get('include_history', 'false').lower() == 'true'
        customer = Customer.query.get_or_404(id)
        return jsonify({
            'success': True,
            'data': customer.to_dict(include_history=include_history)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404


@customer_bp.route('/api/customers', methods=['POST'])
def create_customer():
    """Thêm khách hàng mới"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('full_name'):
            return jsonify({'success': False, 'error': 'Họ tên là bắt buộc'}), 400
        if not data.get('phone'):
            return jsonify({'success': False, 'error': 'Số điện thoại là bắt buộc'}), 400
        
        # Check if phone already exists
        existing = Customer.query.filter_by(phone=data['phone']).first()
        if existing:
            return jsonify({'success': False, 'error': 'Số điện thoại đã được đăng ký'}), 400
        
        # Create new customer
        customer = Customer(
            customer_code=Customer.generate_customer_code(),
            full_name=data['full_name'],
            phone=data['phone'],
            email=data.get('email'),
            address=data.get('address'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            gender=data.get('gender', 'other'),
            rank_id=1  # Default Bronze rank
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Thêm khách hàng thành công',
            'data': customer.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@customer_bp.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    """Cập nhật thông tin khách hàng"""
    try:
        customer = Customer.query.get_or_404(id)
        data = request.get_json()
        
        # Update fields
        if 'full_name' in data:
            customer.full_name = data['full_name']
        if 'phone' in data:
            # Check if phone already exists for another customer
            existing = Customer.query.filter(Customer.phone == data['phone'], Customer.id != id).first()
            if existing:
                return jsonify({'success': False, 'error': 'Số điện thoại đã được sử dụng'}), 400
            customer.phone = data['phone']
        if 'email' in data:
            customer.email = data['email']
        if 'address' in data:
            customer.address = data['address']
        if 'date_of_birth' in data:
            customer.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data['date_of_birth'] else None
        if 'gender' in data:
            customer.gender = data['gender']
        if 'is_active' in data:
            customer.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật thành công',
            'data': customer.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@customer_bp.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    """Xóa khách hàng (soft delete)"""
    try:
        customer = Customer.query.get_or_404(id)
        customer.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Xóa khách hàng thành công'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@customer_bp.route('/api/customers/search', methods=['GET'])
def search_customers():
    """Tìm kiếm khách hàng"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Vui lòng nhập từ khóa tìm kiếm'}), 400
        
        customers = Customer.query.filter(
            Customer.is_active == True,
            (Customer.full_name.ilike(f'%{query}%')) |
            (Customer.phone.ilike(f'%{query}%')) |
            (Customer.customer_code.ilike(f'%{query}%')) |
            (Customer.email.ilike(f'%{query}%'))
        ).all()
        
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in customers],
            'count': len(customers)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# POINTS MANAGEMENT ENDPOINTS
# =====================================================

@customer_bp.route('/api/customers/<int:id>/add-points', methods=['POST'])
def add_points(id):
    """Tích điểm cho khách hàng"""
    try:
        customer = Customer.query.get_or_404(id)
        data = request.get_json()
        
        if not data.get('amount'):
            return jsonify({'success': False, 'error': 'Số tiền là bắt buộc'}), 400
        
        amount = float(data['amount'])
        points_per_amount = data.get('points_per_amount', 1000)
        
        # Calculate points and update customer
        earned_points = customer.add_points(amount, points_per_amount)
        
        # Create purchase history
        purchase = PurchaseHistory(
            customer_id=customer.id,
            invoice_code=data.get('invoice_code', f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            total_amount=amount,
            points_earned=earned_points,
            points_used=0,
            discount_amount=0,
            final_amount=amount,
            note=data.get('note')
        )
        
        db.session.add(purchase)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Đã tích {earned_points} điểm cho khách hàng',
            'data': {
                'customer': customer.to_dict(),
                'points_earned': earned_points,
                'new_total_points': customer.points,
                'purchase': purchase.to_dict()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@customer_bp.route('/api/customers/<int:id>/use-points', methods=['POST'])
def use_points(id):
    """Sử dụng điểm của khách hàng"""
    try:
        customer = Customer.query.get_or_404(id)
        data = request.get_json()
        
        if not data.get('points'):
            return jsonify({'success': False, 'error': 'Số điểm là bắt buộc'}), 400
        
        points_to_use = int(data['points'])
        
        if points_to_use > customer.points:
            return jsonify({
                'success': False, 
                'error': f'Không đủ điểm. Điểm hiện tại: {customer.points}'
            }), 400
        
        # Calculate discount (1 point = 1000 VND)
        discount_amount = points_to_use * 1000
        
        if customer.use_points(points_to_use):
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Đã sử dụng {points_to_use} điểm',
                'data': {
                    'customer': customer.to_dict(),
                    'points_used': points_to_use,
                    'discount_amount': discount_amount,
                    'remaining_points': customer.points
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Không thể sử dụng điểm'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@customer_bp.route('/api/customers/<int:id>/check-rank', methods=['GET'])
def check_rank(id):
    """Kiểm tra và cập nhật hạng thành viên"""
    try:
        customer = Customer.query.get_or_404(id)
        old_rank_id = customer.rank_id
        new_rank_id = customer.update_rank()
        
        rank_changed = old_rank_id != new_rank_id
        
        if rank_changed:
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'customer': customer.to_dict(),
                'rank_changed': rank_changed,
                'message': 'Chúc mừng! Bạn đã được nâng hạng!' if rank_changed else 'Hạng thành viên không thay đổi'
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# PURCHASE HISTORY ENDPOINTS
# =====================================================

@customer_bp.route('/api/customers/<int:id>/purchase-history', methods=['GET'])
def get_purchase_history(id):
    """Lấy lịch sử mua hàng của khách hàng"""
    try:
        customer = Customer.query.get_or_404(id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        history = PurchaseHistory.query.filter_by(customer_id=id)\
            .order_by(PurchaseHistory.purchase_date.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'customer': customer.to_dict(include_history=False),
                'purchase_history': [p.to_dict() for p in history.items],
                'summary': {
                    'total_purchases': history.total,
                    'total_spent': float(customer.total_spent),
                    'total_points': customer.points
                }
            },
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': history.total,
                'pages': history.pages
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# MEMBER RANKS ENDPOINTS
# =====================================================

@customer_bp.route('/api/ranks', methods=['GET'])
def get_ranks():
    """Lấy danh sách các hạng thành viên"""
    try:
        ranks = MemberRank.query.order_by(MemberRank.min_points.asc()).all()
        return jsonify({
            'success': True,
            'data': [r.to_dict() for r in ranks]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@customer_bp.route('/api/ranks/<int:id>', methods=['GET'])
def get_rank(id):
    """Lấy thông tin một hạng thành viên"""
    try:
        rank = MemberRank.query.get_or_404(id)
        # Get customers in this rank
        customers_count = Customer.query.filter_by(rank_id=id, is_active=True).count()
        
        data = rank.to_dict()
        data['customers_count'] = customers_count
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# STATISTICS ENDPOINTS
# =====================================================

@customer_bp.route('/api/statistics/customers', methods=['GET'])
def get_customer_statistics():
    """Thống kê khách hàng"""
    try:
        total_customers = Customer.query.filter_by(is_active=True).count()
        total_inactive = Customer.query.filter_by(is_active=False).count()
        
        # Count by rank
        ranks = MemberRank.query.all()
        rank_stats = []
        for rank in ranks:
            count = Customer.query.filter_by(rank_id=rank.id, is_active=True).count()
            rank_stats.append({
                'rank': rank.to_dict(),
                'count': count
            })
        
        # Total points in system
        from sqlalchemy import func
        total_points = db.session.query(func.sum(Customer.points)).filter(Customer.is_active == True).scalar() or 0
        total_spent = db.session.query(func.sum(Customer.total_spent)).filter(Customer.is_active == True).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_customers': total_customers,
                'total_inactive': total_inactive,
                'rank_statistics': rank_stats,
                'total_points_in_system': int(total_points),
                'total_revenue': float(total_spent)
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
