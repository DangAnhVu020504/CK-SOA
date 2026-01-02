# 🏪 Mini Supermarket Management System

Hệ thống quản lý siêu thị mini theo kiến trúc **SOA** với **Consul Service Discovery**.

## 📁 Cấu trúc

```
CK-SOA/
├── services/               # 7 Microservices
│   ├── product_service/    # Port 5001
│   ├── inventory_service/  # Port 5002
│   ├── sales_service/      # Port 5003
│   ├── supplier_service/   # Port 5004
│   ├── customer_service/   # Port 5005
│   ├── employee_service/   # Port 5006
│   └── auth_service/       # Port 5100
├── frontend/               # Templates & Static
├── gateway/                # API Gateway (Port 5000)
├── shared/                 # Utilities & Consul
├── config/                 # Configuration
├── database/               # Schema
├── docs/                   # Documentation
└── scripts/                # Run scripts
```

## 🔧 Consul Service Discovery

Hệ thống sử dụng **Consul** để:
- ✅ Tự động đăng ký services khi khởi động
- ✅ Tự động hủy đăng ký khi shutdown
- ✅ Health check định kỳ
- ✅ Service discovery động
- ✅ Fallback về URL cố định nếu Consul không có

### Khởi động Consul

**Với Docker:**
```bash
docker-compose -f docker-compose.consul.yml up -d
```

**Hoặc cài Consul thủ công:**
```bash
consul agent -dev
```

### Consul UI
Truy cập: http://localhost:8500

## 🚀 Chạy ứng dụng

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Khởi động Consul (optional)
```bash
docker-compose -f docker-compose.consul.yml up -d
```

### 3. Chạy tất cả services
```powershell
cd scripts
.\run_all_services.ps1
```

## 🔗 Endpoints

| Endpoint | Mô tả |
|----------|-------|
| http://localhost:5000 | Gateway & Dashboard |
| http://localhost:5000/health | Health check tất cả services |
| http://localhost:5000/api | API info |
| http://localhost:5000/consul/status | Consul status |
| http://localhost:5000/consul/services | Liệt kê services |
| http://localhost:8500 | Consul UI |

## 📡 API

```
/api/products        - Product CRUD
/api/inventory/*     - Inventory management
/api/sales/*         - Sales & POS
/api/suppliers       - Supplier management
/api/customers       - Customer & loyalty
/api/employees       - Employee & shifts
/api/auth/*          - Authentication
```

## 🛠️ Công nghệ

- Flask + SQLAlchemy
- Consul (Service Discovery)
- JWT Authentication
- Docker (optional)
