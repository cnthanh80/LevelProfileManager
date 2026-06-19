# LevelProfileManager v1.3

Phase 13 - Enterprise Dashboard.

## Bổ sung chính

- Dashboard lãnh đạo cấp enterprise.
- Ma trận HTTT/hồ sơ theo cấp độ 1-5.
- Bảng ưu tiên xử lý theo rủi ro, điểm tuân thủ, gap bắt buộc.
- Action board cho cán bộ ATTT: tiêu chí bắt buộc chưa đáp ứng, hồ sơ thiếu minh chứng, lịch rà soát đến hạn.
- API executive report tổng hợp phục vụ báo cáo nhanh.
- Frontend dashboard cập nhật thêm chỉ số điều hành.

## API mới

- `GET /api/v1/dashboard/enterprise/overview`
- `GET /api/v1/dashboard/enterprise/level-matrix`
- `GET /api/v1/dashboard/enterprise/compliance-risk`
- `GET /api/v1/dashboard/enterprise/action-board`
- `GET /api/v1/dashboard/enterprise/executive-report`

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
git commit -m "Upgrade to v1.3 - enterprise dashboard"
git tag v1.3
git push
git push origin v1.3
```
