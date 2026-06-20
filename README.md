# LevelProfileManager v2.7

Phase 27 - Executive Dashboard.

## Bổ sung

- API Dashboard lãnh đạo: `/api/v1/dashboard/executive/*`
- KPI điều hành: mức tuân thủ, rủi ro cao, gap bắt buộc, quá hạn rà soát, thẩm định tồn đọng
- Board pack cho lãnh đạo
- Giao diện menu **Dashboard lãnh đạo**

## Chạy

```powershell
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

Truy cập: http://localhost:3000

Tài khoản: `admin / Admin@123`


## v2.7.1 - UTF8 & Quality Hotfix

- Chuẩn hóa output UTF-8 cho script `scripts/windows-test-api.ps1` trên Windows PowerShell.
- Bổ sung thông báo kết thúc `ALL TESTS PASSED` cho phase v2.7.
- Giữ nguyên API/backend của v2.7, chỉ cải thiện chất lượng kiểm thử và hiển thị tiếng Việt.

Triển khai:

```powershell
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```
