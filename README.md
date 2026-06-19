# LevelProfileManager v2.0

MVP Release 2.0 cho ứng dụng quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.

## Nội dung chính

- Kế thừa đầy đủ v1.9: Auth/RBAC, HTTT, hồ sơ cấp độ, checklist, minh chứng, workflow, dashboard, export, notification, audit, template, LDAP/SSO foundation, production/security hardening.
- Bổ sung **Release 2.0 Readiness API** để kiểm tra trạng thái sẵn sàng UAT/MVP.
- Bổ sung checklist UAT nghiệp vụ để chuẩn bị nghiệm thu nội bộ.
- Cập nhật version `APP_VERSION=2.0.0`.

## API mới

- `GET /api/v1/release/info`
- `GET /api/v1/release/data-footprint`
- `GET /api/v1/release/readiness`
- `GET /api/v1/release/uat-checklist`

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
git commit -m "Upgrade to v2.0 - MVP release readiness"
git tag v2.0
git push
git push origin v2.0
```
