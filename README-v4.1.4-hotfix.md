# LevelProfileManager v4.1.4 Hotfix

## Nội dung sửa

- Sửa lỗi frontend build fail do `CompliancePage.jsx` import `hasToken` nhưng `frontend/src/api/client.js` chưa export hàm này.
- Bổ sung `export function hasToken() { return !!getToken(); }` vào `client.js`.

## Cách triển khai

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
```

Giải nén hotfix, copy đè vào project, rồi chạy:

```powershell
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```

## Commit

```powershell
git add .
git commit -m "Hotfix v4.1.4 frontend hasToken export"
git tag v4.1.4
git push
git push origin v4.1.4
```
