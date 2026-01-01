# Script chạy tất cả các services - Mini Supermarket App
# Để chạy: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Hoặc: powershell -ExecutionPolicy Bypass -File run_all_services.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Mini Supermarket - SOA Services Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra xem requirements.txt đã được cài đặt chưa
Write-Host "[1/6] Kiểm tra Python environment..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($pythonCheck -match "3\.[0-9]+") {
    Write-Host "✓ Python đã cài đặt: $pythonCheck" -ForegroundColor Green
} else {
    Write-Host "✗ Python chưa được cài đặt!" -ForegroundColor Red
    exit 1
}

# Cài đặt dependencies (chỉ chạy một lần)
Write-Host ""
Write-Host "[2/6] Cài đặt dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
Write-Host "✓ Dependencies đã cài đặt" -ForegroundColor Green

# Chạy Gateway
Write-Host ""
Write-Host "[3/6] Khởi động API Gateway (Port 5000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\gateway'; python app.py"
Start-Sleep 2

# Chạy Product Service
Write-Host "[4/6] Khởi động Product Service (Port 5001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\services\product_service'; python app.py"
Start-Sleep 1

# Chạy Inventory Service
Write-Host "[5/6] Khởi động Inventory Service (Port 5002)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\services\inventory_service'; python app.py"
Start-Sleep 1

# Chạy Sales Service
Write-Host "[6/6] Khởi động Sales Service (Port 5003)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\services\sales_service'; python app.py"
Start-Sleep 1

# Chạy Supplier Service
Write-Host "[7/7] Khởi động Supplier Service (Port 5004)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\services\supplier_service'; python app.py"
Start-Sleep 1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ Tất cả services đang chạy!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Các services khả dụng:" -ForegroundColor Cyan
Write-Host "  • API Gateway:      http://localhost:5000" -ForegroundColor White
Write-Host "  • Product Service:  http://localhost:5001" -ForegroundColor White
Write-Host "  • Inventory Service: http://localhost:5002" -ForegroundColor White
Write-Host "  • Sales Service:    http://localhost:5003" -ForegroundColor White
Write-Host "  • Supplier Service: http://localhost:5004" -ForegroundColor White
Write-Host ""
Write-Host "Health Check: curl http://localhost:5000/health" -ForegroundColor Gray
Write-Host ""
Write-Host "Nhấn Ctrl+C trong mỗi terminal để dừng service" -ForegroundColor Yellow
Write-Host ""

# Giữ terminal chính mở
Read-Host "Nhấn Enter để thoát"
