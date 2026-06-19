# LevelProfileManager v1.7

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
git commit -m "Upgrade to v1.7 - template engine government document generator"
git tag v1.7
git push
git push origin v1.7
```


## v1.7 - LDAP/SSO Foundation & Organization Access Control

Bổ sung nền tảng tích hợp định danh nội bộ:

- Cấu hình LDAP/SSO trong backend settings.
- API kiểm tra trạng thái identity provider.
- API LDAP dry-run login để test quy trình trước khi nối AD/LDAP thật.
- Mở rộng bảng `users` với `auth_provider`, `external_id`, `is_local_auth_allowed`.
- Nền tảng phân quyền theo đơn vị/tổ chức.
- API kiểm tra phạm vi truy cập hồ sơ và hệ thống thông tin.

Endpoint mới:

```text
GET  /api/v1/auth/identity-provider/status
GET  /api/v1/auth/sso/login-hint
POST /api/v1/auth/ldap-login
GET  /api/v1/access-control/my-scope
GET  /api/v1/access-control/policy
GET  /api/v1/information-systems/{id}/access-check
GET  /api/v1/profiles/{id}/access-check
```
