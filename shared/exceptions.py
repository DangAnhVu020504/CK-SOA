"""
Exceptions cho các services
"""

class ServiceException(Exception):
    """Base exception"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ProductNotFound(ServiceException):
    def __init__(self, message="Sản phẩm không tìm thấy"):
        super().__init__(message, 404)

class InvalidInput(ServiceException):
    def __init__(self, message="Dữ liệu nhập không hợp lệ"):
        super().__init__(message, 400)

class UnauthorizedAccess(ServiceException):
    def __init__(self, message="Không có quyền truy cập"):
        super().__init__(message, 401)

class InsufficientStock(ServiceException):
    def __init__(self, message="Số lượng trong kho không đủ"):
        super().__init__(message, 400)

class SupplierNotFound(ServiceException):
    def __init__(self, message="Nhà cung cấp không tìm thấy"):
        super().__init__(message, 404)

class ExpiryDateWarning(ServiceException):
    def __init__(self, message="Hàng sắp hết hạn sử dụng"):
        super().__init__(message, 200)
