# LevelProfileManager v4.1.3 Hotfix

## Nội dung sửa

- Sửa lỗi download tài liệu/minh chứng/hồ sơ xuất bị `Not authenticated`.
- Không dùng link trực tiếp `<a href="/download">` vì trình duyệt không gửi header `Authorization: Bearer <token>`.
- Bổ sung helper `downloadFile()` trong `frontend/src/api/client.js` để tải file bằng `fetch` có JWT, nhận blob và tự tải xuống.
- Cập nhật các màn hình:
  - `DocumentsPage.jsx`
  - `ProfileDetail.jsx`
  - `DigitalDossierPage.jsx`
  - `TemplateCenterPage.jsx`
  - `AuditPage.jsx`
  - `EnterpriseReportingPage.jsx`

## Cách triển khai

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
```

Giải nén hotfix, copy đè vào project hiện tại, rồi chạy:

```powershell
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```

## Kiểm thử UAT

- Vào menu `Tài liệu/Xuất hồ sơ`.
- Bấm Download tài liệu minh chứng.
- Bấm Download tài liệu đã xuất.
- Vào chi tiết hồ sơ, tab Minh chứng, bấm Download.
- Vào Kho biểu mẫu, bấm tải file template.
- Kỳ vọng: file tải về trực tiếp, không còn JSON `Not authenticated`.
