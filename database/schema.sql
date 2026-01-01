-- =====================================================
-- SOA Mini Supermarket Management - Database Schema
-- =====================================================

-- Tạo database
CREATE DATABASE IF NOT EXISTS supermarket_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE supermarket_db;

-- =====================================================
-- CUSTOMER SERVICE TABLES
-- =====================================================

-- Bảng hạng thành viên
CREATE TABLE IF NOT EXISTS member_ranks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rank_name VARCHAR(50) NOT NULL,
    min_points INT NOT NULL DEFAULT 0,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Thêm các hạng mặc định
INSERT INTO member_ranks (rank_name, min_points, discount_percent, description) VALUES
('Bronze', 0, 0, 'Hạng đồng - Thành viên mới'),
('Silver', 1000, 5, 'Hạng bạc - Giảm 5%'),
('Gold', 5000, 10, 'Hạng vàng - Giảm 10%'),
('Platinum', 10000, 15, 'Hạng bạch kim - Giảm 15%'),
('Diamond', 20000, 20, 'Hạng kim cương - Giảm 20%');

-- Bảng khách hàng
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100),
    address TEXT,
    date_of_birth DATE,
    gender ENUM('male', 'female', 'other') DEFAULT 'other',
    points INT DEFAULT 0,
    total_spent DECIMAL(15,2) DEFAULT 0,
    rank_id INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rank_id) REFERENCES member_ranks(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bảng lịch sử mua hàng
CREATE TABLE IF NOT EXISTS purchase_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    invoice_code VARCHAR(50) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    points_earned INT DEFAULT 0,
    points_used INT DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    final_amount DECIMAL(15,2) NOT NULL,
    note TEXT,
    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- EMPLOYEE SERVICE TABLES
-- =====================================================

-- Bảng vai trò/quyền
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    role_code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    permissions JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Thêm các vai trò mặc định
INSERT INTO roles (role_name, role_code, description, permissions) VALUES
('Thu ngân', 'cashier', 'Nhân viên thu ngân', '{"pos": true, "view_products": true, "view_customers": true}'),
('Quản lý', 'manager', 'Quản lý cửa hàng', '{"pos": true, "view_products": true, "edit_products": true, "view_customers": true, "edit_customers": true, "view_reports": true, "manage_employees": false}'),
('Admin', 'admin', 'Quản trị viên hệ thống', '{"pos": true, "view_products": true, "edit_products": true, "delete_products": true, "view_customers": true, "edit_customers": true, "delete_customers": true, "view_reports": true, "manage_employees": true, "system_settings": true}');

-- Bảng nhân viên
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_code VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    address TEXT,
    date_of_birth DATE,
    gender ENUM('male', 'female', 'other') DEFAULT 'other',
    role_id INT NOT NULL,
    salary DECIMAL(12,2) DEFAULT 0,
    hire_date DATE NOT NULL,
    status ENUM('active', 'inactive', 'on_leave') DEFAULT 'active',
    avatar_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bảng ca làm việc
CREATE TABLE IF NOT EXISTS work_shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shift_name VARCHAR(50) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Thêm các ca làm việc mặc định
INSERT INTO work_shifts (shift_name, start_time, end_time, description) VALUES
('Ca sáng', '06:00:00', '14:00:00', 'Ca làm việc buổi sáng'),
('Ca chiều', '14:00:00', '22:00:00', 'Ca làm việc buổi chiều'),
('Ca đêm', '22:00:00', '06:00:00', 'Ca làm việc ban đêm'),
('Ca hành chính', '08:00:00', '17:00:00', 'Ca làm việc hành chính');

-- Bảng phân công ca làm việc
CREATE TABLE IF NOT EXISTS employee_shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    shift_id INT NOT NULL,
    work_date DATE NOT NULL,
    check_in_time DATETIME,
    check_out_time DATETIME,
    status ENUM('scheduled', 'checked_in', 'checked_out', 'absent', 'late') DEFAULT 'scheduled',
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (shift_id) REFERENCES work_shifts(id),
    UNIQUE KEY unique_employee_shift_date (employee_id, shift_id, work_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX idx_customer_phone ON customers(phone);
CREATE INDEX idx_customer_code ON customers(customer_code);
CREATE INDEX idx_customer_rank ON customers(rank_id);
CREATE INDEX idx_purchase_customer ON purchase_history(customer_id);
CREATE INDEX idx_purchase_date ON purchase_history(purchase_date);
CREATE INDEX idx_employee_code ON employees(employee_code);
CREATE INDEX idx_employee_role ON employees(role_id);
CREATE INDEX idx_employee_shifts_date ON employee_shifts(work_date);
CREATE INDEX idx_employee_shifts_employee ON employee_shifts(employee_id);
