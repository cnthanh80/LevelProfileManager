# LevelProfileManager v0.5

Phiên bản v0.5 kế thừa v0.4.2 và bổ sung **Evidence Document Management**.

## Chức năng mới

- Bảng `evidence_documents`.
- Upload tài liệu minh chứng: Word, Excel, PDF, ảnh.
- Phân loại tài liệu: quy chế ATTT, sơ đồ mạng, sơ đồ ứng dụng, phương án sao lưu, phương án giám sát, phương án ứng cứu sự cố, biên bản đánh giá, văn bản thẩm định, quyết định phê duyệt.
- Gắn tài liệu với hồ sơ đề xuất cấp độ.
- Gắn tài liệu với từng tiêu chí checklist.
- Tự cập nhật `evidence_count` cho checklist answer.
- Download tài liệu minh chứng.
- Xóa metadata và file vật lý.
- Lưu file tại `backend/storage/uploads` và mount vào container `/app/storage`.

## Chạy ứng dụng

```powershell
cd D:\Projects\LevelProfileManager

docker compose down
docker compose up -d --build
```

## Test API

```powershell
.\scripts\windows-test-api.ps1
```

## URL

```text
http://localhost:8000/docs
http://localhost:8000/api/v1/health
```

## Tài khoản test

```text
admin / Admin@123
attt / Attt@123
```

## API mới

```http
POST /api/v1/evidence-documents
GET  /api/v1/evidence-documents
GET  /api/v1/evidence-documents/{document_id}
PUT  /api/v1/evidence-documents/{document_id}
GET  /api/v1/evidence-documents/{document_id}/download
DELETE /api/v1/evidence-documents/{document_id}
GET  /api/v1/profiles/{profile_id}/evidence-documents
GET  /api/v1/checklist-answers/{answer_id}/evidence-documents
```

## Git sau khi test OK

```powershell
git add .
git commit -m "Upgrade to v0.5 - evidence document management"
git tag v0.5
git push
git push origin v0.5
```
