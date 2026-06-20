# Checklist kiểm thử bảo mật UAT

## 1. Authentication
- Không đăng nhập được với sai mật khẩu.
- Tài khoản bị khóa theo chính sách nếu sai nhiều lần.
- Token hết hạn không được truy cập API.

## 2. Authorization
- User không có quyền ADMIN không được quản lý users/roles.
- User đơn vị A không xem/sửa hồ sơ đơn vị B nếu không được phân quyền.
- Hồ sơ đã khóa/phê duyệt không được sửa trái phép.

## 3. Upload file
- Chỉ cho phép định dạng hợp lệ: PDF, DOCX, XLSX, ảnh.
- Không cho upload file thực thi.
- Tên file không gây path traversal.

## 4. Audit
- Đăng nhập, logout, sửa hồ sơ, upload, chuyển workflow phải có audit log.
- Audit log không cho sửa/xóa bởi user thông thường.

## 5. API
- Kiểm tra lỗi 401/403 đúng.
- Kiểm tra rate limit cơ bản.
- Không trả stacktrace chi tiết cho người dùng cuối ở production.
