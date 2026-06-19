# LevelProfileManager v1.2

Phase 12 - Periodic Review Engine.

## Tính năng mới

- Quản lý lịch rà soát định kỳ hồ sơ đề xuất cấp độ.
- Tạo lịch rà soát thủ công theo từng hồ sơ.
- Tự động sinh lịch rà soát tiếp theo theo chu kỳ tháng.
- Theo dõi trạng thái: PLANNED, IN_PROGRESS, COMPLETED, CANCELLED.
- Danh sách hồ sơ đến hạn/sắp đến hạn rà soát.
- Hoàn thành rà soát kèm kết luận và phương án xử lý.
- Tạo thông báo nhắc rà soát định kỳ.
- Dashboard tổng hợp rà soát định kỳ.

## API chính

- POST `/api/v1/profiles/{profile_id}/periodic-reviews`
- POST `/api/v1/profiles/{profile_id}/periodic-reviews/generate-next`
- GET `/api/v1/profiles/{profile_id}/periodic-reviews`
- GET `/api/v1/periodic-reviews/due-soon?days=30`
- PUT `/api/v1/periodic-reviews/{review_id}`
- POST `/api/v1/periodic-reviews/{review_id}/complete`
- POST `/api/v1/periodic-reviews/send-reminders?days=30&recipient=attt@example.com`
- GET `/api/v1/dashboard/periodic-reviews`

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## Tài khoản test

- `admin / Admin@123`
- `attt / Attt@123`

## Git

```powershell
git add .
git commit -m "Upgrade to v1.2 - periodic review engine"
git tag v1.2
git push
git push origin v1.2
```
