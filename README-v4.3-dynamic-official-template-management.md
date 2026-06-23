# LevelProfileManager v4.3 - Dynamic Official Template Management

Phase 42.1 bổ sung cơ chế quản lý mẫu biểu động:

- Upload DOCX template chính thức của cơ quan.
- Sử dụng biến dạng `{{ system_name }}`, `{{ profile_code }}`, `{{ proposed_level }}`.
- Kích hoạt template làm mẫu mặc định theo từng loại văn bản.
- Government Dossier Pack tự ưu tiên template DOCX đang active/default.
- Nếu chưa có template active, hệ thống fallback về mẫu sinh tự động của v4.2.
- Preview context hiển thị dữ liệu sẽ đổ vào template.
- Download template qua API có JWT, không dùng link trực tiếp thiếu token.

## Nhóm loại văn bản nên dùng

| Mẫu trong Government Dossier | document_type cần tạo |
|---|---|
| 01-ToTrinh.docx | APPROVAL_SUBMISSION |
| 02-HoSoCapDo.docx | PROFILE_EXPLANATION |
| 03-VanBanXinYKien.docx | CONSULTATION_REQUEST |
| 04-QuyetDinh.docx | APPROVAL_DECISION |
| 05-Checklist.xlsx | CHECKLIST_APPENDIX |

## Quy trình

1. Vào `Kho biểu mẫu / Quản lý mẫu biểu động`.
2. Tạo biểu mẫu mới, chọn đúng `document_type`.
3. Upload file DOCX chính thức.
4. Bấm `Default`.
5. Vào `Government Dossier Pack`.
6. Sinh bộ hồ sơ.
7. Kiểm tra ZIP được sinh theo mẫu DOCX đang active.

## Cú pháp biến

Ví dụ trong Word:

```text
Điều 1. Phê duyệt cấp độ {{ proposed_level }} đối với hệ thống thông tin {{ system_name }}.
```

Các biến phổ biến:

- `{{ agency_name }}`
- `{{ place_name }}`
- `{{ document_date }}`
- `{{ profile_code }}`
- `{{ proposed_level }}`
- `{{ system_name }}`
- `{{ system_code }}`
- `{{ owner_organization }}`
- `{{ operator_organization }}`
- `{{ system_scope }}`
- `{{ technical_architecture }}`
- `{{ compliance_rate }}`
- `{{ evidence_count }}`
- `{{ signer_title }}`
- `{{ signer_name }}`

## Triển khai

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```

## Git

```powershell
git add .
git commit -m "Upgrade to v4.3 - dynamic official template management"
git tag v4.3.0
git push
git push origin v4.3.0
```
