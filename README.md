# LevelProfileManager v1.4

Phase 14 - Email + Telegram Notification Engine.

## Nội dung chính

- Kế thừa v1.3 Enterprise Dashboard.
- Bổ sung Notification Engine gửi qua 3 kênh:
  - `IN_APP`
  - `EMAIL`
  - `TELEGRAM`
- Mặc định chạy an toàn ở chế độ `NOTIFICATION_DRY_RUN=true` để test trên Docker Desktop Windows mà không cần SMTP/Telegram thật.
- API kiểm tra cấu hình runtime.
- API gửi test Email/Telegram.
- API gửi nhắc rà soát định kỳ qua kênh chọn trước.
- Ghi nhận kết quả gửi vào `notification_logs` với trạng thái `SENT` hoặc `FAILED`.

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## API mới

```text
GET  /api/v1/notifications/runtime-status
POST /api/v1/notifications/send-email-test
POST /api/v1/notifications/send-telegram-test
POST /api/v1/notifications/send-due-review-reminders
```

## Cấu hình Email thật

Sửa file `backend/.env`:

```env
NOTIFICATION_DRY_RUN=false
SMTP_ENABLED=true
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_user
SMTP_PASSWORD=your_password
SMTP_FROM_EMAIL=no-reply@example.com
SMTP_FROM_NAME=Level Profile Manager
SMTP_USE_TLS=true
```

## Cấu hình Telegram thật

```env
NOTIFICATION_DRY_RUN=false
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=123456:ABCDEF
TELEGRAM_DEFAULT_CHAT_ID=123456789
```

Sau khi sửa `.env`:

```powershell
docker compose down
docker compose up -d --build
```

## Git

```powershell
git add .
git commit -m "Upgrade to v1.4 - email telegram notification engine"
git tag v1.4
git push
git push origin v1.4
```
