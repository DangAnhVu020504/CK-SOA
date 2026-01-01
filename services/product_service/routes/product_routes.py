"""
Product Routes
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from flask import Blueprint, request, jsonify
from shared.utils import handle_exceptions, success_response, error_response
from shared.exceptions import ProductNotFound, InvalidInput
from shared.database import db
from models.product_model import Product

product_bp = Blueprint('products', __name__)

# ============ GET Methods ============

@product_bp.route('/', methods=['GET'])
@handle_exceptions
def get_all_products():
    """Lấy danh sách tất cả sản phẩm"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category', None)
    
    query = Product.query.filter_by(status='active')
    
    if category:
        query = query.filter_by(category=category)
    
    paginated = query.paginate(page=page, per_page=per_page)
    
    products = [p.to_dict() for p in paginated.items]
    
    return success_response({
        'products': products,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }, message="Lấy danh sách sản phẩm thành công")

@product_bp.route('/<int:product_id>', methods=['GET'])
@handle_exceptions
def get_product(product_id):
    """Lấy chi tiết sản phẩm"""
    product = Product.query.get(product_id)
    
    if not product or product.status == 'deleted':
        raise ProductNotFound()
    
    return success_response(product.to_dict(), message="Lấy chi tiết sản phẩm thành công")

@product_bp.route('/by-sku/<sku>', methods=['GET'])
@handle_exceptions
def get_product_by_sku(sku):
    """Lấy sản phẩm theo SKU"""
    product = Product.query.filter_by(sku=sku, status='active').first()
    
    if not product:
        raise ProductNotFound(f"Sản phẩm SKU {sku} không tìm thấy")
    
    return success_response(product.to_dict(), message="Lấy sản phẩm theo SKU thành công")

@product_bp.route('/by-barcode/<barcode>', methods=['GET'])
@handle_exceptions
def get_product_by_barcode(barcode):
    """Lấy sản phẩm theo mã vạch"""
    product = Product.query.filter_by(barcode=barcode, status='active').first()
    
    if not product:
        raise ProductNotFound(f"Sản phẩm barcode {barcode} không tìm thấy")
    
    return success_response(product.to_dict(), message="Lấy sản phẩm theo barcode thành công")

# ============ POST Methods ============

@product_bp.route('/', methods=['POST'])
@handle_exceptions
def create_product():
    """Tạo sản phẩm mới"""
    data = request.get_json()
    
    # Validation
    required_fields = ['sku', 'name', 'category', 'price', 'barcode']
    if not all(field in data for field in required_fields):
        raise InvalidInput(f"Thiếu các trường bắt buộc: {', '.join(required_fields)}")
    
    # Kiểm tra SKU trùng lặp
    if Product.query.filter_by(sku=data['sku']).first():
        raise InvalidInput(f"SKU {data['sku']} đã tồn tại")
    
    # Kiểm tra barcode trùng lặp
    if Product.query.filter_by(barcode=data['barcode']).first():
        raise InvalidInput(f"Barcode {data['barcode']} đã tồn tại")
    
    product = Product(
        sku=data['sku'],
        name=data['name'],
        description=data.get('description', ''),
        category=data['category'],
        price=data['price'],
        cost=data.get('cost'),
        barcode=data['barcode'],
        unit=data.get('unit', 'cái'),
        supplier_id=data.get('supplier_id')
    )
    
    db.session.add(product)
    db.session.commit()
    
    return success_response(product.to_dict(), message="Tạo sản phẩm thành công", status_code=201)

# ============ PUT Methods ============

@product_bp.route('/<int:product_id>', methods=['PUT'])
@handle_exceptions
def update_product(product_id):
    """Cập nhật sản phẩm"""
    product = Product.query.get(product_id)
    
    if not product or product.status == 'deleted':
        raise ProductNotFound()
    
    data = request.get_json()
    
    # Cập nhật các trường
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'category' in data:
        product.category = data['category']
    if 'price' in data:
        product.price = data['price']
    if 'cost' in data:
        product.cost = data['cost']
    if 'unit' in data:
        product.unit = data['unit']
    if 'supplier_id' in data:
        product.supplier_id = data['supplier_id']
    
    db.session.commit()
    
    return success_response(product.to_dict(), message="Cập nhật sản phẩm thành công")

# ============ DELETE Methods ============

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@handle_exceptions
def delete_product(product_id):
    """Xóa sản phẩm (soft delete)"""
    product = Product.query.get(product_id)
    
    if not product:
        raise ProductNotFound()
    
    product.status = 'deleted'
    db.session.commit()
    
    return success_response(None, message="Xóa sản phẩm thành công")

# ============ SEARCH Methods ============

@product_bp.route('/search', methods=['POST'])
@handle_exceptions
def search_products():
    """Tìm kiếm sản phẩm"""
    data = request.get_json()
    keyword = data.get('keyword', '')
    category = data.get('category', None)
    
    query = Product.query.filter_by(status='active')
    
    if keyword:
        query = query.filter(
            db.or_(
                Product.name.contains(keyword),
                Product.sku.contains(keyword),
                Product.barcode.contains(keyword)
            )
        )
    
    if category:
        query = query.filter_by(category=category)
    
    products = [p.to_dict() for p in query.all()]
    
    return success_response({
        'products': products,
        'total': len(products)
    }, message="Tìm kiếm sản phẩm thành công")
