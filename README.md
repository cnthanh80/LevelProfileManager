# LevelProfileManager v0.9

Phase 9 bổ sung **Notification & Audit Foundation** cho hệ thống quản lý hồ sơ đề xuất cấp độ.

## Thành phần kế thừa

- v0.3 Auth JWT + RBAC
- v0.4 Checklist Engine
- v0.5 Evidence Document Management
- v0.6 Workflow Engine
- v0.7 Dashboard Management
- v0.8 Export Document Engine

## Tính năng mới v0.9

- Bảng `notification_logs`
- Bảng `audit_logs`
- API danh sách/thống kê thông báo
- API tạo thông báo kiểm thử
- API gửi nhắc xử lý hồ sơ
- Nền tảng tích hợp Email/Telegram ở phase sau

## API mới

```text
GET  /api/v1/notifications
GET  /api/v1/notifications/summary
POST /api/v1/notifications/send-test
POST /api/v1/profiles/{profile_id}/notifications/review-reminder
GET  /api/v1/audit-logs
```

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## Git

```powershell
git add .
git commit -m "Upgrade to v0.9 - notification audit foundation"
git tag v0.9
git push
git push origin v0.9
```
