# LevelProfileManager v1.1

Phase 11 - Compliance Engine.

## Tính năng mới

- Gợi ý cấp độ tự động từ thông tin hồ sơ và hệ thống thông tin.
- API phân loại cấp độ theo bộ tiêu chí đầu vào.
- Gap Analysis: xác định yêu cầu bắt buộc/chưa đáp ứng.
- Compliance Score: điểm quản lý, kỹ thuật, tổng thể.
- Risk Assessment: điểm rủi ro và khuyến nghị xử lý.
- Readiness Assessment: đánh giá sẵn sàng gửi thẩm định.
- Lưu lịch sử đánh giá vào `profile_assessments`, `compliance_scores`, `risk_assessments`.
- Dashboard compliance tổng hợp.

## API chính

```text
POST /api/v1/compliance/classify-level
GET  /api/v1/profiles/{id}/compliance/suggest-level
GET  /api/v1/profiles/{id}/compliance/gap-analysis
GET  /api/v1/profiles/{id}/compliance/score
GET  /api/v1/profiles/{id}/compliance/risk
GET  /api/v1/profiles/{id}/compliance/readiness
POST /api/v1/profiles/{id}/compliance/run-assessment
GET  /api/v1/profiles/{id}/compliance/assessments
GET  /api/v1/dashboard/compliance
```

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## Git

```powershell
git add .
git commit -m "Upgrade to v1.1 - compliance engine"
git tag v1.1
git push
git push origin v1.1
```
