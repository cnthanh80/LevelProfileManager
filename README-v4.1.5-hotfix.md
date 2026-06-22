# LevelProfileManager v4.1.5 Hotfix

## Nội dung sửa lỗi

### 1. PDF tiếng Việt bị lỗi font
- Bổ sung `backend/app/services/pdf_font.py` để đăng ký font Unicode cho ReportLab.
- Cập nhật `export_service.py` và `template_engine.py` để dùng font Unicode khi sinh PDF.
- Cập nhật `backend/Dockerfile` để cài `fonts-dejavu-core` trong container backend.

Lưu ý: các file PDF đã sinh trước hotfix sẽ không tự sửa font. Cần sinh lại tài liệu PDF mới sau khi triển khai hotfix.

### 2. Tài liệu minh chứng bị lặp nhiều dòng
- Cập nhật `evidence_service.py` để không tạo thêm bản ghi nếu người dùng upload lại đúng cùng một file, cùng hồ sơ, cùng loại tài liệu và cùng checksum.
- Cập nhật endpoint `evidence_documents.py` để danh sách tài liệu minh chứng chỉ hiển thị bản mới nhất đối với các bản ghi trùng tuyệt đối.

## Triển khai

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
```

Giải nén hotfix, copy đè vào project, rồi chạy:

```powershell
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```

## Kiểm thử sau triển khai

1. Vào menu **Tài liệu/Xuất hồ sơ**.
2. Kiểm tra danh sách tài liệu minh chứng không còn lặp nhiều dòng giống nhau.
3. Sinh lại một PDF mới.
4. Download PDF mới và kiểm tra tiếng Việt hiển thị đúng dấu.

## Commit đề xuất

```powershell
git add .
git commit -m "Hotfix v4.1.5 PDF unicode and evidence duplicate handling"
git tag v4.1.5
git push
git push origin v4.1.5
```
