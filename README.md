# LevelProfileManager v1.9

Phase 19 – Security Hardening Foundation.

## Nội dung mới

- Chính sách mật khẩu tập trung.
- Kiểm tra độ mạnh mật khẩu.
- Ghi nhận sự kiện bảo mật: đăng nhập thành công/thất bại, khóa/mở khóa tài khoản.
- Khóa tài khoản tạm thời sau nhiều lần đăng nhập sai.
- API tổng hợp security summary.
- API danh sách security events.
- API mở khóa tài khoản cho ADMIN.

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## API chính

```text
GET  /api/v1/security/password-policy
POST /api/v1/security/password-policy/validate
GET  /api/v1/security/summary
GET  /api/v1/security/events
POST /api/v1/security/events
POST /api/v1/users/{user_id}/security/unlock
```

## Git

```powershell
git add .
git commit -m "Upgrade to v1.9 - security hardening foundation"
git tag v1.9
git push
git push origin v1.9
```
