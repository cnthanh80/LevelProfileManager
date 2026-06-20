# LevelProfileManager v3.3 - External Assessment Workflow


## 1. Mục tiêu

Bản v3.0 là baseline sẵn sàng UAT/production pilot cho ứng dụng quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.

## 2. Chuẩn bị cấu hình

Trước khi triển khai production, cập nhật `backend/.env`:

```env
APP_ENV=production
APP_VERSION=3.0.0
JWT_SECRET_KEY=<chuoi-bi-mat-manh>
CORS_ALLOWED_ORIGINS=https://<ten-mien-noi-bo>
RATE_LIMIT_ENABLED=true
SECURITY_HEADERS_ENABLED=true
NOTIFICATION_DRY_RUN=false
```

Nếu chưa cấu hình SMTP/Telegram thật, giữ `NOTIFICATION_DRY_RUN=true` trong UAT.

## 3. Chạy production compose

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

Kiểm tra:

```powershell
.\scripts\windows-production-check.ps1
```

## 4. Backup và restore

Backup:

```powershell
.\scripts\windows-backup-db.ps1
```

Restore:

```powershell
.\scripts\windows-restore-db.ps1 -BackupFile .\backups\level_profile_db_YYYYMMDD_HHMMSS.sql
```

## 5. Checklist go-live

- Đổi `JWT_SECRET_KEY`.
- Bật `RATE_LIMIT_ENABLED=true`.
- Giới hạn CORS theo domain nội bộ.
- Cấu hình SMTP/Telegram thật hoặc xác nhận dry-run cho UAT.
- Cấu hình LDAP/SSO theo hạ tầng định danh.
- Kiểm tra backup/restore.
- Kiểm tra quyền truy cập theo đơn vị.
- Kiểm tra audit log và security events.
- Kiểm tra xuất hồ sơ DOCX/PDF.
- Kiểm tra ký số: hiện là mock signing, cần tích hợp CA/HSM/remote signing trước khi dùng ký chính thức.

## 6. Tài khoản UAT mặc định

```text
admin / Admin@123
attt / Attt@123
```

Đổi mật khẩu ngay khi dùng dữ liệu thật.


## v3.3 - Workflow thẩm định đa cấp

- Bổ sung assessment_workflow_events.
- Bổ sung rule engine cho quy trình gửi thẩm định, nhận ý kiến, giải trình, phê duyệt và ban hành quyết định.
- Bổ sung API /assessment-workflow/summary, /assessment-workflow/rules, /assessment-cases/{id}/workflow-transition.
- Bổ sung giao diện Workflow thẩm định.
