# LevelProfileManager v4.0 - Enterprise Release Deployment

## Run on Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-production-check.ps1
```

## Web UI

- Frontend: http://localhost:3000
- Swagger: http://localhost:8000/docs

Default test account:

```text
admin / Admin@123
```

## v4.0 Enterprise Center

New menu: **Enterprise Center v4.0**

Main capabilities:

- Enterprise Configuration Center
- System Health Center
- Job Scheduler Center
- Data Retention Policy
- Backup & Recovery Center
- Enterprise Readiness Dashboard

Main APIs:

- `GET /api/v1/enterprise-center/dashboard`
- `POST /api/v1/enterprise-center/seed-defaults`
- `GET /api/v1/enterprise-center/health`
- `GET /api/v1/enterprise-center/readiness`
- `GET /api/v1/enterprise-center/configurations`
- `GET /api/v1/enterprise-center/jobs`
- `GET /api/v1/enterprise-center/retention-policies`
- `POST /api/v1/enterprise-center/backups/mock`
- `POST /api/v1/enterprise-center/backups/{backup_id}/validate`
