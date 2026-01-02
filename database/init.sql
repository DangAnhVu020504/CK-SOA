-- =====================================================
-- MINI SUPERMARKET SOA - COMPLETE DATABASE SCRIPT
-- Chạy script này trong MySQL Workbench
-- Version: 2.0 - Updated with all columns
-- =====================================================

-- Tạo các databases
CREATE DATABASE IF NOT EXISTS product_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS inventory_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS sales_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS supplier_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS customer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS employee_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- =====================================================
-- PRODUCT DATABASE
-- =====================================================
USE product_db;

-- Xóa bảng cũ nếu tồn tại (để tạo lại với cấu trúc mới)
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    barcode VARCHAR(50) UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    unit VARCHAR(20) DEFAULT 'cái',
    cost_price FLOAT DEFAULT 0,
    selling_price FLOAT DEFAULT 0,
    supplier_id INT,
    manufacturing_date DATE,
    expiry_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sku (sku),
    INDEX idx_barcode (barcode),
    INDEX idx_category (category),
    INDEX idx_supplier (supplier_id)
);

-- Dữ liệu mẫu sản phẩm (với supplier_id, manufacturing_date, expiry_date)
INSERT INTO products (sku, barcode, name, description, category, unit, cost_price, selling_price, supplier_id, manufacturing_date, expiry_date) VALUES
('SP001', '8934567890001', 'Sữa tươi Vinamilk 1L', 'Sữa tươi tiệt trùng có đường', 'Sữa & Sản phẩm từ sữa', 'hộp', 25000, 32000, 1, '2025-12-01', '2026-06-01'),
('SP002', '8934567890002', 'Mì Hảo Hảo gói', 'Mì ăn liền vị tôm chua cay', 'Thực phẩm khô', 'gói', 3000, 4500, 2, '2025-11-15', '2026-11-15'),
('SP003', '8934567890003', 'Nước ngọt Coca Cola lon 330ml', 'Nước giải khát có gas', 'Nước giải khát', 'lon', 8000, 12000, 3, '2025-10-01', '2026-10-01'),
('SP004', '8934567890004', 'Dầu ăn Neptune 1L', 'Dầu thực vật tinh luyện', 'Dầu ăn & Gia vị', 'chai', 35000, 45000, 5, '2025-09-01', '2027-09-01'),
('SP005', '8934567890005', 'Gạo ST25 5kg', 'Gạo thơm đặc sản', 'Gạo & Ngũ cốc', 'bao', 120000, 150000, 4, '2025-12-15', '2026-12-15'),
('SP006', '8934567890006', 'Bánh Oreo 137g', 'Bánh quy socola nhân kem', 'Bánh kẹo', 'gói', 18000, 25000, 2, '2025-11-01', '2026-05-01'),
('SP007', '8934567890007', 'Nước mắm Phú Quốc 500ml', 'Nước mắm cá cốt', 'Dầu ăn & Gia vị', 'chai', 40000, 55000, 4, '2025-08-01', '2027-08-01'),
('SP008', '8934567890008', 'Sữa chua Vinamilk lốc 4', 'Sữa chua có đường', 'Sữa & Sản phẩm từ sữa', 'lốc', 20000, 28000, 1, '2025-12-20', '2026-01-20'),
('SP009', '8934567890009', 'Bột giặt OMO 3kg', 'Bột giặt siêu sạch', 'Đồ gia dụng', 'gói', 95000, 120000, NULL, NULL, NULL),
('SP010', '8934567890010', 'Khăn giấy Kleenex 100 tờ', 'Khăn giấy mềm mịn', 'Đồ gia dụng', 'hộp', 25000, 35000, NULL, NULL, NULL);

-- =====================================================
-- INVENTORY DATABASE
-- =====================================================
USE inventory_db;

DROP TABLE IF EXISTS inventory_movements;
DROP TABLE IF EXISTS inventory;

CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL UNIQUE,
    quantity INT DEFAULT 0,
    min_quantity INT DEFAULT 10,
    max_quantity INT DEFAULT 1000,
    location VARCHAR(100),
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product (product_id),
    INDEX idx_quantity (quantity)
);

CREATE TABLE inventory_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    movement_type ENUM('in', 'out', 'adjust') NOT NULL,
    quantity INT NOT NULL,
    reference VARCHAR(100),
    note TEXT,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_product (product_id),
    INDEX idx_type (movement_type),
    INDEX idx_created (created_at)
);

-- Dữ liệu mẫu tồn kho (một số sản phẩm sắp hết để test tab "Sắp Hết")
INSERT INTO inventory (product_id, quantity, min_quantity, max_quantity, location) VALUES
(1, 150, 20, 500, 'Kệ A1 - Tủ lạnh'),
(2, 500, 50, 2000, 'Kệ B1 - Thực phẩm khô'),
(3, 25, 30, 1000, 'Kệ C1 - Nước giải khát'),      -- SẮP HẾT: quantity < min
(4, 80, 15, 300, 'Kệ A2 - Dầu ăn'),
(5, 8, 10, 200, 'Kho chính - Gạo'),                -- SẮP HẾT: quantity < min
(6, 15, 20, 500, 'Kệ D1 - Bánh kẹo'),              -- SẮP HẾT: quantity < min
(7, 60, 10, 200, 'Kệ A3 - Gia vị'),
(8, 100, 20, 400, 'Tủ lạnh 1 - Sữa chua'),
(9, 5, 10, 150, 'Kệ E1 - Đồ gia dụng'),            -- SẮP HẾT: quantity < min
(10, 200, 30, 800, 'Kệ F1 - Đồ gia dụng');

-- Dữ liệu mẫu lịch sử di chuyển kho (nhiều records để test tab "Lịch Sử")
INSERT INTO inventory_movements (product_id, movement_type, quantity, reference, note, created_at) VALUES
-- Ngày 01/01/2026
(1, 'in', 200, 'PO-20260101001', 'Nhập hàng từ Vinamilk', '2026-01-01 08:30:00'),
(1, 'out', 50, 'INV-20260101-0001', 'Bán hàng', '2026-01-01 10:15:00'),
(2, 'in', 600, 'PO-20260101002', 'Nhập hàng từ Acecook', '2026-01-01 09:00:00'),
(2, 'out', 100, 'INV-20260101-0003', 'Bán hàng', '2026-01-01 14:30:00'),
(3, 'in', 300, 'PO-20260101003', 'Nhập hàng từ Coca-Cola', '2026-01-01 09:30:00'),
(3, 'out', 275, 'INV-20260101-0005', 'Bán hàng chương trình khuyến mãi', '2026-01-01 16:00:00'),
-- Ngày 02/01/2026
(4, 'in', 100, 'PO-20260102001', 'Nhập dầu ăn Neptune', '2026-01-02 08:00:00'),
(4, 'out', 20, 'INV-20260102-0001', 'Bán hàng', '2026-01-02 11:00:00'),
(5, 'in', 50, 'PO-20260102002', 'Nhập gạo ST25', '2026-01-02 08:30:00'),
(5, 'out', 42, 'INV-20260102-0002', 'Bán hàng', '2026-01-02 17:00:00'),
(6, 'in', 80, 'PO-20260102003', 'Nhập bánh Orion', '2026-01-02 09:00:00'),
(6, 'out', 65, 'INV-20260102-0003', 'Bán hàng Tết', '2026-01-02 18:00:00'),
(7, 'in', 100, 'PO-20260102004', 'Nhập nước mắm Chinsu', '2026-01-02 09:30:00'),
(7, 'out', 40, 'INV-20260102-0004', 'Bán hàng', '2026-01-02 14:00:00'),
(8, 'in', 150, 'PO-20260102005', 'Nhập sữa chua Vinamilk', '2026-01-02 10:00:00'),
(8, 'out', 50, 'INV-20260102-0005', 'Bán hàng', '2026-01-02 15:30:00'),
(9, 'adjust', -35, 'ADJ-20260102001', 'Điều chỉnh hàng hết hạn', '2026-01-02 16:00:00'),
(10, 'in', 250, 'PO-20260102006', 'Nhập giấy vệ sinh', '2026-01-02 10:30:00'),
(10, 'out', 50, 'INV-20260102-0006', 'Bán hàng', '2026-01-02 19:00:00');

-- =====================================================
-- SALES DATABASE
-- =====================================================
USE sales_db;

DROP TABLE IF EXISTS invoice_details;
DROP TABLE IF EXISTS invoices;

CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT,
    employee_id INT,
    subtotal FLOAT DEFAULT 0,
    discount FLOAT DEFAULT 0,
    tax FLOAT DEFAULT 0,
    total FLOAT DEFAULT 0,
    payment_method ENUM('cash', 'card', 'transfer', 'ewallet') DEFAULT 'cash',
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    INDEX idx_number (invoice_number),
    INDEX idx_customer (customer_id),
    INDEX idx_employee (employee_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
);

CREATE TABLE invoice_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(200),
    product_sku VARCHAR(50),
    quantity INT DEFAULT 1,
    unit_price FLOAT DEFAULT 0,
    total_price FLOAT DEFAULT 0,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    INDEX idx_invoice (invoice_id),
    INDEX idx_product (product_id)
);

-- Dữ liệu mẫu hóa đơn
INSERT INTO invoices (invoice_number, customer_id, employee_id, subtotal, discount, total, payment_method, status, completed_at) VALUES
('INV-20260101-0001', 1, 1, 100000, 5000, 95000, 'cash', 'completed', NOW()),
('INV-20260101-0002', 2, 1, 250000, 10000, 240000, 'card', 'completed', NOW()),
('INV-20260101-0003', NULL, 2, 50000, 0, 50000, 'cash', 'completed', NOW()),
('INV-20260102-0001', 3, 2, 180000, 0, 180000, 'transfer', 'completed', NOW()),
('INV-20260102-0002', NULL, 1, 75000, 0, 75000, 'cash', 'pending', NULL);

INSERT INTO invoice_details (invoice_id, product_id, product_name, product_sku, quantity, unit_price, total_price) VALUES
(1, 1, 'Sữa tươi Vinamilk 1L', 'SP001', 2, 32000, 64000),
(1, 3, 'Nước ngọt Coca Cola lon 330ml', 'SP003', 3, 12000, 36000),
(2, 5, 'Gạo ST25 5kg', 'SP005', 1, 150000, 150000),
(2, 4, 'Dầu ăn Neptune 1L', 'SP004', 2, 45000, 90000),
(3, 2, 'Mì Hảo Hảo gói', 'SP002', 10, 4500, 45000),
(4, 6, 'Bánh Oreo 137g', 'SP006', 4, 25000, 100000),
(4, 8, 'Sữa chua Vinamilk lốc 4', 'SP008', 2, 28000, 56000),
(5, 7, 'Nước mắm Phú Quốc 500ml', 'SP007', 1, 55000, 55000);

-- =====================================================
-- SUPPLIER DATABASE
-- =====================================================
USE supplier_db;

DROP TABLE IF EXISTS purchase_order_details;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS suppliers;

CREATE TABLE suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    tax_code VARCHAR(20),
    bank_account VARCHAR(50),
    bank_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_name (name)
);

CREATE TABLE purchase_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    supplier_id INT NOT NULL,
    total_amount FLOAT DEFAULT 0,
    status ENUM('pending', 'approved', 'received', 'cancelled', 'paid') DEFAULT 'pending',
    payment_status ENUM('unpaid', 'partial', 'paid') DEFAULT 'unpaid',
    note TEXT,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved_at DATETIME,
    received_at DATETIME,
    paid_at DATETIME,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    INDEX idx_number (order_number),
    INDEX idx_supplier (supplier_id),
    INDEX idx_status (status)
);

CREATE TABLE purchase_order_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(200),
    quantity INT DEFAULT 1,
    unit_price FLOAT DEFAULT 0,
    total_price FLOAT DEFAULT 0,
    received_quantity INT DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
    INDEX idx_order (order_id)
);

-- Dữ liệu mẫu nhà cung cấp
INSERT INTO suppliers (code, name, contact_person, phone, email, address, tax_code) VALUES
('NCC001', 'Công ty TNHH Vinamilk', 'Nguyễn Văn A', '028-1234567', 'sales@vinamilk.com', '10 Tân Trào, Quận 7, TP.HCM', '0301234567'),
('NCC002', 'Công ty CP Acecook Việt Nam', 'Trần Thị B', '028-2345678', 'order@acecook.com.vn', 'KCN Tân Bình, TP.HCM', '0302345678'),
('NCC003', 'Công ty TNHH Coca-Cola Việt Nam', 'Lê Văn C', '028-3456789', 'sales@cocacola.vn', 'Bình Dương', '0303456789'),
('NCC004', 'Đại lý Gạo Miền Tây', 'Phạm Thị D', '0918123456', 'gaomientay@gmail.com', 'Cần Thơ', '0304567890'),
('NCC005', 'Công ty Neptune Việt Nam', 'Hoàng Văn E', '028-4567890', 'info@neptune.vn', 'Long An', '0305678901');

INSERT INTO purchase_orders (order_number, supplier_id, total_amount, status, payment_status, received_at, paid_at) VALUES
('PO-20260101001', 1, 5000000, 'paid', 'paid', NOW(), NOW()),
('PO-20260101002', 2, 3000000, 'received', 'unpaid', NOW(), NULL),
('PO-20260101003', 3, 2000000, 'pending', 'unpaid', NULL, NULL),
('PO-20260102001', 4, 6000000, 'approved', 'unpaid', NULL, NULL);

INSERT INTO purchase_order_details (order_id, product_id, product_name, quantity, unit_price, total_price, received_quantity) VALUES
(1, 1, 'Sữa tươi Vinamilk 1L', 200, 25000, 5000000, 200),
(2, 2, 'Mì Hảo Hảo gói', 1000, 3000, 3000000, 1000),
(3, 3, 'Nước ngọt Coca Cola lon 330ml', 250, 8000, 2000000, 0),
(4, 5, 'Gạo ST25 5kg', 50, 120000, 6000000, 0);

-- =====================================================
-- CUSTOMER DATABASE
-- =====================================================
USE customer_db;

DROP TABLE IF EXISTS purchase_history;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS member_ranks;

CREATE TABLE member_ranks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    min_points INT DEFAULT 0,
    discount_percent FLOAT DEFAULT 0,
    description TEXT,
    benefits TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100),
    address TEXT,
    date_of_birth DATE,
    gender ENUM('male', 'female', 'other') DEFAULT 'other',
    points INT DEFAULT 0,
    total_spent FLOAT DEFAULT 0,
    rank_id INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rank_id) REFERENCES member_ranks(id),
    INDEX idx_code (code),
    INDEX idx_phone (phone),
    INDEX idx_rank (rank_id)
);

CREATE TABLE purchase_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    total_amount FLOAT NOT NULL,
    points_earned INT DEFAULT 0,
    points_used INT DEFAULT 0,
    discount_amount FLOAT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_customer (customer_id)
);

-- Dữ liệu mẫu hạng thành viên
INSERT INTO member_ranks (name, min_points, discount_percent, description, benefits) VALUES
('Member', 0, 0, 'Thành viên thường', 'Tích điểm 1% giá trị đơn hàng'),
('Silver', 1000, 3, 'Thành viên Bạc', 'Giảm 3% + Tích điểm 1.5%'),
('Gold', 5000, 5, 'Thành viên Vàng', 'Giảm 5% + Tích điểm 2% + Quà sinh nhật'),
('Platinum', 10000, 10, 'Thành viên Bạch Kim', 'Giảm 10% + Tích điểm 3% + Quà sinh nhật + Ưu tiên phục vụ');

-- Dữ liệu mẫu khách hàng
INSERT INTO customers (code, full_name, phone, email, address, date_of_birth, gender, points, total_spent, rank_id) VALUES
('KH20260101001', 'Nguyễn Thị Mai', '0901234567', 'mai.nguyen@gmail.com', '123 Nguyễn Huệ, Q1, TP.HCM', '1990-05-15', 'female', 1500, 5000000, 2),
('KH20260101002', 'Trần Văn Nam', '0912345678', 'nam.tran@gmail.com', '456 Lê Lợi, Q3, TP.HCM', '1985-08-20', 'male', 6000, 15000000, 3),
('KH20260101003', 'Lê Thị Hoa', '0923456789', 'hoa.le@gmail.com', '789 Cách Mạng Tháng 8, Q10, TP.HCM', '1995-03-10', 'female', 500, 2000000, 1),
('KH20260101004', 'Phạm Minh Tuấn', '0934567890', 'tuan.pham@gmail.com', '321 Điện Biên Phủ, Bình Thạnh', '1988-12-25', 'male', 12000, 30000000, 4),
('KH20260101005', 'Hoàng Thị Lan', '0945678901', 'lan.hoang@gmail.com', '654 Hai Bà Trưng, Q1, TP.HCM', '1992-07-08', 'female', 800, 3000000, 1);

-- Lịch sử mua hàng
INSERT INTO purchase_history (customer_id, invoice_number, total_amount, points_earned, points_used, discount_amount) VALUES
(1, 'INV-20260101-0001', 95000, 95, 0, 5000),
(2, 'INV-20260101-0002', 240000, 240, 0, 10000),
(3, 'INV-20260102-0001', 180000, 180, 0, 0);

-- =====================================================
-- EMPLOYEE DATABASE
-- =====================================================
USE employee_db;

DROP TABLE IF EXISTS employee_shifts;
DROP TABLE IF EXISTS work_shifts;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    description VARCHAR(200),
    salary_rate FLOAT DEFAULT 1.0,
    permissions JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    address TEXT,
    date_of_birth DATE,
    gender ENUM('male', 'female', 'other') DEFAULT 'other',
    role_id INT,
    base_salary FLOAT DEFAULT 0,
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    avatar_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    INDEX idx_code (code),
    INDEX idx_role (role_id)
);

CREATE TABLE work_shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employee_shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    shift_id INT NOT NULL,
    work_date DATE NOT NULL,
    check_in_time DATETIME,
    check_out_time DATETIME,
    status ENUM('scheduled', 'checked_in', 'checked_out', 'absent', 'late') DEFAULT 'scheduled',
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (shift_id) REFERENCES work_shifts(id),
    UNIQUE KEY unique_shift (employee_id, shift_id, work_date),
    INDEX idx_date (work_date)
);

-- Dữ liệu mẫu vai trò
INSERT INTO roles (name, code, description, salary_rate, permissions) VALUES
('Quản lý', 'manager', 'Quản lý cửa hàng', 1.5, '{"all": true}'),
('Thu ngân', 'cashier', 'Nhân viên thu ngân', 1.0, '{"pos": true, "view_products": true, "view_customers": true}'),
('Kho', 'warehouse', 'Nhân viên kho', 1.0, '{"inventory": true, "view_products": true}'),
('Bán hàng', 'sales', 'Nhân viên bán hàng', 1.0, '{"pos": true, "view_products": true}');

-- Dữ liệu mẫu ca làm
INSERT INTO work_shifts (name, start_time, end_time, description) VALUES
('Ca sáng', '06:00:00', '14:00:00', 'Ca làm việc buổi sáng'),
('Ca chiều', '14:00:00', '22:00:00', 'Ca làm việc buổi chiều'),
('Ca đêm', '22:00:00', '06:00:00', 'Ca làm việc ban đêm'),
('Ca hành chính', '08:00:00', '17:00:00', 'Ca làm việc hành chính');

-- Dữ liệu mẫu nhân viên (password mặc định: 123456)
INSERT INTO employees (code, full_name, phone, email, password_hash, address, date_of_birth, gender, role_id, base_salary, hire_date) VALUES
('NV001', 'Nguyễn Văn Quản', '0901111111', 'quan.nguyen@supermarket.com', 'scrypt:32768:8:1$TKwGxVPCZW4bGw0e$7d8f5b3c2a1e9f0d8c7b6a5e4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a', '100 Nguyễn Du, Q1, TP.HCM', '1985-01-15', 'male', 1, 15000000, '2020-01-01'),
('NV002', 'Trần Thị Thu', '0902222222', 'thu.tran@supermarket.com', 'scrypt:32768:8:1$TKwGxVPCZW4bGw0e$7d8f5b3c2a1e9f0d8c7b6a5e4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a', '200 Lý Tự Trọng, Q3, TP.HCM', '1992-06-20', 'female', 2, 8000000, '2021-03-15'),
('NV003', 'Lê Văn Kho', '0903333333', 'kho.le@supermarket.com', 'scrypt:32768:8:1$TKwGxVPCZW4bGw0e$7d8f5b3c2a1e9f0d8c7b6a5e4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a', '300 Võ Văn Tần, Q3, TP.HCM', '1990-09-10', 'male', 3, 7500000, '2021-06-01'),
('NV004', 'Phạm Thị Bán', '0904444444', 'ban.pham@supermarket.com', 'scrypt:32768:8:1$TKwGxVPCZW4bGw0e$7d8f5b3c2a1e9f0d8c7b6a5e4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a', '400 Pasteur, Q1, TP.HCM', '1995-12-05', 'female', 4, 7000000, '2022-01-10'),
('NV005', 'Hoàng Văn An', '0905555555', 'an.hoang@supermarket.com', 'scrypt:32768:8:1$TKwGxVPCZW4bGw0e$7d8f5b3c2a1e9f0d8c7b6a5e4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a', '500 Nam Kỳ Khởi Nghĩa, Q3, TP.HCM', '1993-04-18', 'male', 2, 8000000, '2022-06-01');

-- Phân công ca làm mẫu
INSERT INTO employee_shifts (employee_id, shift_id, work_date, status) VALUES
(1, 4, CURDATE(), 'scheduled'),
(2, 1, CURDATE(), 'checked_in'),
(3, 1, CURDATE(), 'checked_in'),
(4, 2, CURDATE(), 'scheduled'),
(5, 2, CURDATE(), 'scheduled');

-- =====================================================
-- AUTH DATABASE
-- =====================================================
USE auth_db;

DROP TABLE IF EXISTS refresh_tokens;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200),
    permissions JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(15),
    role_id INT,
    employee_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    INDEX idx_username (username),
    INDEX idx_email (email)
);

CREATE TABLE refresh_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(500) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_user (user_id)
);

-- Dữ liệu mẫu vai trò hệ thống
INSERT INTO roles (name, description, permissions) VALUES
('admin', 'Quản trị viên hệ thống', '{"all": true}'),
('manager', 'Quản lý cửa hàng', '{"read": true, "write": true, "delete": false}'),
('staff', 'Nhân viên', '{"read": true, "write": true}'),
('customer', 'Khách hàng', '{"read": true}');

-- Dữ liệu mẫu users (password mặc định: 123456)
INSERT INTO users (username, email, password_hash, full_name, role_id, employee_id) VALUES
('admin', 'admin@supermarket.com', 'scrypt:32768:8:1$TKwGxVPCZW4bGw0e$7d8f5b3c2a1e9f0d8c7b6a5e4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a', 'System Admin', 1, NULL),
('manager', 'manager@supermarket.com', 'scrypt:32768:8:1$TKwGxVPCZW4bGw0e$7d8f5b3c2a1e9f0d8c7b6a5e4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a', 'Nguyễn Văn Quản', 2, 1),
('thu.tran', 'thu.tran@supermarket.com', 'scrypt:32768:8:1$TKwGxVPCZW4bGw0e$7d8f5b3c2a1e9f0d8c7b6a5e4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a', 'Trần Thị Thu', 3, 2),
('kho.le', 'kho.le@supermarket.com', 'scrypt:32768:8:1$TKwGxVPCZW4bGw0e$7d8f5b3c2a1e9f0d8c7b6a5e4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a', 'Lê Văn Kho', 3, 3);

-- =====================================================
-- HOÀN THÀNH!
-- =====================================================
SELECT 'Database setup completed successfully!' AS Status;
SELECT 'All 7 databases have been created with sample data.' AS Info;
