# LevelProfileManager v4.2.2 - CMDB Administration UI Hotfix

Bản hotfix này bổ sung chức năng phục vụ UAT tại màn hình **CMDB/Tài sản CNTT**:

- Hiển thị nút **Sửa/Xóa** trên tab Tài sản, Ứng dụng, CSDL, Thiết bị mạng.
- Bổ sung form sửa dữ liệu CMDB trên frontend.
- Bổ sung import tài sản bằng JSON trên frontend.
- Bổ sung API PUT/DELETE cho Ứng dụng, CSDL, Thiết bị mạng.
- Giữ nguyên API PUT/DELETE hiện có cho Tài sản.
- Bổ sung mô tả rõ chức năng **Đồng bộ hồ sơ** ngay trên giao diện.

## Phân quyền

Backend kiểm soát quyền như sau:

- ADMIN: thêm/sửa/xóa/import CMDB.
- SECURITY_OFFICER: thêm/sửa/xóa/import CMDB.
- Các vai trò khác: xem dữ liệu; nếu gọi API ghi dữ liệu sẽ bị từ chối theo RBAC.

## Triển khai

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```

## Commit Git

```powershell
git add .
git commit -m "Hotfix v4.2.2 CMDB administration UI for UAT"
git tag v4.2.2
git push
git push origin v4.2.2
```
