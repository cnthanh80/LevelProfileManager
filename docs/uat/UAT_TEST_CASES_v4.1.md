# Bộ test case UAT v4.1

## TC-01 Đăng nhập

| Mục | Nội dung |
|---|---|
| Tiền điều kiện | Docker đang chạy, backend/frontend OK |
| Dữ liệu | admin / Admin@123 |
| Bước test | Mở http://localhost:3000, đăng nhập |
| Kết quả mong đợi | Vào được dashboard, hiển thị menu theo quyền |
| Mức độ | Critical |

## TC-02 Tạo hệ thống thông tin

| Mục | Nội dung |
|---|---|
| Bước test | Tạo hệ thống mới với mã duy nhất |
| Kết quả mong đợi | Hệ thống được lưu, xuất hiện trong danh sách |
| Mức độ | Critical |

## TC-03 Tạo hồ sơ cấp độ

| Mục | Nội dung |
|---|---|
| Bước test | Tạo hồ sơ cho hệ thống, chọn cấp độ 3 |
| Kết quả mong đợi | Hồ sơ ở trạng thái DRAFT |
| Mức độ | Critical |

## TC-04 Sinh checklist

| Mục | Nội dung |
|---|---|
| Bước test | Gọi chức năng sinh checklist cho hồ sơ |
| Kết quả mong đợi | Danh sách yêu cầu ATTT được tạo theo cấp độ |
| Mức độ | Critical |

## TC-05 Cập nhật đáp ứng checklist

| Mục | Nội dung |
|---|---|
| Bước test | Cập nhật một tiêu chí thành COMPLIANT, một tiêu chí NON_COMPLIANT |
| Kết quả mong đợi | Compliance summary thay đổi tương ứng |
| Mức độ | High |

## TC-06 Upload minh chứng

| Mục | Nội dung |
|---|---|
| Bước test | Upload file PDF/DOCX gắn với hồ sơ/checklist |
| Kết quả mong đợi | File được lưu, download được, evidence_count tăng |
| Mức độ | Critical |

## TC-07 Workflow nội bộ

| Mục | Nội dung |
|---|---|
| Bước test | DRAFT → INTERNAL_REVIEW → REVIEWED → APPROVED |
| Kết quả mong đợi | Trạng thái chuyển đúng, có lịch sử workflow |
| Mức độ | Critical |

## TC-08 Xuất hồ sơ

| Mục | Nội dung |
|---|---|
| Bước test | Xuất DOCX/PDF hồ sơ hoặc checklist |
| Kết quả mong đợi | Tạo file, download được, có lịch sử exported_documents |
| Mức độ | High |

## TC-09 AI gợi ý cấp độ

| Mục | Nội dung |
|---|---|
| Bước test | Chạy classification cho hồ sơ có Internet/API/dữ liệu quan trọng |
| Kết quả mong đợi | Có recommended_level, confidence, explanation |
| Mức độ | Medium |

## TC-10 Enterprise readiness

| Mục | Nội dung |
|---|---|
| Bước test | Chạy windows-production-check.ps1 |
| Kết quả mong đợi | Các API health/readiness trả OK |
| Mức độ | High |
