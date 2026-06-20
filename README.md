# LevelProfileManager v3.8

Phase 38 - Continuous Compliance Monitoring.

## Nội dung chính

- Compliance Monitoring Score Engine.
- Snapshot tuân thủ liên tục cho từng hồ sơ.
- Findings riêng cho monitoring: mandatory gap, evidence gap, score decrease, low score.
- Notification dry-run cho hồ sơ có rủi ro HIGH/CRITICAL hoặc trend giảm.
- Heatmap compliance theo hồ sơ/hệ thống/đơn vị/cấp độ.
- API dashboard monitoring.
- Giao diện web menu **Compliance Monitoring**.

## Triển khai trên Windows Docker Desktop

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```

## API chính

- `GET /api/v1/dashboard/compliance-monitoring`
- `GET /api/v1/compliance-monitoring/score/{profile_id}`
- `POST /api/v1/compliance-monitoring/recalculate`
- `GET /api/v1/compliance-monitoring/snapshots`
- `GET /api/v1/compliance-monitoring/findings`
- `GET /api/v1/compliance-monitoring/notifications`
- `GET /api/v1/compliance-monitoring/heatmap`
- `GET /api/v1/compliance-monitoring/trends/{profile_id}`

## Git

```powershell
git add .
git commit -m "Upgrade to v3.8 - continuous compliance monitoring"
git tag v3.8
git push
git push origin v3.8
```
