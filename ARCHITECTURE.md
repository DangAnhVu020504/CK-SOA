# Kiến Trúc SOA - Mini Supermarket Management System

## Tổng Quan Kiến Trúc

```
┌─────────────────────────────────────────────────────────────┐
│                      Client/Frontend                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway (Port 5000)                     │
│  - Request routing                                           │
│  - Error handling                                            │
│  - Health check                                              │
│  - Logging                                                   │
└────┬────────────┬────────────┬──────────────┬───────────────┘
     │            │            │              │
     ▼            ▼            ▼              ▼
┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐
│Product  │  │Inventory │  │ Sales  │  │Supplier  │
│Service  │  │ Service  │  │Service │  │ Service  │
│5001     │  │  5002    │  │  5003  │  │  5004    │
└────┬────┘  └────┬─────┘  └────┬───┘  └────┬─────┘
     │            │             │           │
     ▼            ▼             ▼           ▼
┌──────────────────────────────────────────────────┐
│          Shared Layer                            │
│  - Database (SQLAlchemy ORM)                     │
│  - Exception Handling                            │
│  - Utility Functions                             │
└──────────────────────────────────────────────────┘
     │            │             │           │
     ▼            ▼             ▼           ▼
  SQLite      SQLite         SQLite      SQLite
```

## Design Patterns Sử Dụng

### 1. **Service-Oriented Architecture (SOA)**
- Mỗi service quản lý một domain cụ thể
- Services độc lập, dễ maintain và scale
- Communication qua REST APIs

### 2. **API Gateway Pattern**
- Điểm vào duy nhất cho clients
- Route requests tới services
- Xử lý cross-cutting concerns (logging, error handling)

### 3. **Database Per Service**
- Mỗi service có database riêng
- Không chia sẻ database giữa services
- Đảm bảo loose coupling

### 4. **Repository Pattern**
- Models trong mỗi service quản lý dữ liệu
- ORM (SQLAlchemy) cho database operations

### 5. **Blueprint Pattern (Flask)**
- Modularity trong routes
- Dễ dàng group related endpoints

## Service Responsibilities

```
┌─────────────────────────────────────────────────────────┐
│           PRODUCT SERVICE                               │
├─────────────────────────────────────────────────────────┤
│ Responsibilities:                                        │
│  • Quản lý catalog sản phẩm                             │
│  • CRUD operations sản phẩm                             │
│  • Tìm kiếm sản phẩm                                    │
│  • Quản lý danh mục                                     │
│                                                         │
│ Database: product_service.db                            │
│ Tables:                                                  │
│  - products (id, sku, name, barcode, category, price...) │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│           INVENTORY SERVICE                             │
├─────────────────────────────────────────────────────────┤
│ Responsibilities:                                        │
│  • Quản lý tồn kho                                      │
│  • Nhập/xuất/điều chỉnh hàng                            │
│  • Theo dõi hạn sử dụng                                 │
│  • Cảnh báo sản phẩm sắp hết                            │
│                                                         │
│ Database: inventory_service.db                          │
│ Tables:                                                  │
│  - inventories (product_id, quantity, location...)      │
│  - inventory_movements (type, quantity, reference_id..) │
│  - expiry_warnings (product_id, expiry_date, quantity..)│
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│           SALES SERVICE (POS)                           │
├─────────────────────────────────────────────────────────┤
│ Responsibilities:                                        │
│  • Tạo/quản lý hóa đơn bán hàng                         │
│  • Quản lý payment                                       │
│  • Tính toán tổng tiền, chiết khấu                      │
│  • Thống kê doanh thu                                    │
│                                                         │
│ Database: sales_service.db                              │
│ Tables:                                                  │
│  - invoices (number, total, discount, payment_method..) │
│  - invoice_details (product_id, quantity, unit_price...) │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│           SUPPLIER SERVICE                              │
├─────────────────────────────────────────────────────────┤
│ Responsibilities:                                        │
│  • Quản lý thông tin nhà cung cấp                       │
│  • Tạo/quản lý đơn nhập hàng (PO)                       │
│  • Theo dõi nhận hàng                                    │
│  • Quản lý thanh toán NCC                               │
│                                                         │
│ Database: supplier_service.db                           │
│ Tables:                                                  │
│  - suppliers (code, name, contact, address, bank...)    │
│  - purchase_orders (po_number, total, status...)        │
│  - po_details (product_id, quantity, expiry_date...)    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│           API GATEWAY                                   │
├─────────────────────────────────────────────────────────┤
│ Responsibilities:                                        │
│  • Route requests tới services                          │
│  • Health check                                          │
│  • Error handling centralized                           │
│  • Logging & monitoring                                  │
│                                                         │
│ No Database                                             │
│ Proxy requests, không xử lý business logic              │
└─────────────────────────────────────────────────────────┘
```

## Data Flow Examples

### 1. Tạo Hóa Đơn (Sales Flow)
```
Client POST /api/sales/invoices
   ↓
API Gateway
   ↓
Sales Service (create_invoice)
   ├─ Validate input
   ├─ Create Invoice record
   ├─ Create InvoiceDetail records
   ├─ Calculate totals
   └─ Return response
   ↓
Response to Client
```

### 2. Nhập Hàng (Receiving Flow)
```
Client POST /api/suppliers/purchase-orders/<po_id>/receive
   ↓
API Gateway
   ↓
Supplier Service (receive_purchase_order)
   ├─ Validate PO exists
   ├─ Update received quantities
   ├─ Set delivery date
   ├─ Update status to 'completed'
   └─ Return response
   ↓
Inventory Service SHOULD be called to:
   ├─ Update inventory quantities
   ├─ Create InventoryMovement
   └─ Add ExpiryWarning
   ↓
Response to Client
```

### 3. Bán Hàng (Sales Transaction)
```
Client: Quét barcode → POST /api/sales/invoices/<id>/add-item
   ↓
API Gateway
   ↓
Sales Service
   ├─ Validate product exists
   ├─ Get product info from Product Service
   ├─ Add item to invoice
   ├─ Recalculate totals
   └─ Return invoice with items
   ↓
[Repeat for each product]
   ↓
Client: Checkout → PUT /api/sales/invoices/<id>/checkout
   ↓
API Gateway
   ↓
Sales Service
   ├─ Finalize invoice
   ├─ Record payment
   ├─ Set status to 'completed'
   └─ Return receipt
   ↓
Inventory Service SHOULD be called to:
   ├─ Reduce quantities
   ├─ Create OUT movement
   └─ Check low stock
   ↓
Response to Client (Receipt)
```

## Mở Rộng Kiến Trúc (Future Services)

```
┌──────────────────────────────────────────────────┐
│         Có thể thêm trong tương lai:              │
├──────────────────────────────────────────────────┤
│  • Customer Service (khách hàng, loyalty)         │
│  • Employee Service (nhân viên, ca làm)           │
│  • Auth Service (xác thực, phân quyền)           │
│  • Report Service (báo cáo, thống kê)            │
│  • Notification Service (thông báo)              │
│  • Payment Service (xử lý thanh toán)            │
│  • Accounting Service (kế toán)                  │
└──────────────────────────────────────────────────┘
```

## Deployment Architecture

```
                     Load Balancer
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
      Instance 1       Instance 2       Instance 3
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Gateway    │  │  Gateway    │  │  Gateway    │
    │  (Port 5000)│  │  (Port 5000)│  │  (Port 5000)│
    └──┬──┬──┬────┘  └──┬──┬──┬────┘  └──┬──┬──┬────┘
       │  │  │          │  │  │          │  │  │
    ┌──┴─┐│  │       ┌──┴─┐│  │       ┌──┴─┐│  │
    │ PS │  │ IS     │ PS │  │ IS     │ PS │  │ IS
    └────┘  │        └────┘  │        └────┘  │
         ┌──┴─┐            ┌──┴─┐            ┌──┴─┐
         │SAS │ SS         │SAS │ SS         │SAS │ SS
         └────┘            └────┘            └────┘
         
    PS = Product Service
    IS = Inventory Service
    SAS = Sales Service
    SS = Supplier Service
```

## Best Practices

1. **Error Handling**: Centralized ở Gateway
2. **Logging**: Mỗi service log lại, Gateway log tất cả
3. **Database**: Riêng biệt per service
4. **Cache**: Có thể implement Redis cho product/inventory data
5. **Monitoring**: Sử dụng health check endpoints
6. **Documentation**: API docs per service
7. **Testing**: Unit tests per service
8. **Versioning**: API versioning strategy
9. **Security**: JWT authentication (future)
10. **Rate Limiting**: Implement ở Gateway

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Data Consistency | Event-driven architecture, Message Queue |
| Service Discovery | Service registry (future) |
| Network Latency | Caching, async operations |
| Debugging | Distributed tracing, centralized logging |
| Deployment | Docker, Kubernetes (future) |
| Testing | Integration tests, contract testing |
