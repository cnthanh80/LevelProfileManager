# LevelProfileManager v2.3.3 Hotfix

Sửa lỗi Alembic revision quá dài gây lỗi PostgreSQL:

`value too long for type character varying(32)`

File migration cũ:

`backend/alembic/versions/0014_multi_organization_management.py`

được thay bằng:

`backend/alembic/versions/0014_multi_org.py`

Revision ID mới: `0014_multi_org`


## LevelProfileManager v2.3 - Digital Signature & Electronic Dossier

Bổ sung Phase 23:

- Quản lý phiên bản hồ sơ điện tử `profile_versions`.
- Ký số mô phỏng `profile_signatures`.
- Sinh snapshot JSON và SHA-256 hash cho hồ sơ, checklist, tài liệu minh chứng.
- So sánh hai phiên bản hồ sơ.
- Tải bằng chứng ký số mô phỏng.
- Giao diện React: menu **Hồ sơ điện tử/Ký số**.

### API chính

```text
GET  /api/v1/profiles/{profile_id}/dossier/summary
POST /api/v1/profiles/{profile_id}/versions
GET  /api/v1/profiles/{profile_id}/versions
GET  /api/v1/profile-versions/{version_id}
GET  /api/v1/profile-versions/compare
POST /api/v1/profile-versions/{version_id}/sign
GET  /api/v1/profiles/{profile_id}/signatures
GET  /api/v1/profile-signatures/{signature_id}/download
```

### Chạy kiểm tra

```powershell
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

Frontend: http://localhost:3000

User test: `admin / Admin@123`


## Hotfix v2.3.2

- Sửa thứ tự route `/profile-versions/compare` để không bị FastAPI nhận nhầm `compare` là `{version_id}`.
- Giữ nguyên các sửa lỗi v2.3.1: import React và evidence document version.
