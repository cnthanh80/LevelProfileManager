# LevelProfileManager v0.8

Ứng dụng web quản lý hồ sơ đề xuất cấp độ ATHTTT.

## Nội dung kế thừa

- v0.3: Auth JWT + RBAC
- v0.4: Checklist Engine
- v0.5: Evidence Document Management
- v0.6: Workflow Engine
- v0.7: Dashboard Management

## Bổ sung v0.8 - Export Document Engine

- Bảng `exported_documents`
- Xuất DOCX hồ sơ đề xuất cấp độ
- Xuất PDF phụ lục checklist/tóm tắt hồ sơ
- Lưu lịch sử file đã xuất
- Download/xóa file đã xuất
- API:
  - `POST /api/v1/profiles/{profile_id}/exports`
  - `GET /api/v1/exported-documents`
  - `GET /api/v1/exported-documents/{id}`
  - `GET /api/v1/exported-documents/{id}/download`
  - `DELETE /api/v1/exported-documents/{id}`

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## Swagger

```text
http://localhost:8000/docs
```

## Tài khoản test

```text
admin / Admin@123
attt / Attt@123
```

## Git

```powershell
git add .
git commit -m "Upgrade to v0.8 - export document engine"
git tag v0.8
git push
git push origin v0.8
```
