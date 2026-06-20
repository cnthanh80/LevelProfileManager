# LevelProfileManager v2.5

Phiên bản v2.5 bổ sung **SLA & Risk Register** trên nền v2.4.1.

## Tính năng mới

- Quản lý danh mục rủi ro theo hồ sơ/hệ thống.
- Tính điểm rủi ro theo likelihood x impact.
- Phân loại LOW/MEDIUM/HIGH/CRITICAL.
- Theo dõi trạng thái xử lý rủi ro.
- Quản lý chính sách SLA theo trạng thái workflow.
- Dashboard cảnh báo SLA warning/breached.
- Giao diện web menu **SLA & Risk Register**.

## Chạy kiểm tra

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## Commit

```powershell
git add .
git commit -m "Upgrade to v2.5 - SLA and risk register"
git tag v2.5
git push
git push origin v2.5
```
