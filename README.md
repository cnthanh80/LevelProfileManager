# LevelProfileManager v0.3

Ứng dụng web quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.

Phiên bản v0.3 kế thừa Phase 1 + Phase 2 và bổ sung:

- FastAPI backend
- PostgreSQL 16
- Alembic migration đầu tiên
- CRUD `organizations`
- CRUD `information-systems`
- CRUD `level-profiles`
- Auth JWT
- RBAC cơ bản theo vai trò
- Seed dữ liệu role/user mặc định

## 1. Yêu cầu môi trường Windows

- Windows 10/11
- Docker Desktop đã cài và đang chạy
- Docker Desktop dùng Linux containers
- PowerShell hoặc Windows Terminal

## 2. Cách chạy lần đầu

Giải nén file zip, mở PowerShell tại thư mục `LevelProfileManager-v0.3`, chạy:

```powershell
docker compose up -d --build
```

Hoặc chạy script:

```powershell
.\scripts\windows-run.ps1
```

## 3. Kiểm tra container

```powershell
docker compose ps
```

Xem log backend:

```powershell
docker compose logs -f backend
```

## 4. Truy cập API

- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health
- DB Health: http://localhost:8000/api/v1/health/db

## 5. Tài khoản mặc định

### Quản trị hệ thống

```text
username: admin
password: Admin@123
role: ADMIN
```

### Cán bộ ATTT

```text
username: attt
password: Attt@123
role: SECURITY_OFFICER
```

Khuyến nghị đổi mật khẩu ngay khi dùng lâu dài.

## 6. Test nhanh API bằng PowerShell

```powershell
.\scripts\windows-test-api.ps1
```

Script sẽ:

1. Kiểm tra health API
2. Login bằng user `admin`
3. Gọi `/auth/me`
4. Gọi danh sách roles/users
5. Gọi các API CRUD nền tảng

## 7. Cách login trên Swagger

1. Mở http://localhost:8000/docs
2. Bấm nút **Authorize**
3. Nhập:

```text
username: admin
password: Admin@123
```

4. Sau đó thử các API cần quyền như:

```text
GET /api/v1/users
POST /api/v1/organizations
POST /api/v1/information-systems
POST /api/v1/level-profiles
```

## 8. Vai trò RBAC hiện có

| Role code | Tên vai trò |
|---|---|
| ADMIN | Quản trị hệ thống |
| SECURITY_OFFICER | Cán bộ ATTT |
| OPERATOR | Đơn vị vận hành |
| REVIEWER | Người rà soát |
| APPROVER | Lãnh đạo phê duyệt |
| REPORT_VIEWER | Người xem báo cáo |

Quyền hiện tại:

- `ADMIN`: quản trị user, xóa dữ liệu, toàn quyền thao tác
- `SECURITY_OFFICER`: tạo/cập nhật tổ chức, hệ thống, hồ sơ
- `OPERATOR`: tạo/cập nhật hệ thống thông tin
- Các vai trò còn lại được seed trước để phục vụ Phase workflow sau

## 9. Reset môi trường local

Cẩn thận: lệnh này xóa toàn bộ dữ liệu PostgreSQL local của project.

```powershell
docker compose down -v
docker compose up -d --build
```

## 10. Kiểm tra bảng DB

```powershell
docker exec -it lpm_postgres psql -U lpm_user -d level_profile_db
```

Trong psql:

```sql
\dt
select id, code, name from roles order by id;
select id, username, full_name, role_id from users order by id;
```

Thoát:

```sql
\q
```

## 11. Ghi chú phát triển tiếp theo

Phase 4 nên triển khai:

- Checklist engine
- Bảng `security_requirements`
- Bảng `profile_requirement_answers`
- Seed checklist yêu cầu quản lý/kỹ thuật theo cấp độ
- API trả tỷ lệ đáp ứng theo từng hồ sơ
