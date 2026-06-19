# LevelProfileManager v2.4

Phase 24 - Government Template Center.

## Điểm mới

- Kho biểu mẫu cơ quan/tổ chức.
- Quản lý template theo loại văn bản: thuyết minh hồ sơ, công văn xin ý kiến, tờ trình, quyết định phê duyệt, phụ lục checklist.
- Upload/download file template DOCX/PDF/XLSX/TXT/HTML.
- Đặt template mặc định theo loại văn bản.
- Danh sách biến template hỗ trợ.
- Preview context dữ liệu trước khi sinh văn bản.
- Giao diện web menu **Kho biểu mẫu**.

## Triển khai trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

Truy cập:

- Web: http://localhost:3000
- API: http://localhost:8000/docs

Tài khoản test:

- `admin / Admin@123`

## Git

```powershell
git add .
git commit -m "Upgrade to v2.4 - government template center"
git tag v2.4
git push
git push origin v2.4
```


## Hotfix v2.4.1

- Sửa lỗi preview template context: `LevelProfile` không có thuộc tính `name`; dùng `profile_code` thay thế.
