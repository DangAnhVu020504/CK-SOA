"""
Customer Service Models
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class MemberRank(db.Model):
    """Model cho bảng hạng thành viên"""
    __tablename__ = 'member_ranks'
    
    id = db.Column(db.Integer, primary_key=True)
    rank_name = db.Column(db.String(50), nullable=False)
    min_points = db.Column(db.Integer, default=0)
    discount_percent = db.Column(db.Numeric(5, 2), default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customers = db.relationship('Customer', backref='rank', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'rank_name': self.rank_name,
            'min_points': self.min_points,
            'discount_percent': float(self.discount_percent) if self.discount_percent else 0,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Customer(db.Model):
    """Model cho bảng khách hàng"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('male', 'female', 'other'), default='other')
    points = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Numeric(15, 2), default=0)
    rank_id = db.Column(db.Integer, db.ForeignKey('member_ranks.id'), default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchase_history = db.relationship('PurchaseHistory', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_rank=True, include_history=False):
        data = {
            'id': self.id,
            'customer_code': self.customer_code,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'points': self.points,
            'total_spent': float(self.total_spent) if self.total_spent else 0,
            'rank_id': self.rank_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_rank and self.rank:
            data['rank'] = self.rank.to_dict()
            
        if include_history:
            data['purchase_history'] = [p.to_dict() for p in self.purchase_history]
            
        return data
    
    def update_rank(self):
        """Cập nhật hạng thành viên dựa trên điểm"""
        ranks = MemberRank.query.order_by(MemberRank.min_points.desc()).all()
        for rank in ranks:
            if self.points >= rank.min_points:
                self.rank_id = rank.id
                break
        return self.rank_id
    
    def add_points(self, amount, points_per_amount=1000):
        """Tích điểm dựa trên số tiền mua hàng"""
        earned_points = int(amount / points_per_amount)
        self.points += earned_points
        self.total_spent = float(self.total_spent or 0) + amount
        self.update_rank()
        return earned_points
    
    def use_points(self, points_to_use):
        """Sử dụng điểm"""
        if points_to_use <= self.points:
            self.points -= points_to_use
            return True
        return False
    
    @staticmethod
    def generate_customer_code():
        """Tạo mã khách hàng tự động"""
        last_customer = Customer.query.order_by(Customer.id.desc()).first()
        if last_customer:
            last_number = int(last_customer.customer_code[2:])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"KH{new_number:06d}"


class PurchaseHistory(db.Model):
    """Model cho bảng lịch sử mua hàng"""
    __tablename__ = 'purchase_history'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    invoice_code = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    points_used = db.Column(db.Integer, default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    final_amount = db.Column(db.Numeric(15, 2), nullable=False)
    note = db.Column(db.Text)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'invoice_code': self.invoice_code,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'points_earned': self.points_earned,
            'points_used': self.points_used,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'final_amount': float(self.final_amount) if self.final_amount else 0,
            'note': self.note,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None
        }
