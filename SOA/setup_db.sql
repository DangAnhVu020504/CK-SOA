-- =============================================
-- Mini Supermarket Database Schema
-- MySQL Setup Script
-- =============================================

-- Create database
CREATE DATABASE IF NOT EXISTS mini_supermarket
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mini_supermarket;

-- =============================================
-- Roles Table
-- =============================================
CREATE TABLE IF NOT EXISTS roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_role_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Users Table
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150),
    phone VARCHAR(20),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    role_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
    INDEX idx_user_username (username),
    INDEX idx_user_email (email),
    INDEX idx_user_role (role_id),
    INDEX idx_user_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Insert Default Roles
-- =============================================
INSERT INTO roles (name, description, permissions) VALUES
('admin', 'Quản trị viên hệ thống - Toàn quyền', '["all"]'),
('manager', 'Quản lý cửa hàng - Quản lý nhân viên và hàng hóa', '["read", "write", "manage_staff", "manage_products", "view_reports"]'),
('staff', 'Nhân viên bán hàng', '["read", "write", "sell_products"]'),
('customer', 'Khách hàng', '["read", "view_products", "purchase"]')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- =============================================
-- Create Default Admin User
-- Password: Admin123! (hashed)
-- =============================================
-- Note: You should create the admin user via the API using /api/auth/register-admin endpoint
-- with the admin_secret key for security.

-- =============================================
-- Useful Queries
-- =============================================

-- Get all users with their roles:
-- SELECT u.id, u.username, u.email, u.full_name, r.name as role_name, u.is_active, u.created_at
-- FROM users u
-- JOIN roles r ON u.role_id = r.id;

-- Get users by role:
-- SELECT u.* FROM users u
-- JOIN roles r ON u.role_id = r.id
-- WHERE r.name = 'admin';

-- Count users by role:
-- SELECT r.name, COUNT(u.id) as user_count
-- FROM roles r
-- LEFT JOIN users u ON r.id = u.role_id
-- GROUP BY r.id;
