# LevelProfileManager v1.6

Phase 16 – Template Engine & Government Document Generator.

## Nội dung chính

- Quản lý danh mục mẫu văn bản (`document_templates`).
- Seed mẫu văn bản mặc định cho hồ sơ đề xuất cấp độ.
- Sinh văn bản hành chính dạng DOCX/PDF:
  - Thuyết minh hồ sơ đề xuất cấp độ.
  - Công văn xin ý kiến chuyên môn.
  - Tờ trình phê duyệt.
  - Quyết định phê duyệt.
  - Phụ lục checklist đáp ứng yêu cầu ATTT.
- Lưu lịch sử file sinh ra trong `exported_documents`.
- API tải file vẫn dùng endpoint `/api/v1/exported-documents/{id}/download`.

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## API mới

```text
GET  /api/v1/document-templates
POST /api/v1/document-templates
GET  /api/v1/document-templates/{template_id}
PUT  /api/v1/document-templates/{template_id}
POST /api/v1/document-templates/seed-defaults
GET  /api/v1/government-documents/types
POST /api/v1/profiles/{profile_id}/government-documents/generate
```

## Ví dụ sinh công văn/tờ trình

```json
{
  "document_type": "APPROVAL_SUBMISSION",
  "file_format": "docx",
  "agency_name": "NGÂN HÀNG CHÍNH SÁCH XÃ HỘI",
  "signer_title": "GIÁM ĐỐC TRUNG TÂM CNTT",
  "place_name": "Hà Nội"
}
```

## Git

```powershell
git add .
git commit -m "Upgrade to v1.6 - template engine government document generator"
git tag v1.6
git push
git push origin v1.6
```
