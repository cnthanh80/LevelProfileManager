# LevelProfileManager v2.3 Hotfix 1

Sửa lỗi màn hình trắng frontend do React chưa được import trong một số JSX modules.

Sửa lỗi backend Digital Dossier:
- `EvidenceDocument.version_no` -> `EvidenceDocument.version`

Cách triển khai:

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
# copy đè toàn bộ nội dung gói hotfix vào project
docker compose build --no-cache frontend
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

Truy cập:
- Frontend: http://localhost:3000
- Swagger: http://localhost:8000/docs

User test:
- admin / Admin@123
