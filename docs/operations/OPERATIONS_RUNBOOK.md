# Runbook vận hành LevelProfileManager

## 1. Daily checklist

| Hạng mục | Lệnh/Thao tác | Kỳ vọng |
|---|---|---|
| Container | `docker ps` | backend/frontend/postgres Up |
| API health | `/api/v1/health` | status ok |
| DB health | `/api/v1/health/db` | connected |
| Log lỗi | `docker compose logs backend --tail=200` | Không có traceback mới |
| Dung lượng | `docker system df` | Không đầy disk |

## 2. Khi backend không truy cập được

1. Kiểm tra container:
   ```powershell
   docker compose ps -a
   ```
2. Xem log:
   ```powershell
   docker compose logs backend --tail=200
   ```
3. Nếu lỗi migration, không xóa volume database nếu chưa backup.
4. Nếu lỗi import Python, kiểm tra file endpoint/schema/service vừa cập nhật.

## 3. Khi frontend trắng màn hình

1. Mở F12 → Console.
2. Kiểm tra lỗi JavaScript.
3. Kiểm tra Nginx log:
   ```powershell
   docker compose logs frontend --tail=100
   ```
4. Kiểm tra API proxy `/api/v1/health`.

## 4. Khi PowerShell không chạy script

```powershell
Get-ChildItem -Recurse *.ps1 | Unblock-File
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```
