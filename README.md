# LevelProfileManager v3.0

Ứng dụng web quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin theo hướng production pilot.

## Chạy local bằng Docker Desktop Windows

```powershell
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

Frontend:

```text
http://localhost:3000
```

Backend Swagger:

```text
http://localhost:8000/docs
```

Tài khoản UAT:

```text
admin / Admin@123
attt / Attt@123
```

## Kiểm tra production readiness

```powershell
.\scripts\windows-production-check.ps1
```

## Tính năng chính

- Quản lý hệ thống thông tin.
- Quản lý hồ sơ đề xuất cấp độ.
- Checklist yêu cầu ATTT.
- Quản lý minh chứng.
- Workflow phê duyệt.
- Dashboard nghiệp vụ và dashboard lãnh đạo.
- Export DOCX/PDF.
- Notification Email/Telegram foundation.
- Audit trail nâng cao.
- Compliance engine.
- Rà soát định kỳ.
- LDAP/SSO foundation.
- Multi-organization.
- Hồ sơ điện tử và ký số mô phỏng.
- Kho biểu mẫu cơ quan.
- SLA & Risk Register.
- Assessment Portal.
- Production readiness API.

## Production guide

Xem `PRODUCTION_DEPLOYMENT.md`.
