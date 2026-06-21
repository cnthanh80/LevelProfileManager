# LevelProfileManager v4.1.1 Hotfix

Hotfix UAT cho Compliance Engine và Enterprise Reporting.

## Nội dung sửa

- Frontend `CompliancePage`: không còn nuốt lỗi `401 Unauthorized`; hiển thị Alert/toast rõ ràng khi thiếu hoặc hết hạn JWT.
- Frontend `CompliancePage`: hiển thị rõ kết quả `Gợi ý cấp độ`, `Tải đánh giá`, `Chạy assessment` gồm Score, Risk, Readiness, GAP, Suggested Level và Assessment vừa chạy.
- Frontend API client: tự clear token và phát sự kiện `lpm:unauthorized` khi gặp HTTP 401 để buộc người dùng đăng nhập lại.
- Backend Enterprise Reporting: bổ sung alias `/api/v1/enterprise-reporting/dashboard` tương thích với script/frontend cũ, ngoài endpoint chuẩn `/api/v1/dashboard/enterprise-reporting`.

## Triển khai

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```

Sau khi OK:

```powershell
git add .
git commit -m "Hotfix v4.1.1 compliance engine UI auth feedback"
git tag v4.1.1
git push
git push origin v4.1.1
```
