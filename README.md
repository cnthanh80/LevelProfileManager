# LevelProfileManager v4.1

Ứng dụng web quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin theo hướng triển khai nội bộ cho cơ quan/tổ chức.

## Truy cập

- Frontend: http://localhost:3000
- Backend Swagger: http://localhost:8000/docs

## Tài khoản test

- `admin / Admin@123`
- `attt / Attt@123`

## Chạy hệ thống

```powershell
cd D:\Projects\LevelProfileManager
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose down
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-uat-check.ps1
```

## Bộ tài liệu UAT v4.1

- `docs/uat/UAT_PLAN_v4.1.md`
- `docs/uat/UAT_TEST_CASES_v4.1.md`
- `docs/user-guide/USER_GUIDE_ATTT_OFFICER.md`
- `docs/admin-guide/ADMIN_GUIDE.md`
- `docs/operations/OPERATIONS_RUNBOOK.md`
- `docs/security/SECURITY_TEST_CHECKLIST.md`
- `docs/release/RELEASE_NOTES_v4.1.md`

## Mục tiêu v4.1

Phase 41 tập trung ổn định UAT, tài liệu hóa, checklist vận hành và chuẩn bị bàn giao dùng thử nội bộ. Không bổ sung thay đổi nghiệp vụ lớn để hạn chế rủi ro phát sinh lỗi mới.
