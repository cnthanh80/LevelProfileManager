# Hướng dẫn quản trị hệ thống

## 1. Khởi động hệ thống

```powershell
cd D:\Projects\LevelProfileManager
docker compose up -d --build
```

## 2. Kiểm tra trạng thái

```powershell
docker ps
docker compose logs backend --tail=100
docker compose logs frontend --tail=100
```

## 3. Tài khoản mặc định

| User | Password | Ghi chú |
|---|---|---|
| admin | Admin@123 | Quản trị hệ thống |
| attt | Attt@123 | Cán bộ ATTT |

Sau UAT cần đổi mật khẩu mặc định.

## 4. Backup database

```powershell
.\scripts\windows-backup-db.ps1
```

## 5. Restore database

```powershell
.\scripts\windows-restore-db.ps1 -BackupFile <path>
```

## 6. Kiểm tra production baseline

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-production-check.ps1
```
