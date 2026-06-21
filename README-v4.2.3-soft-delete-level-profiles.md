# v4.2.3 - Soft Delete Level Profiles

Hotfix này sửa lỗi không xóa được hồ sơ cấp độ khi hồ sơ đã có dữ liệu workflow history.

## Thay đổi chính

- Không xóa vật lý bản ghi trong `level_profiles`.
- `DELETE /api/v1/level-profiles/{id}` chuyển hồ sơ DRAFT sang `ARCHIVED`.
- Bổ sung các trường:
  - `is_deleted`
  - `deleted_at`
  - `deleted_by`
- Danh sách hồ sơ mặc định ẩn hồ sơ đã lưu trữ.
- Có thể xem hồ sơ lưu trữ bằng `include_deleted=true`.
- Bổ sung API khôi phục:
  - `POST /api/v1/level-profiles/{id}/restore`
- Frontend đổi nút `Xóa` thành `Lưu trữ`.

## Lý do

Hồ sơ cấp độ có liên kết với workflow history, checklist, minh chứng, chữ ký, audit log. Vì vậy xóa vật lý sẽ vi phạm khóa ngoại và không phù hợp nghiệp vụ quản lý hồ sơ.

## Triển khai

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```

## Git

```powershell
git add .
git commit -m "Hotfix v4.2.3 soft delete level profiles"
git tag v4.2.3
git push
git push origin v4.2.3
```
