# LevelProfileManager v2.1

Ứng dụng web quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.

## v2.1 - Frontend Business UI Complete

Bản này kế thừa codebase hiện tại và mở rộng giao diện React/Ant Design theo hướng nghiệp vụ:

- Login page nâng cấp, SSO/LDAP hint.
- Dashboard điều hành tổng hợp.
- Quản lý hệ thống thông tin CRUD.
- Quản lý hồ sơ cấp độ CRUD.
- Trang chi tiết hồ sơ tích hợp checklist, minh chứng, workflow, compliance, export, rà soát định kỳ.
- Compliance Engine UI: gợi ý cấp độ, GAP, risk, readiness.
- Document Center: minh chứng, tài liệu xuất, template biểu mẫu.
- Notification Center: Email/Telegram test và log.
- Periodic Review UI.
- Audit Trail UI.
- Admin UI: users, organizations, identity provider, security events.
- Release/UAT Readiness UI.

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

Truy cập:

- Frontend: http://localhost:3000
- Swagger API: http://localhost:8000/docs

Tài khoản seed:

- admin / Admin@123
- attt / Attt@123

## Commit Git

```powershell
git add .
git commit -m "Upgrade to v2.1 - frontend business UI complete"
git tag v2.1
git push
git push origin v2.1
```
