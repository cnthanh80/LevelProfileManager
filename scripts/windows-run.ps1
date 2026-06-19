# Chạy tại thư mục gốc LevelProfileManager-v0.3
# Yêu cầu: Docker Desktop đã bật và đang chạy Linux containers

docker compose up -d --build

docker compose ps

Write-Host "API docs: http://localhost:8000/docs"
Write-Host "Health:   http://localhost:8000/api/v1/health"
Write-Host "DB:       http://localhost:8000/api/v1/health/db"
Write-Host "Login user admin / Admin@123"
