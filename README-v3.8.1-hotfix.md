# LevelProfileManager v3.8.1 Hotfix

Sửa lỗi PowerShell interpolation ở endpoint trends của Continuous Compliance Monitoring.

## Nội dung sửa

- `scripts/windows-test-api.ps1`
  - Đổi `$profileId?limit=10` thành `${profileId}?limit=10` để PowerShell không hiểu sai biến.
  - Bổ sung UTF-8 output guard.

## Cách triển khai

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```
