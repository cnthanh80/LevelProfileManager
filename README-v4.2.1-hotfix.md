# LevelProfileManager v4.2.1 Hotfix

Hotfix sửa lỗi PowerShell 5.1 gửi JSON có tiếng Việt tới API Administration Center.

## Nội dung sửa

- Bổ sung helper `Invoke-LpmJson` trong `scripts/windows-test-api.ps1`.
- Ép JSON body sang UTF-8 bytes với `application/json; charset=utf-8`.
- Cập nhật test Administration Center v4.2.1.

## Triển khai

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
git commit -m "Hotfix v4.2.1 administration center PowerShell JSON UTF8"
git tag v4.2.1
git push
git push origin v4.2.1
```
