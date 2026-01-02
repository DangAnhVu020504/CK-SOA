"""
Sales Service - Utility Functions
"""
import random
import string
from datetime import datetime


def generate_invoice_number():
    """Generate unique invoice number"""
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=4))}"
