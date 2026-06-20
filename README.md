# LevelProfileManager v2.6

Phase 26 – Assessment Portal.

Bản này kế thừa v2.5 và bổ sung cổng thẩm định hồ sơ đề xuất cấp độ.

## Tính năng mới

- Quản lý hồ sơ gửi thẩm định.
- Theo dõi trạng thái: `DRAFT`, `SUBMITTED`, `COMMENTED`, `COMPLETED`.
- Tiếp nhận ý kiến thẩm định.
- Phản hồi ý kiến thẩm định.
- Dashboard tóm tắt thẩm định.
- Giao diện web menu **Cổng thẩm định**.

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## Truy cập

- Frontend: http://localhost:3000
- Backend Swagger: http://localhost:8000/docs

User mặc định:

```text
admin / Admin@123
```

## Git

```powershell
git add .
git commit -m "Upgrade to v2.6 - assessment portal"
git tag v2.6
git push
git push origin v2.6
```
