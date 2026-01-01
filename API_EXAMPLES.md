"""
API Examples - Các ví dụ request/response cho hệ thống
"""

# ============================================================
# PRODUCT SERVICE EXAMPLES
# ============================================================

# 1. Lấy danh sách sản phẩm
GET http://localhost:5000/api/products?page=1&per_page=10

Response:
{
  "success": true,
  "message": "Lấy danh sách sản phẩm thành công",
  "data": {
    "products": [
      {
        "id": 1,
        "sku": "SKU001",
        "name": "Nước ngọt Coca 1.5L",
        "description": "Nước ngọt có ga",
        "category": "Đồ uống",
        "price": 25000,
        "cost": 15000,
        "barcode": "8936073028429",
        "unit": "chai",
        "supplier_id": 1,
        "status": "active",
        "created_at": "2024-12-19T10:00:00",
        "updated_at": "2024-12-19T10:00:00"
      }
    ],
    "total": 1,
    "pages": 1,
    "current_page": 1
  }
}

# 2. Tạo sản phẩm mới
POST http://localhost:5000/api/products
Content-Type: application/json

{
  "sku": "SKU001",
  "name": "Nước ngọt Coca 1.5L",
  "description": "Nước ngọt có ga",
  "category": "Đồ uống",
  "price": 25000,
  "cost": 15000,
  "barcode": "8936073028429",
  "unit": "chai",
  "supplier_id": 1
}

Response: 201 Created
{
  "success": true,
  "message": "Tạo sản phẩm thành công",
  "data": {
    "id": 1,
    "sku": "SKU001",
    "name": "Nước ngọt Coca 1.5L",
    ...
  }
}

# 3. Tìm sản phẩm theo barcode
GET http://localhost:5000/api/products/by-barcode/8936073028429

Response:
{
  "success": true,
  "message": "Lấy sản phẩm theo barcode thành công",
  "data": {
    "id": 1,
    "sku": "SKU001",
    "name": "Nước ngọt Coca 1.5L",
    ...
  }
}

# 4. Cập nhật sản phẩm
PUT http://localhost:5000/api/products/1
Content-Type: application/json

{
  "name": "Nước ngọt Coca 1.5L (cập nhật)",
  "price": 26000
}

Response:
{
  "success": true,
  "message": "Cập nhật sản phẩm thành công",
  "data": {
    "id": 1,
    "name": "Nước ngọt Coca 1.5L (cập nhật)",
    "price": 26000,
    ...
  }
}

# ============================================================
# INVENTORY SERVICE EXAMPLES
# ============================================================

# 1. Khởi tạo tồn kho cho sản phẩm
POST http://localhost:5000/api/inventory/init
Content-Type: application/json

{
  "product_id": 1,
  "quantity_on_hand": 100,
  "reorder_level": 20,
  "location": "Kệ A1"
}

Response: 201 Created
{
  "success": true,
  "message": "Khởi tạo tồn kho thành công",
  "data": {
    "id": 1,
    "product_id": 1,
    "quantity_on_hand": 100,
    "quantity_available": 100,
    "reorder_level": 20,
    "location": "Kệ A1",
    ...
  }
}

# 2. Lấy tồn kho của sản phẩm
GET http://localhost:5000/api/inventory/by-product/1

Response:
{
  "success": true,
  "message": "Lấy tồn kho thành công",
  "data": {
    "product_id": 1,
    "quantity_on_hand": 100,
    "quantity_reserved": 10,
    "quantity_available": 90
  }
}

# 3. Điều chỉnh tồn kho
POST http://localhost:5000/api/inventory/adjust
Content-Type: application/json

{
  "product_id": 1,
  "quantity": -5,
  "reason": "Hàng lỗi, loại bỏ"
}

Response:
{
  "success": true,
  "message": "Điều chỉnh tồn kho thành công",
  "data": {
    "product_id": 1,
    "quantity_on_hand": 95,
    "quantity_available": 85,
    ...
  }
}

# 4. Lấy sản phẩm sắp hết
GET http://localhost:5000/api/inventory/low-stock

Response:
{
  "success": true,
  "message": "Lấy danh sách sản phẩm sắp hết thành công",
  "data": {
    "low_stock_items": [
      {
        "product_id": 5,
        "quantity_available": 15,
        "reorder_level": 20,
        ...
      }
    ],
    "total": 1
  }
}

# 5. Thêm cảnh báo hạn sử dụng
POST http://localhost:5000/api/inventory/add-expiry-warning
Content-Type: application/json

{
  "product_id": 1,
  "batch_number": "BATCH001",
  "expiry_date": "2024-12-31T23:59:59",
  "quantity": 50
}

Response: 201 Created
{
  "success": true,
  "message": "Thêm cảnh báo hạn sử dụng thành công",
  "data": {
    "product_id": 1,
    "batch_number": "BATCH001",
    "expiry_date": "2024-12-31T23:59:59",
    "quantity": 50,
    "warning_level": "warning",
    ...
  }
}

# 6. Lấy cảnh báo hạn sử dụng
GET http://localhost:5000/api/inventory/expiry-warnings?days=30

Response:
{
  "success": true,
  "message": "Lấy cảnh báo hạn sử dụng thành công",
  "data": {
    "warnings": [
      {
        "product_id": 1,
        "batch_number": "BATCH001",
        "expiry_date": "2024-12-31T23:59:59",
        "quantity": 50,
        "warning_level": "warning",
        ...
      }
    ],
    "total": 1
  }
}

# ============================================================
# SALES SERVICE EXAMPLES
# ============================================================

# 1. Tạo hóa đơn mới
POST http://localhost:5000/api/sales/invoices
Content-Type: application/json

{
  "invoice_number": "INV001",
  "cashier_id": 1,
  "discount": 0,
  "payment_method": "cash",
  "items": [
    {
      "product_id": 1,
      "product_name": "Nước ngọt Coca 1.5L",
      "barcode": "8936073028429",
      "sku": "SKU001",
      "quantity": 2,
      "unit_price": 25000
    },
    {
      "product_id": 2,
      "product_name": "Bánh mì 30g",
      "barcode": "8935052001234",
      "sku": "SKU002",
      "quantity": 3,
      "unit_price": 10000
    }
  ]
}

Response: 201 Created
{
  "success": true,
  "message": "Tạo hóa đơn thành công",
  "data": {
    "id": 1,
    "invoice_number": "INV001",
    "cashier_id": 1,
    "subtotal": 80000,
    "discount": 0,
    "total_amount": 80000,
    "payment_method": "cash",
    "status": "active",
    "created_at": "2024-12-19T10:15:00",
    ...
  }
}

# 2. Thêm sản phẩm vào hóa đơn
POST http://localhost:5000/api/sales/invoices/1/add-item
Content-Type: application/json

{
  "product_id": 3,
  "product_name": "Nước lọc Aquafina 500ml",
  "barcode": "8936076012345",
  "sku": "SKU003",
  "quantity": 1,
  "unit_price": 5000
}

Response:
{
  "success": true,
  "message": "Thêm sản phẩm vào hóa đơn thành công",
  "data": {
    "id": 1,
    "invoice_number": "INV001",
    "subtotal": 85000,
    "total_amount": 85000,
    ...
  }
}

# 3. Hoàn thành hóa đơn (Checkout)
PUT http://localhost:5000/api/sales/invoices/1/checkout
Content-Type: application/json

{
  "paid_amount": 100000,
  "payment_method": "cash"
}

Response:
{
  "success": true,
  "message": "Hoàn thành hóa đơn thành công",
  "data": {
    "id": 1,
    "invoice_number": "INV001",
    "total_amount": 85000,
    "paid_amount": 100000,
    "change_amount": 15000,
    "status": "completed",
    ...
  }
}

# 4. Lấy chi tiết hóa đơn
GET http://localhost:5000/api/sales/invoices/1

Response:
{
  "success": true,
  "message": "Lấy chi tiết hóa đơn thành công",
  "data": {
    "id": 1,
    "invoice_number": "INV001",
    "subtotal": 85000,
    "total_amount": 85000,
    "status": "completed",
    "details": [
      {
        "id": 1,
        "product_id": 1,
        "product_name": "Nước ngọt Coca 1.5L",
        "quantity": 2,
        "unit_price": 25000,
        "line_total": 50000
      },
      ...
    ],
    ...
  }
}

# 5. Thống kê doanh thu
GET http://localhost:5000/api/sales/revenue?start_date=2024-12-01&end_date=2024-12-31

Response:
{
  "success": true,
  "message": "Lấy thống kê doanh thu thành công",
  "data": {
    "total_revenue": 5000000,
    "total_discount": 50000,
    "invoice_count": 120,
    "average_invoice": 41666.67
  }
}

# ============================================================
# SUPPLIER SERVICE EXAMPLES
# ============================================================

# 1. Tạo nhà cung cấp mới
POST http://localhost:5000/api/suppliers
Content-Type: application/json

{
  "name": "Công ty TNHH ABC",
  "code": "SUP001",
  "email": "abc@example.com",
  "phone": "0234567890",
  "address": "123 Đường Lê Lợi",
  "city": "TP. HCM",
  "postal_code": "70000",
  "contact_person": "Nguyễn Văn A",
  "contact_phone": "0912345678",
  "payment_terms": "NET30",
  "shipping_cost": 50000
}

Response: 201 Created
{
  "success": true,
  "message": "Tạo nhà cung cấp thành công",
  "data": {
    "id": 1,
    "name": "Công ty TNHH ABC",
    "code": "SUP001",
    ...
  }
}

# 2. Tạo đơn nhập hàng
POST http://localhost:5000/api/suppliers/purchase-orders
Content-Type: application/json

{
  "po_number": "PO001",
  "supplier_id": 1,
  "expected_delivery_date": "2024-12-25T00:00:00",
  "tax": 0,
  "items": [
    {
      "product_id": 1,
      "product_name": "Nước ngọt Coca 1.5L",
      "sku": "SKU001",
      "ordered_quantity": 100,
      "unit_price": 15000,
      "expiry_date": "2025-12-31T23:59:59",
      "batch_number": "BATCH001"
    },
    {
      "product_id": 2,
      "product_name": "Bánh mì 30g",
      "sku": "SKU002",
      "ordered_quantity": 500,
      "unit_price": 6000,
      "expiry_date": "2025-01-31T23:59:59",
      "batch_number": "BATCH002"
    }
  ]
}

Response: 201 Created
{
  "success": true,
  "message": "Tạo đơn nhập hàng thành công",
  "data": {
    "id": 1,
    "po_number": "PO001",
    "supplier_id": 1,
    "order_date": "2024-12-19T10:30:00",
    "subtotal": 3000000,
    "shipping_cost": 50000,
    "total_amount": 3050000,
    "status": "pending",
    ...
  }
}

# 3. Nhận hàng từ PO
PUT http://localhost:5000/api/suppliers/purchase-orders/1/receive
Content-Type: application/json

{
  "items": [
    {
      "id": 1,
      "received_quantity": 100
    },
    {
      "id": 2,
      "received_quantity": 500
    }
  ]
}

Response:
{
  "success": true,
  "message": "Nhận hàng thành công",
  "data": {
    "id": 1,
    "po_number": "PO001",
    "actual_delivery_date": "2024-12-22T10:45:00",
    "status": "completed",
    ...
  }
}

# 4. Thanh toán PO
PUT http://localhost:5000/api/suppliers/purchase-orders/1/pay
Content-Type: application/json

{
  "amount": 3050000
}

Response:
{
  "success": true,
  "message": "Thanh toán thành công",
  "data": {
    "id": 1,
    "po_number": "PO001",
    "paid_amount": 3050000,
    "payment_status": "paid",
    ...
  }
}

# ============================================================
# GATEWAY HEALTH CHECK
# ============================================================

# Kiểm tra trạng thái tất cả services
GET http://localhost:5000/health

Response:
{
  "status": "healthy",
  "services": {
    "product_service": true,
    "inventory_service": true,
    "sales_service": true,
    "supplier_service": true
  }
}
