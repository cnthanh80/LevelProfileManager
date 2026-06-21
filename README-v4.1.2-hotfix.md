# LevelProfileManager v4.1.2 Hotfix

## Nội dung sửa
- Sửa lỗi AI Classification crash khi hồ sơ hoặc hệ thống thông tin có trường NULL.
- Bổ sung `_safe_text()` và `_safe_join()` trong `ai_classification_service.py`.
- Chuẩn hóa input từ `LevelProfile`/`InformationSystem` trước khi ghép chuỗi và sinh `AiClassificationInput`.

## Lỗi đã xử lý
`TypeError: sequence item 4: expected str instance, NoneType found`

## Triển khai
Copy đè thư mục `backend/app/services/ai_classification_service.py` vào project hiện tại, sau đó chạy:

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```
