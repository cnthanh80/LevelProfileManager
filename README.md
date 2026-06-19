# LevelProfileManager v1.8

Ứng dụng web quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.

## Phase 18 - Production Hardening Foundation

Bản v1.8 kế thừa v1.7 và bổ sung nền tảng hardening cho triển khai nội bộ/production:

- Request ID middleware: tự sinh `X-Request-ID` cho mỗi request.
- Security headers middleware: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `Cache-Control`.
- CORS cấu hình qua `.env`, không mở `*` mặc định.
- Rate limit middleware dạng in-memory, tắt mặc định cho local dev, bật được bằng `.env`.
- Health endpoints chuẩn vận hành: `/health/liveness`, `/health/readiness`.
- System runtime endpoint cho ADMIN.
- Production checklist endpoint cho ADMIN.
- File mẫu `.env.production.example`.
- `docker-compose.prod.yml` tham khảo cho môi trường production nội bộ.

## Chạy local trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## API mới

```text
GET /api/v1/health/liveness
GET /api/v1/health/readiness
GET /api/v1/system/runtime
GET /api/v1/system/production-checklist
```

Hai API `/system/*` yêu cầu tài khoản ADMIN.

## Tài khoản test

```text
admin / Admin@123
attt / Attt@123
```

## Gợi ý Git

```powershell
git add .
git commit -m "Upgrade to v1.8 - production hardening foundation"
git tag v1.8
git push
git push origin v1.8
```
