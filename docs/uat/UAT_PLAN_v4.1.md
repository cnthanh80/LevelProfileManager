# Kế hoạch UAT LevelProfileManager v4.1

## 1. Mục tiêu
Xác nhận hệ thống quản lý hồ sơ đề xuất cấp độ có thể dùng thử nội bộ với luồng nghiệp vụ end-to-end:

1. Quản lý đơn vị/tổ chức.
2. Quản lý hệ thống thông tin.
3. Tạo hồ sơ đề xuất cấp độ.
4. Sinh checklist theo cấp độ.
5. Cập nhật hiện trạng đáp ứng.
6. Upload tài liệu minh chứng.
7. Chạy workflow nội bộ và workflow thẩm định.
8. Xuất hồ sơ/văn bản.
9. Theo dõi dashboard, compliance, risk, SLA, SIEM, CMDB, báo cáo.

## 2. Phạm vi UAT

| Nhóm | Phạm vi kiểm thử |
|---|---|
| Auth/RBAC | Đăng nhập, phân quyền, kiểm soát truy cập theo vai trò |
| Information Systems | CRUD hệ thống thông tin, tìm kiếm, phân trang |
| Level Profiles | Tạo/cập nhật hồ sơ cấp độ, trạng thái hồ sơ |
| Checklist | Sinh checklist, cập nhật đáp ứng, tính tỷ lệ |
| Evidence | Upload/download/xóa tài liệu minh chứng |
| Workflow | Chuyển trạng thái, bình luận, lịch sử |
| Export | Xuất DOCX/PDF, lưu lịch sử tài liệu xuất |
| Compliance | Gợi ý cấp độ, gap, score, monitoring |
| Enterprise | Health, backup, retention, scheduler, readiness |

## 3. Dữ liệu UAT đề xuất
Tối thiểu 5 hệ thống:

| STT | Hệ thống | Cấp độ dự kiến | Ghi chú |
|---|---|---:|---|
| 1 | Core Banking | 4 | Nghiệp vụ trọng yếu |
| 2 | Mobile Banking | 3 | Kết nối Internet/API |
| 3 | ESB/API Gateway | 3 | Tích hợp hệ thống |
| 4 | CITAD | 3 | Thanh toán/liên ngân hàng |
| 5 | Website nội bộ | 2 | Thông tin nội bộ |

## 4. Tiêu chí đạt UAT
- 100% test case mức Critical/High đạt.
- Không có lỗi crash backend/frontend.
- Không có lỗi sai phân quyền nghiêm trọng.
- Xuất được tài liệu hồ sơ và checklist.
- Dashboard có số liệu nhất quán.
- Backup/restore test thành công ở mức kỹ thuật.
