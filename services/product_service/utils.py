"""
Product Service - Utility Functions
"""
from datetime import datetime


def parse_date(date_str):
    """Parse date string to date object"""
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            pass
    return None
