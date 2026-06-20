# Release Notes v4.1 - UAT Stabilization & Documentation Pack

## Mục tiêu
Bổ sung bộ tài liệu và script hỗ trợ UAT, bàn giao dùng thử nội bộ, vận hành và kiểm thử bảo mật.

## Nội dung mới
- Kế hoạch UAT.
- Bộ test case UAT.
- Hướng dẫn người dùng cán bộ ATTT.
- Hướng dẫn quản trị.
- Runbook vận hành.
- Checklist kiểm thử bảo mật.
- Danh mục template cần chuẩn hóa.
- Script kiểm tra UAT nhanh.
- Script mở tài liệu hướng dẫn.

## Không thay đổi lớn
- Không thay đổi cấu trúc nghiệp vụ chính.
- Không thay đổi DB schema nghiệp vụ.
- Không thay đổi cơ chế đăng nhập.

## Khuyến nghị sau khi cập nhật
1. Chạy `windows-test-api.ps1`.
2. Chạy `windows-uat-check.ps1`.
3. Thực hiện UAT theo `docs/uat/UAT_TEST_CASES_v4.1.md`.
4. Ghi lỗi vào issue tracker hoặc file UAT log nội bộ.
