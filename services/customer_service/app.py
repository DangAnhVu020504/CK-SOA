"""
Customer Service - Quản lý khách hàng & Loyalty
Port: 5005
Database: MySQL (customer_db)
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
services_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(services_dir)
sys.path.insert(0, root_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(root_dir, '.env'))

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'customer-service-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'CUSTOMER_DB_URL',
    f'sqlite:///{current_dir}/customer_service.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280, 'pool_pre_ping': True}

CORS(app)
db = SQLAlchemy(app)


class MemberRank(db.Model):
    __tablename__ = 'member_ranks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    min_points = db.Column(db.Integer, default=0)
    discount_percent = db.Column(db.Float, default=0)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'min_points': self.min_points, 'discount_percent': self.discount_percent}


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    points = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0)
    rank_id = db.Column(db.Integer, db.ForeignKey('member_ranks.id'), default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    rank = db.relationship('MemberRank', backref='customers')
    
    def to_dict(self):
        return {
            'id': self.id, 'code': self.code, 'full_name': self.full_name,
            'phone': self.phone, 'email': self.email, 'points': self.points,
            'total_spent': self.total_spent, 'rank': self.rank.name if self.rank else 'Member',
            'is_active': self.is_active
        }


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 'service': 'customer_service', 'port': 5005,
        'database': 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.filter_by(is_active=True).all()
    return jsonify({'success': True, 'data': [c.to_dict() for c in customers]}), 200


@app.route('/api/customers/by-phone/<phone>', methods=['GET'])
def get_customer_by_phone(phone):
    """Find customer by phone number"""
    customer = Customer.query.filter_by(phone=phone, is_active=True).first()
    if customer:
        return jsonify({'success': True, 'found': True, 'data': customer.to_dict()}), 200
    return jsonify({'success': True, 'found': False, 'data': None}), 200


@app.route('/api/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({'success': True, 'data': customer.to_dict()}), 200


@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    if not data.get('full_name') or not data.get('phone'):
        return jsonify({'success': False, 'message': 'Tên và SĐT là bắt buộc'}), 400
    
    customer = Customer(
        code=f"KH{datetime.now().strftime('%Y%m%d%H%M%S')}",
        full_name=data['full_name'], phone=data['phone'],
        email=data.get('email'), address=data.get('address'), rank_id=1
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({'success': True, 'data': customer.to_dict()}), 201


@app.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    for field in ['full_name', 'email', 'address', 'phone', 'points', 'total_spent']:
        if field in data:
            setattr(customer, field, data[field])
    db.session.commit()
    return jsonify({'success': True, 'data': customer.to_dict()}), 200


@app.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    customer.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Xóa thành công'}), 200


@app.route('/api/customers/<int:id>/add-points', methods=['POST'])
def add_points(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    customer.points += data.get('points', 0)
    customer.total_spent += data.get('amount', 0)
    
    new_rank = MemberRank.query.filter(MemberRank.min_points <= customer.points).order_by(MemberRank.min_points.desc()).first()
    if new_rank:
        customer.rank_id = new_rank.id
    db.session.commit()
    return jsonify({'success': True, 'data': customer.to_dict()}), 200


@app.route('/api/customers/<int:id>/use-points', methods=['POST'])
def use_points(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    points = data.get('points', 0)
    if customer.points < points:
        return jsonify({'success': False, 'message': 'Không đủ điểm'}), 400
    customer.points -= points
    db.session.commit()
    return jsonify({'success': True, 'data': customer.to_dict()}), 200


@app.route('/api/customers/ranks', methods=['GET'])
def get_ranks():
    ranks = MemberRank.query.order_by(MemberRank.min_points).all()
    return jsonify({'success': True, 'data': [r.to_dict() for r in ranks]}), 200


@app.route('/api/customers/statistics', methods=['GET'])
def get_statistics():
    total = Customer.query.filter_by(is_active=True).count()
    return jsonify({'success': True, 'data': {'total_customers': total}}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404


def init_default_ranks():
    defaults = [
        {'name': 'Member', 'min_points': 0, 'discount_percent': 0},
        {'name': 'Silver', 'min_points': 1000, 'discount_percent': 3},
        {'name': 'Gold', 'min_points': 5000, 'discount_percent': 5},
        {'name': 'Platinum', 'min_points': 10000, 'discount_percent': 10}
    ]
    for r in defaults:
        if not MemberRank.query.filter_by(name=r['name']).first():
            db.session.add(MemberRank(**r))
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_default_ranks()
    
    try:
        from shared.consul_utils import register_flask_service
        register_flask_service(app, 'customer_service', 5005, ['customer', 'loyalty'])
    except Exception as e:
        print(f"Warning: Could not register with Consul: {e}")
    
    db_type = 'MySQL' if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    print("=" * 50)
    print(f"  Customer Service running on port 5005")
    print(f"  Database: {db_type}")
    print("=" * 50)
    app.run(debug=True, port=5005, host='0.0.0.0')
