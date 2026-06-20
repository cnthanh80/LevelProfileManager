# LevelProfileManager v3.9

Phase 39 – Enterprise Reporting & Data Warehouse.

## Bổ sung

- Enterprise Reporting Dashboard
- Data Warehouse Metrics
- Enterprise Report Snapshots
- Portfolio CSV Export
- Frontend menu: Enterprise Reporting

## Triển khai Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```

## Git

```powershell
git add .
git commit -m "Upgrade to v3.9 - enterprise reporting data warehouse"
git tag v3.9
git push
git push origin v3.9
```


## LevelProfileManager v4.0 - Enterprise Release

Phase 40 bổ sung Enterprise Center cho vận hành production:

- Enterprise Configuration Center
- System Health Center
- Job Scheduler Center
- Data Retention Policy
- Backup & Recovery Center
- Enterprise Readiness Dashboard

API chính:

- `GET /api/v1/enterprise-center/dashboard`
- `POST /api/v1/enterprise-center/seed-defaults`
- `GET /api/v1/enterprise-center/health`
- `GET /api/v1/enterprise-center/readiness`
- `GET /api/v1/enterprise-center/configurations`
- `GET /api/v1/enterprise-center/jobs`
- `GET /api/v1/enterprise-center/retention-policies`
- `POST /api/v1/enterprise-center/backups/mock`
- `POST /api/v1/enterprise-center/backups/{id}/validate`

Frontend: menu **Enterprise Center v4.0**.
