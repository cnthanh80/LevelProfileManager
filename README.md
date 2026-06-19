# LevelProfileManager v0.4

Ứng dụng web quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.

## v0.4 bổ sung

- Checklist Engine.
- Danh mục yêu cầu ATTT theo cấp độ 1-5.
- Bảng `security_requirements`.
- Bảng `profile_requirement_answers`.
- API sinh checklist tự động theo cấp độ hồ sơ.
- API cập nhật trạng thái đáp ứng checklist.
- API thống kê tỷ lệ đáp ứng và cảnh báo tiêu chí bắt buộc chưa đáp ứng.
- Seed dữ liệu mẫu cho 3 hệ thống cấp độ 2, 3, 4.

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
```

Mở Swagger:

```text
http://localhost:8000/docs
```

## Tài khoản test

```text
admin / Admin@123
attt / Attt@123
```

## Test nhanh

```powershell
.\scripts\windows-test-api.ps1
```

## API mới trong v0.4

```http
GET  /api/v1/security-requirements
GET  /api/v1/security-requirements/by-level/{level}
POST /api/v1/security-requirements
PUT  /api/v1/security-requirements/{requirement_id}
DELETE /api/v1/security-requirements/{requirement_id}

POST /api/v1/profiles/{profile_id}/generate-checklist
GET  /api/v1/profiles/{profile_id}/checklist
PUT  /api/v1/checklist-answers/{answer_id}
GET  /api/v1/profiles/{profile_id}/compliance-summary
```

## Quy trình upgrade từ v0.3 lên v0.4 bằng Git

Trước khi giải nén đè:

```powershell
git status
git add .
git commit -m "Backup before upgrade to v0.4"
git push
```

Giải nén nội dung `LevelProfileManager-v0.4.zip` đè vào thư mục project hiện tại.

Sau khi test OK:

```powershell
git add .
git commit -m "Upgrade to v0.4 - checklist engine"
git tag v0.4
git push
git push origin v0.4
```

## Lưu ý database

Nếu anh đang dùng volume PostgreSQL từ v0.3, Alembic sẽ tự chạy migration `0002_checklist_engine` khi backend khởi động.

Nếu muốn reset sạch dữ liệu test:

```powershell
docker compose down -v
docker compose up -d --build
```


## Hotfix bcrypt/passlib

Bản này đã pin `bcrypt==4.0.1` để tương thích với `passlib==1.7.4` trên Python 3.12, tránh lỗi backend exit khi seed user.


## Hotfix v0.4.2

- Sửa email seed user từ `example.local` sang `example.com` để tương thích Pydantic EmailStr.
- Bổ sung Alembic migration `0003_fix_seed_user_emails`.

