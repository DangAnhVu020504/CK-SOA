"""
Customer Service - Utility Functions
"""
from models import db, MemberRank


def init_default_ranks():
    """Khởi tạo các hạng thành viên mặc định"""
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
