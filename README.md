# LevelProfileManager v1.0 - Frontend React Foundation

Ứng dụng web quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.

## Thành phần

- Backend: Python FastAPI
- Database: PostgreSQL 16
- Frontend: React + Vite + Ant Design
- Container: Docker Compose

## Tài khoản test

- `admin / Admin@123`
- `attt / Attt@123`

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
```

Lần build frontend đầu tiên có thể mất vài phút vì Docker cần tải package NodeJS.

## Truy cập

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Test API

```powershell
.\scripts\windows-test-api.ps1
```

## Nội dung v1.0

Kế thừa v0.9 và bổ sung:

- React frontend foundation
- Màn hình đăng nhập
- Layout quản trị
- Dashboard tổng hợp
- Danh sách hệ thống thông tin
- Danh sách hồ sơ cấp độ
- Danh sách thông báo
- Docker Compose chạy đủ PostgreSQL + Backend + Frontend

## Commit Git

```powershell
git add .
git commit -m "Upgrade to v1.0 - frontend React foundation"
git tag v1.0
git push
git push origin v1.0
```
