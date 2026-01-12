"""
Product Service - API Routes
"""
from flask import Blueprint, jsonify, request
from models import db, Product
from utils import parse_date

product_bp = Blueprint('product', __name__)


@product_bp.route('/health', methods=['GET'])
def health_check():
    from flask import current_app
    return jsonify({
        'status': 'healthy',
        'service': 'product_service',
        'port': 5001,
        'database': 'MySQL' if 'mysql' in current_app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'
    }), 200


@product_bp.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in products],
        'count': len(products)
    }), 200


@product_bp.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': product.to_dict()
    }), 200


@product_bp.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    
    if not data.get('name') or not data.get('sku'):
        return jsonify({'success': False, 'message': 'Tên và SKU là bắt buộc'}), 400
    
    product = Product(
        sku=data['sku'],
        barcode=data.get('barcode'),
        name=data['name'],
        description=data.get('description'),
        category=data.get('category'),
        unit=data.get('unit', 'cái'),
        cost_price=data.get('cost_price') or data.get('cost', 0),
        selling_price=data.get('selling_price') or data.get('price', 0),
        quantity=data.get('quantity', 0),
        supplier_id=data.get('supplier_id'),
        manufacturing_date=parse_date(data.get('manufacturing_date')),
        expiry_date=parse_date(data.get('expiry_date'))
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Tạo sản phẩm thành công',
        'data': product.to_dict()
    }), 201


@product_bp.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'category' in data:
        product.category = data['category']
    if 'unit' in data:
        product.unit = data['unit']
    if 'cost_price' in data or 'cost' in data:
        product.cost_price = data.get('cost_price') or data.get('cost', 0)
    if 'selling_price' in data or 'price' in data:
        product.selling_price = data.get('selling_price') or data.get('price', 0)
    if 'barcode' in data:
        product.barcode = data['barcode']
    if 'supplier_id' in data:
        product.supplier_id = data['supplier_id']
    if 'manufacturing_date' in data:
        product.manufacturing_date = parse_date(data['manufacturing_date']) if data['manufacturing_date'] else None
    if 'expiry_date' in data:
        product.expiry_date = parse_date(data['expiry_date']) if data['expiry_date'] else None
    if 'quantity' in data:
        product.quantity = data['quantity']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Cập nhật sản phẩm thành công',
        'data': product.to_dict()
    }), 200


@product_bp.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    product.is_active = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Xóa sản phẩm thành công'
    }), 200


@product_bp.route('/api/products/by-barcode/<barcode>', methods=['GET'])
def get_by_barcode(barcode):
    product = Product.query.filter_by(barcode=barcode, is_active=True).first()
    if not product:
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    return jsonify({'success': True, 'data': product.to_dict()}), 200


@product_bp.route('/api/products/by-sku/<sku>', methods=['GET'])
def get_by_sku(sku):
    product = Product.query.filter_by(sku=sku, is_active=True).first()
    if not product:
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    return jsonify({'success': True, 'data': product.to_dict()}), 200


@product_bp.route('/api/products/<int:id>/update-quantity', methods=['PUT'])
def update_quantity(id):
    """Cập nhật số lượng sản phẩm (dùng khi bán hàng hoặc nhập hàng)"""
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    quantity_change = data.get('quantity_change', 0)
    operation = data.get('operation', 'set')  # 'add', 'subtract', 'set'
    
    if operation == 'add':
        product.quantity += quantity_change
    elif operation == 'subtract':
        if product.quantity < quantity_change:
            return jsonify({'success': False, 'message': 'Không đủ số lượng trong kho'}), 400
        product.quantity -= quantity_change
    else:  # set
        product.quantity = data.get('quantity', product.quantity)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Cập nhật số lượng thành công',
        'data': product.to_dict()
    }), 200


@product_bp.route('/api/products/low-stock', methods=['GET'])
def get_low_stock_products():
    """Lấy danh sách sản phẩm sắp hết hàng (quantity <= 50)"""
    threshold = request.args.get('threshold', Product.LOW_STOCK_THRESHOLD, type=int)
    products = Product.query.filter(
        Product.is_active == True,
        Product.quantity <= threshold,
        Product.quantity > 0
    ).all()
    
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in products],
        'count': len(products)
    }), 200


@product_bp.route('/api/products/out-of-stock', methods=['GET'])
def get_out_of_stock_products():
    """Lấy danh sách sản phẩm hết hàng (quantity = 0)"""
    products = Product.query.filter(
        Product.is_active == True,
        Product.quantity <= 0
    ).all()
    
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in products],
        'count': len(products)
    }), 200


@product_bp.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404


@product_bp.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'message': 'Lỗi server'}), 500
