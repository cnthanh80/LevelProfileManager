# LevelProfileManager v3.7

Ứng dụng web quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.

## v3.7 - Compliance Automation

Bổ sung:

- Compliance Automation Rule Engine
- Chạy kiểm tra tự động gap tuân thủ theo hồ sơ
- Phát hiện tiêu chí bắt buộc chưa đáp ứng
- Phát hiện tiêu chí đạt nhưng thiếu minh chứng
- Phát hiện rủi ro cao chưa xử lý
- Phát hiện hồ sơ quá hạn rà soát
- Dashboard Compliance Automation
- Giao diện menu **Compliance Automation**

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

Truy cập:

- Frontend: http://localhost:3000
- Swagger: http://localhost:8000/docs

Tài khoản test:

- admin / Admin@123
- attt / Attt@123


## v3.7.2 Hotfix
- Added missing ComplianceAutomationRunRequest compatibility schema.
