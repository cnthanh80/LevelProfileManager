# LevelProfileManager v3.5

Phase 35 – LDAP/SSO Production.

## Tính năng mới

- LDAP/SSO production readiness API.
- LDAP connection dry-run/test endpoint.
- Preview mapping LDAP user sang user nội bộ.
- Sync external LDAP user vào hệ thống.
- SSO assertion dry-run cho claim mapping.
- Giao diện **LDAP/SSO Production**.

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

Truy cập:

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

Tài khoản test:

- admin / Admin@123
