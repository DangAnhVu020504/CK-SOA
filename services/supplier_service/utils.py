"""
Supplier Service - Utility Functions
"""
from datetime import datetime


def generate_order_number():
    """Generate unique purchase order number"""
    return f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
