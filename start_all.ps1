# PowerShell Script - Khởi động tất cả Services cùng lúc
# Usage: .\start_all.ps1

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Mini Supermarket SOA - Starting Services" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$RootDir = "d:\Flask\CK-SOA"

# Kiểm tra Consul
Write-Host "Checking Consul..." -ForegroundColor Yellow
try {
    $consulCheck = Invoke-WebRequest -Uri "http://localhost:8500/v1/status/leader" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "  [OK] Consul is running" -ForegroundColor Green
} catch {
    Write-Host "  [!] Consul not running - Services will use fallback mode" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow

# Start Product Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir\services\product_service'; Write-Host 'Product Service (5001)' -ForegroundColor Green; python app.py"
Start-Sleep -Milliseconds 500

# Start Inventory Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir\services\inventory_service'; Write-Host 'Inventory Service (5002)' -ForegroundColor Green; python app.py"
Start-Sleep -Milliseconds 500

# Start Sales Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir\services\sales_service'; Write-Host 'Sales Service (5003)' -ForegroundColor Green; python app.py"
Start-Sleep -Milliseconds 500

# Start Supplier Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir\services\supplier_service'; Write-Host 'Supplier Service (5004)' -ForegroundColor Green; python app.py"
Start-Sleep -Milliseconds 500

# Start Customer Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir\services\customer_service'; Write-Host 'Customer Service (5005)' -ForegroundColor Green; python app.py"
Start-Sleep -Milliseconds 500

# Start Employee Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir\services\employee_service'; Write-Host 'Employee Service (5006)' -ForegroundColor Green; python app.py"
Start-Sleep -Milliseconds 500

# Start Auth Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir\services\auth_service'; Write-Host 'Auth Service (5100)' -ForegroundColor Green; python app.py"
Start-Sleep -Milliseconds 500

# Start Gateway
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir\gateway'; Write-Host 'API Gateway (5000)' -ForegroundColor Cyan; python app.py"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  All services started!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor White
Write-Host "  Gateway:    http://localhost:5000" -ForegroundColor Cyan
Write-Host "  Health:     http://localhost:5000/health" -ForegroundColor Gray
Write-Host "  Consul UI:  http://localhost:8500" -ForegroundColor Gray
Write-Host ""
