# LevelProfileManager v0.6

Ứng dụng web quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.

## v0.6 bổ sung

- Workflow Engine cho hồ sơ đề xuất cấp độ.
- Rule engine chuyển trạng thái hồ sơ.
- Lịch sử xử lý hồ sơ `profile_workflow_history`.
- Bình luận/phê duyệt nội bộ `approval_comments`.
- API dashboard tổng hợp trạng thái workflow.

## Cách chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
```

Mở Swagger:

```text
http://localhost:8000/docs
```

Tài khoản test:

```text
admin / Admin@123
attt / Attt@123
```

## Test nhanh

```powershell
.\scripts\windows-test-api.ps1
```

## API mới trong v0.6

```text
GET  /api/v1/profiles/{profile_id}/workflow
POST /api/v1/profiles/{profile_id}/workflow/transition
GET  /api/v1/profiles/{profile_id}/workflow/history
POST /api/v1/profiles/{profile_id}/comments
GET  /api/v1/profiles/{profile_id}/comments
GET  /api/v1/dashboard/workflow-summary
```

## Workflow actions chính

```text
submit_internal_review
resubmit_internal_review
approve_review
request_revision
submit_leader_approval
leader_approve
leader_request_revision
submit_assessment
receive_assessment_comment
mark_completed
complete_after_assessment
issue_approval_decision
mark_review_due
start_periodic_review
```

## Git

Sau khi test OK:

```powershell
git add .
git commit -m "Upgrade to v0.6 - workflow engine"
git tag v0.6
git push
git push origin v0.6
```
