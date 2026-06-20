# LevelProfileManager v3.3 - External Assessment Workflow


Phase 32 - Real Digital Signature Gateway Foundation.

Bổ sung tích hợp ký số thực tế theo adapter: nhà cung cấp CA/HSM, yêu cầu ký, callback trạng thái ký, mô phỏng remote signing và giao diện Ký số thực tế.

## Run

```powershell
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

## Login

```text
admin / Admin@123
```

# LevelProfileManager v3.1

Ứng dụng web quản lý hồ sơ đề xuất cấp độ an toàn hệ thống thông tin.

## Điểm mới v3.1

- AI Classification & Level Recommendation Engine.
- Gợi ý cấp độ dựa trên dữ liệu, kết nối, quy mô, tác động CIA và mức độ quan trọng nghiệp vụ.
- Cảnh báo hồ sơ có nguy cơ phân loại thấp hơn mức engine khuyến nghị.
- Lưu lịch sử khuyến nghị cấp độ.
- Dashboard AI Classification.
- Giao diện web: **AI gợi ý cấp độ**.

## Chạy trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
docker compose up -d --build
.\scripts\windows-test-api.ps1
```

Frontend:

```text
http://localhost:3000
```

Swagger API:

```text
http://localhost:8000/docs
```

Tài khoản test:

```text
admin / Admin@123
```


## v3.3 - Workflow thẩm định đa cấp

- Bổ sung assessment_workflow_events.
- Bổ sung rule engine cho quy trình gửi thẩm định, nhận ý kiến, giải trình, phê duyệt và ban hành quyết định.
- Bổ sung API /assessment-workflow/summary, /assessment-workflow/rules, /assessment-cases/{id}/workflow-transition.
- Bổ sung giao diện Workflow thẩm định.
