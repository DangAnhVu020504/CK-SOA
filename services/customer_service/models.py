"""
Customer Service - Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class MemberRank(db.Model):
    __tablename__ = 'member_ranks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    min_points = db.Column(db.Integer, default=0)
    discount_percent = db.Column(db.Float, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'min_points': self.min_points,
            'discount_percent': self.discount_percent
        }


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
            'id': self.id,
            'code': self.code,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'points': self.points,
            'total_spent': self.total_spent,
            'rank': self.rank.name if self.rank else 'Member',
            'is_active': self.is_active
        }
