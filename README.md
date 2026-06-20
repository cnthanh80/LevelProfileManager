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
