"""
Database initialization - chứa các model chung
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.mysql import LONGTEXT

db = SQLAlchemy()

class TimestampMixin:
    """Mixin để thêm created_at và updated_at"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class StatusMixin:
    """Mixin để quản lý trạng thái"""
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive, deleted
