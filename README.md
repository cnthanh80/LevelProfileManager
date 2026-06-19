# LevelProfileManager v1.5

Phase 15 - Advanced Audit Trail.

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## Tính năng mới

- Mở rộng `audit_logs` với thông tin request: request id, HTTP method, path, status code, duration, success/fail, source.
- Middleware tự động ghi audit trail cho các API request.
- API tổng hợp audit trail.
- API danh mục action.
- API audit trail theo hồ sơ.
- API tạo audit log thủ công cho cán bộ ATTT/Admin.
- Export audit log CSV.

## API mới

- `GET /api/v1/audit-logs/summary`
- `GET /api/v1/audit-logs/actions`
- `POST /api/v1/audit-logs/manual`
- `GET /api/v1/profiles/{profile_id}/audit-trail`
- `GET /api/v1/audit-logs/export.csv`

## Git

```powershell
git add .
git commit -m "Upgrade to v1.5 - advanced audit trail"
git tag v1.5
git push
git push origin v1.5
```
