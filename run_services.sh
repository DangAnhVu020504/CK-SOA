#!/bin/bash
# Script chạy tất cả các services

echo "Starting Mini Supermarket SOA Services..."

# Chạy các services với nền
cd services/product_service && python app.py &
echo "Product Service started on port 5001"

cd ../inventory_service && python app.py &
echo "Inventory Service started on port 5002"

cd ../sales_service && python app.py &
echo "Sales Service started on port 5003"

cd ../supplier_service && python app.py &
echo "Supplier Service started on port 5004"

cd ../../gateway && python app.py &
echo "API Gateway started on port 5000"

echo "All services started!"
echo "API Gateway available at http://localhost:5000"

# Giữ script chạy
wait
