# Mini Supermarket Management System - SOA Architecture

Ứng dụng quản lý siêu thị mini với kiến trúc Service-Oriented Architecture (SOA) sử dụng Python Flask.

## Kiến Trúc Hệ Thống

```
Mini Supermarket App
├── gateway/              # API Gateway (Port 5000)
├── services/
│   ├── product_service/         # Quản lý sản phẩm (Port 5001)
│   ├── inventory_service/       # Quản lý tồn kho (Port 5002)
│   ├── sales_service/           # Quản lý bán hàng POS (Port 5003)
│   └── supplier_service/        # Quản lý nhà cung cấp (Port 5004)
├── shared/              # Code chung (utils, exceptions, database)
├── templates/           # Frontend templates
├── static/              # CSS, JS, images
├── config.py           # Cấu hình chung
└── requirements.txt    # Dependencies
```

## Các Service

### 1. **Product Service** (Port 5001)
**Chức năng:**
- ✓ Thêm/Sửa/Xóa sản phẩm
- ✓ Quản lý danh mục sản phẩm
- ✓ Tìm kiếm sản phẩm theo SKU/Barcode
- ✓ Lấy thông tin chi tiết sản phẩm

**Models:**
- `Product`: Thông tin sản phẩm (SKU, Name, Price, Barcode, Category...)

**API Endpoints:**
```
GET    /api/products              - Lấy danh sách sản phẩm
POST   /api/products              - Tạo sản phẩm mới
GET    /api/products/<id>         - Lấy chi tiết sản phẩm
PUT    /api/products/<id>         - Cập nhật sản phẩm
DELETE /api/products/<id>         - Xóa sản phẩm
GET    /api/products/by-sku/<sku> - Tìm theo SKU
GET    /api/products/by-barcode/<code> - Tìm theo Barcode
POST   /api/products/search       - Tìm kiếm nâng cao
```

### 2. **Inventory Service** (Port 5002)
**Chức năng:**
- ✓ Quản lý tồn kho (Nhập/Xuất/Điều chỉnh)
- ✓ Theo dõi hạn sử dụng và cảnh báo
- ✓ Kiểm kê hàng hóa
- ✓ Lịch sử nhập/xuất kho

**Models:**
- `Inventory`: Tồn kho của sản phẩm
- `InventoryMovement`: Lịch sử nhập/xuất
- `ExpiryWarning`: Cảnh báo hạn sử dụng

**API Endpoints:**
```
GET    /api/inventory/by-product/<product_id>  - Lấy tồn kho sản phẩm
GET    /api/inventory/all                       - Lấy tất cả tồn kho
GET    /api/inventory/low-stock                 - Sản phẩm sắp hết
GET    /api/inventory/movements/<product_id>    - Lịch sử nhập/xuất
GET    /api/inventory/expiry-warnings           - Cảnh báo hạn sử dụng
POST   /api/inventory/init                      - Khởi tạo tồn kho
POST   /api/inventory/adjust                    - Điều chỉnh tồn kho
POST   /api/inventory/add-expiry-warning        - Thêm cảnh báo
PUT    /api/inventory/<product_id>              - Cập nhật thông tin tồn kho
```

### 3. **Sales Service (POS)** (Port 5003)
**Chức náng:**
- ✓ Tạo hóa đơn bán hàng
- ✓ Quét mã vạch thêm sản phẩm
- ✓ Tính tổng tiền, chiết khấu
- ✓ Quản lý thanh toán
- ✓ Thống kê doanh thu

**Models:**
- `Invoice`: Hóa đơn bán hàng
- `InvoiceDetail`: Chi tiết sản phẩm trong hóa đơn

**API Endpoints:**
```
GET    /api/sales/invoices                      - Danh sách hóa đơn
POST   /api/sales/invoices                      - Tạo hóa đơn mới
GET    /api/sales/invoices/<id>                 - Chi tiết hóa đơn
GET    /api/sales/invoices/by-number/<number>   - Tìm theo số hóa đơn
POST   /api/sales/invoices/<id>/add-item        - Thêm sản phẩm vào hóa đơn
PUT    /api/sales/invoices/<id>/checkout        - Hoàn thành hóa đơn
DELETE /api/sales/invoices/<id>                 - Hủy hóa đơn
GET    /api/sales/revenue                       - Thống kê doanh thu
```

### 4. **Supplier Service** (Port 5004)
**Chức năng:**
- ✓ Quản lý thông tin nhà cung cấp
- ✓ Quản lý đơn nhập hàng (PO)
- ✓ Theo dõi nhận hàng
- ✓ Quản lý thanh toán nhà cung cấp

**Models:**
- `Supplier`: Thông tin nhà cung cấp
- `PurchaseOrder`: Đơn nhập hàng
- `PurchaseOrderDetail`: Chi tiết đơn nhập

**API Endpoints:**
```
GET    /api/suppliers                           - Danh sách nhà cung cấp
POST   /api/suppliers                           - Tạo nhà cung cấp
GET    /api/suppliers/<id>                      - Chi tiết nhà cung cấp
PUT    /api/suppliers/<id>                      - Cập nhật nhà cung cấp
DELETE /api/suppliers/<id>                      - Xóa nhà cung cấp

GET    /api/suppliers/purchase-orders           - Danh sách đơn nhập
POST   /api/suppliers/purchase-orders           - Tạo đơn nhập
GET    /api/suppliers/purchase-orders/<id>      - Chi tiết đơn nhập
PUT    /api/suppliers/purchase-orders/<id>/receive - Nhận hàng
PUT    /api/suppliers/purchase-orders/<id>/pay  - Thanh toán
```

### 5. **API Gateway** (Port 5000)
**Chức năng:**
- Điều phối requests tới các services
- Health check các services
- Xử lý errors tập trung
- Logging requests/responses

## Cài Đặt

### 1. Clone/Tải dự án
```bash
cd d:\SOA\Mini-supermarket-app
```

### 2. Tạo virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường
```bash
cp .env.example .env
# Edit .env với các giá trị phù hợp
```

## Chạy Ứng Dụng

### Tùy chọn 1: Chạy từng service riêng lẻ
```bash
# Terminal 1 - Product Service
cd services\product_service
python app.py

# Terminal 2 - Inventory Service
cd services\inventory_service
python app.py

# Terminal 3 - Sales Service
cd services\sales_service
python app.py

# Terminal 4 - Supplier Service
cd services\supplier_service
python app.py

# Terminal 5 - API Gateway
cd gateway
python app.py
```

### Tùy chọn 2: Chạy tất cả services cùng lúc (Windows)
```bash
# Tạo file run_all_services.bat
:: run_all_services.bat
start cmd /k "cd services\product_service && python app.py"
start cmd /k "cd services\inventory_service && python app.py"
start cmd /k "cd services\sales_service && python app.py"
start cmd /k "cd services\supplier_service && python app.py"
start cmd /k "cd gateway && python app.py"
```

## Kiểm Tra Hệ Thống

### Health Check
```bash
curl http://localhost:5000/health
```

### Test Product Service
```bash
# Lấy danh sách sản phẩm
curl http://localhost:5000/api/products

# Tạo sản phẩm
curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "SKU001",
    "name": "Sản phẩm test",
    "category": "Thực phẩm",
    "price": 50000,
    "barcode": "8936073028429"
  }'
```

### Test Inventory Service
```bash
# Lấy tồn kho sản phẩm
curl http://localhost:5000/api/inventory/by-product/1

# Lấy sản phẩm sắp hết
curl http://localhost:5000/api/inventory/low-stock
```

### Test Sales Service
```bash
# Tạo hóa đơn
curl -X POST http://localhost:5000/api/sales/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "INV001",
    "items": [
      {
        "product_id": 1,
        "product_name": "Sản phẩm 1",
        "quantity": 2,
        "unit_price": 50000
      }
    ],
    "payment_method": "cash"
  }'
```

## Cấu Trúc Database

Mỗi service có database riêng với các bảng:

**Product Service:**
- `products` - Danh mục sản phẩm

**Inventory Service:**
- `inventories` - Tồn kho
- `inventory_movements` - Lịch sử nhập/xuất
- `expiry_warnings` - Cảnh báo hạn

**Sales Service:**
- `invoices` - Hóa đơn
- `invoice_details` - Chi tiết hóa đơn

**Supplier Service:**
- `suppliers` - Nhà cung cấp
- `purchase_orders` - Đơn nhập hàng
- `purchase_order_details` - Chi tiết đơn nhập

## Response Format

Tất cả API responses sử dụng format chung:

```json
{
  "success": true/false,
  "message": "Thông báo",
  "data": {...}
}
```

## Error Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable

## Tiếp Theo Cần Làm

- [ ] Thêm Authentication (JWT)
- [ ] Thêm User/Employee Management Service
- [ ] Thêm Customer Loyalty Service
- [ ] Thêm Reports & Analytics Service
- [ ] Thêm Frontend UI
- [ ] Thêm Unit Tests
- [ ] Thêm Docker support
- [ ] Thêm API Documentation (Swagger)
- [ ] Tối ưu Database queries

## Lưu Ý

- Mỗi service là độc lập, có thể scale riêng
- Database của mỗi service riêng biệt (Database per service pattern)
- Services giao tiếp qua HTTP/REST API
- API Gateway là điểm vào duy nhất cho client
- Logging tập trung ở Gateway

## Hỗ Trợ

Nếu gặp vấn đề, kiểm tra:
1. Tất cả services đang chạy?
2. Ports không bị chiếm?
3. Database connections?
4. Network connectivity?

## Tác Giả

Nhóm Kiến Trúc Hướng Dịch Vụ (SOA)
