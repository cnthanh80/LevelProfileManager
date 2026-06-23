# LevelProfileManager v4.2 - Phase 42.0 Government Dossier Pack

## Mục tiêu

Nâng chức năng xuất hồ sơ từ mức biểu mẫu demo sang gói hồ sơ hành chính có cấu trúc, gồm:

1. `01-ToTrinh.docx` - Tờ trình phê duyệt hồ sơ đề xuất cấp độ.
2. `02-HoSoCapDo.docx` - Hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.
3. `03-VanBanXinYKien.docx` - Văn bản xin ý kiến chuyên môn.
4. `04-QuyetDinh.docx` - Quyết định phê duyệt cấp độ.
5. `05-Checklist.xlsx` - Phụ lục checklist đáp ứng yêu cầu ATTT.
6. `06-MinhChung/` - Thư mục tài liệu minh chứng đi kèm trong gói ZIP.

## API mới

- `GET /api/v1/dossiers/summary`
- `POST /api/v1/dossiers/{profile_id}/generate`
- `GET /api/v1/dossiers`
- `GET /api/v1/dossiers/{dossier_id}`
- `GET /api/v1/dossiers/{dossier_id}/files`
- `GET /api/v1/dossiers/{dossier_id}/download`
- `GET /api/v1/dossier-files/{file_id}/download`
- `POST /api/v1/dossiers/{dossier_id}/regenerate`
- `DELETE /api/v1/dossiers/{dossier_id}`

## Database mới

- `government_dossiers`
- `government_dossier_files`

Migration: `0028_government_dossier_pack.py`.

## Frontend mới

Menu mới: `Government Dossier Pack`.

Chức năng:

- Chọn hồ sơ cấp độ.
- Sinh bộ hồ sơ.
- Chọn có/không đính kèm minh chứng.
- Xem danh sách bộ hồ sơ đã sinh.
- Download ZIP.
- Xem chi tiết từng file trong bộ hồ sơ.
- Download từng file DOCX/XLSX.
- Regenerate phiên bản mới.

## Lưu ý nghiệp vụ

Bộ mẫu v4.2 đã có cấu trúc đúng hướng hồ sơ hành chính theo Nghị định 85/2016/NĐ-CP và Thông tư 12/2022/TT-BTTTT, nhưng vẫn là mẫu generic. Giai đoạn tiếp theo nên triển khai `Phase 42.1 - Official Template Pack NHCSXH` để đưa biểu mẫu về đúng mẫu nội bộ của cơ quan.
