$ErrorActionPreference = "Stop"

$BaseUrl = "http://localhost:8000"
Write-Host "Testing LevelProfileManager API v2.2..." -ForegroundColor Cyan

Invoke-RestMethod "$BaseUrl/api/v1/health" | ConvertTo-Json
Invoke-RestMethod "$BaseUrl/api/v1/health/db" | ConvertTo-Json

$loginBody = @{
  username = "admin"
  password = "Admin@123"
}

$tokenResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/auth/login" -Body $loginBody
$token = $tokenResponse.access_token
$headers = @{ Authorization = "Bearer $token" }

Write-Host "Login OK" -ForegroundColor Green
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/auth/me" | ConvertTo-Json

Write-Host "Profiles" -ForegroundColor Cyan
$profiles = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/level-profiles?limit=10"
$profiles | ConvertTo-Json -Depth 5

if ($profiles.items.Count -gt 0) {
  $profileId = $profiles.items[0].id
  Write-Host "Generate checklist for profile $profileId" -ForegroundColor Cyan
  Invoke-RestMethod -Method Post -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/generate-checklist" | ConvertTo-Json -Depth 5
  $checklist = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/checklist"
  $checklist | ConvertTo-Json -Depth 6
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/compliance-summary" | ConvertTo-Json -Depth 6

  $answerId = $null
  if ($checklist.Count -gt 0) { $answerId = $checklist[0].id }

  Write-Host "Upload evidence document" -ForegroundColor Cyan
  $tmpFile = Join-Path $env:TEMP "lpm-evidence-sample.pdf"
  "Tai lieu minh chung mau cho ho so de xuat cap do" | Out-File -Encoding utf8 $tmpFile

  $curlArgs = @(
    "-sS",
    "-X", "POST",
    "$BaseUrl/api/v1/evidence-documents",
    "-H", "Authorization: Bearer $token",
    "-F", "profile_id=$profileId",
    "-F", "document_type=QUY_CHE_ATTT",
    "-F", "title=Quy che ATTT mau",
    "-F", "description=File test upload minh chung tu script",
    "-F", "file=@$tmpFile;type=application/pdf"
  )
  if ($answerId) {
    $curlArgs += @("-F", "checklist_answer_id=$answerId")
  }

  $uploadRaw = & curl.exe @curlArgs
  if ($LASTEXITCODE -ne 0) {
    throw "curl.exe upload failed with exit code $LASTEXITCODE"
  }
  $uploaded = $uploadRaw | ConvertFrom-Json
  $uploaded | ConvertTo-Json -Depth 5

  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/evidence-documents?profile_id=$profileId" | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/evidence-documents" | ConvertTo-Json -Depth 5

  Write-Host "Workflow current state" -ForegroundColor Cyan
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/workflow" | ConvertTo-Json -Depth 5

  Write-Host "Create workflow comment" -ForegroundColor Cyan
  $commentBody = @{ comment = "Kiem tra workflow comment tu script v0.6"; action = "comment" } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/comments" -Body $commentBody | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/comments" | ConvertTo-Json -Depth 5

  $workflow = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/workflow"
  if ($workflow.allowed_actions -contains "submit_internal_review") {
    Write-Host "Transition submit_internal_review" -ForegroundColor Cyan
    $transitionBody = @{ action = "submit_internal_review"; comment = "Gui ra soat noi bo tu script v0.6" } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/workflow/transition" -Body $transitionBody | ConvertTo-Json -Depth 5
  }

  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/workflow" | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/workflow/history" | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/workflow-summary" | ConvertTo-Json -Depth 5

  Write-Host "Export DOCX document" -ForegroundColor Cyan
  $exportBody = @{ document_type = "PROFILE_EXPLANATION"; file_format = "docx" } | ConvertTo-Json
  $docxExport = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/exports" -Body $exportBody
  $docxExport | ConvertTo-Json -Depth 5

  Write-Host "Export PDF document" -ForegroundColor Cyan
  $pdfBody = @{ document_type = "CHECKLIST_APPENDIX"; file_format = "pdf" } | ConvertTo-Json
  $pdfExport = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/exports" -Body $pdfBody
  $pdfExport | ConvertTo-Json -Depth 5

  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/exported-documents?profile_id=$profileId" | ConvertTo-Json -Depth 5

  Write-Host "Compliance Engine" -ForegroundColor Cyan
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/compliance/suggest-level" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/compliance/gap-analysis" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/compliance/score" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/compliance/risk" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/compliance/readiness" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/profiles/$profileId/compliance/run-assessment" | ConvertTo-Json -Depth 8
  Write-Host "Periodic Review Engine" -ForegroundColor Cyan
  $dueDate = (Get-Date).AddDays(20).ToString("yyyy-MM-dd")
  $reviewBody = @{
    review_type = "ANNUAL"
    due_date = $dueDate
    note = "Lich ra soat dinh ky tao tu script v1.2"
  } | ConvertTo-Json
  $review = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/periodic-reviews" -Body $reviewBody
  $review | ConvertTo-Json -Depth 6
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/periodic-reviews" | ConvertTo-Json -Depth 6
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/periodic-reviews/due-soon?days=30" | ConvertTo-Json -Depth 6
  $completeBody = @{ findings = "Da ra soat thanh cong tu script v1.2"; action_plan = "Tiep tuc theo doi va cap nhat ho so khi co thay doi" } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/periodic-reviews/$($review.id)/complete" -Body $completeBody | ConvertTo-Json -Depth 6

}


Write-Host "Dashboard summary" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/summary" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/compliance-overview" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/evidence-gaps" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/compliance" | ConvertTo-Json -Depth 8

Write-Host "v0.8 core API test completed" -ForegroundColor Green

Write-Host "Notification summary" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/notifications/summary" | ConvertTo-Json -Depth 8

Write-Host "Send test notification" -ForegroundColor Cyan
$notifyBody = @{
  event_type = "MANUAL_TEST"
  channel = "IN_APP"
  recipient = "admin@example.com"
  subject = "Thong bao test v0.9"
  message = "Day la thong bao kiem thu Notification Engine v0.9"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/notifications/send-test" -Body $notifyBody | ConvertTo-Json -Depth 5

if ($profiles.items.Count -gt 0) {
  $profileId = $profiles.items[0].id
  Write-Host "Send profile review reminder" -ForegroundColor Cyan
  $reminderBody = @{
    channel = "IN_APP"
    recipient = "attt@example.com"
  } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/notifications/review-reminder" -Body $reminderBody | ConvertTo-Json -Depth 5
}

Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/notifications?limit=10" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/audit-logs?limit=10" | ConvertTo-Json -Depth 8

Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/periodic-reviews" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/periodic-reviews/send-reminders?days=30&recipient=attt@example.com" | ConvertTo-Json -Depth 8


Write-Host "Notification runtime status" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/notifications/runtime-status" | ConvertTo-Json -Depth 8

Write-Host "Send EMAIL dry-run notification" -ForegroundColor Cyan
$emailBody = @{
  event_type = "EMAIL_TEST"
  recipient = "admin@example.com"
  subject = "Email test v1.4"
  message = "Day la email dry-run tu Notification Engine v1.4"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/notifications/send-email-test" -Body $emailBody | ConvertTo-Json -Depth 5

Write-Host "Send TELEGRAM dry-run notification" -ForegroundColor Cyan
$telegramBody = @{
  event_type = "TELEGRAM_TEST"
  recipient = "000000000"
  subject = "Telegram test v1.4"
  message = "Day la Telegram dry-run tu Notification Engine v1.4"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/notifications/send-telegram-test" -Body $telegramBody | ConvertTo-Json -Depth 5

Write-Host "Enterprise Dashboard" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/enterprise/overview" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/enterprise/level-matrix" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/enterprise/compliance-risk" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/enterprise/action-board" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/enterprise/executive-report" | ConvertTo-Json -Depth 10

Write-Host "v1.4 API test completed" -ForegroundColor Green

Write-Host "Frontend health" -ForegroundColor Cyan
try {
  Invoke-RestMethod "http://localhost:3000/health" | Out-Host
  Write-Host "Frontend is available at http://localhost:3000" -ForegroundColor Green
} catch {
  Write-Host "Frontend health check skipped or not ready. Open http://localhost:3000 after build completes." -ForegroundColor Yellow
}

Write-Host "Audit Trail Enhancement" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/audit-logs/summary" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/audit-logs/actions" | ConvertTo-Json -Depth 8
$manualAuditBody = @{
  action = "MANUAL_TEST"
  entity_type = "LEVEL_PROFILE"
  entity_id = 1
  detail = "Ban ghi audit tao tu script test v1.5"
  source = "SCRIPT"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/audit-logs/manual" -Body $manualAuditBody | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/1/audit-trail" | ConvertTo-Json -Depth 8
Write-Host "v1.5 audit trail test completed" -ForegroundColor Green


Write-Host "Template Engine & Government Document Generator" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/government-documents/types" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/document-templates/seed-defaults" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/document-templates?limit=20" | ConvertTo-Json -Depth 8

if ($profiles.items.Count -gt 0) {
  $profileId = $profiles.items[0].id
  Write-Host "Generate government DOCX" -ForegroundColor Cyan
  $govDocBody = @{
    document_type = "APPROVAL_SUBMISSION"
    file_format = "docx"
    agency_name = "NGAN HANG CHINH SACH XA HOI"
    signer_title = "GIAM DOC TRUNG TAM CNTT"
    place_name = "Ha Noi"
  } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/government-documents/generate" -Body $govDocBody | ConvertTo-Json -Depth 8

  Write-Host "Generate government PDF" -ForegroundColor Cyan
  $govPdfBody = @{
    document_type = "APPROVAL_DECISION"
    file_format = "pdf"
    agency_name = "NGAN HANG CHINH SACH XA HOI"
    signer_title = "TONG GIAM DOC"
    place_name = "Ha Noi"
  } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/government-documents/generate" -Body $govPdfBody | ConvertTo-Json -Depth 8

  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/exported-documents?profile_id=$profileId" | ConvertTo-Json -Depth 8
}

Write-Host "v1.6 template engine test completed" -ForegroundColor Green

Write-Host "LDAP/SSO Foundation & Organization Access Control" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/auth/identity-provider/status" | ConvertTo-Json -Depth 8
Invoke-RestMethod "$BaseUrl/api/v1/auth/sso/login-hint" | ConvertTo-Json -Depth 8
$ldapBody = @{ username = "admin"; password = "Admin@123" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/auth/ldap-login" -Body $ldapBody | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/access-control/my-scope" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/access-control/policy" | ConvertTo-Json -Depth 8
if ($profiles.items.Count -gt 0) {
  $profileId = $profiles.items[0].id
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/access-check" | ConvertTo-Json -Depth 8
}
Write-Host "v1.7 LDAP/SSO foundation test completed" -ForegroundColor Green

Write-Host "Production Hardening" -ForegroundColor Cyan
Invoke-RestMethod "$BaseUrl/api/v1/health/liveness" | ConvertTo-Json -Depth 8
Invoke-RestMethod "$BaseUrl/api/v1/health/readiness" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/system/runtime" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/system/production-checklist" | ConvertTo-Json -Depth 8
Write-Host "v1.8 production hardening test completed" -ForegroundColor Green

Write-Host "Security Hardening" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/security/password-policy" | ConvertTo-Json -Depth 8
$weakPasswordBody = @{ password = "abc" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/security/password-policy/validate" -Body $weakPasswordBody | ConvertTo-Json -Depth 8
$strongPasswordBody = @{ password = "Strong@123" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/security/password-policy/validate" -Body $strongPasswordBody | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/security/summary" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/security/events?limit=10" | ConvertTo-Json -Depth 8
Write-Host "v1.9 security hardening test completed" -ForegroundColor Green

Write-Host "Release 2.0 readiness" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/info" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/data-footprint" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/readiness" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/uat-checklist" | ConvertTo-Json -Depth 8
Write-Host "v2.0 release readiness test completed" -ForegroundColor Green


Write-Host "Multi-Organization Management v2.2" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/organizations/tree" | ConvertTo-Json -Depth 12
$orgs = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/organizations?limit=20"
$orgs | ConvertTo-Json -Depth 8
if ($orgs.items.Count -gt 0) {
  $orgId = $orgs.items[0].id
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/organizations/$orgId/scope-summary" | ConvertTo-Json -Depth 10
}
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/access-control/my-scope" | ConvertTo-Json -Depth 10
Write-Host "v2.2 multi-organization management test completed" -ForegroundColor Green

Write-Host "Digital Signature & Electronic Dossier v2.3" -ForegroundColor Cyan
if ($profiles.items.Count -gt 0) {
  $profileId = $profiles.items[0].id
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/dossier/summary" | ConvertTo-Json -Depth 8

  $versionBody1 = @{
    title = "Ho so dien tu ban 1"
    change_summary = "Tao phien ban ho so dien tu tu script v2.3"
  } | ConvertTo-Json
  $v1 = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/versions" -Body $versionBody1
  $v1 | ConvertTo-Json -Depth 8

  $versionBody2 = @{
    title = "Ho so dien tu ban 2"
    change_summary = "Tao phien ban thu hai de kiem tra compare"
  } | ConvertTo-Json
  $v2 = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/versions" -Body $versionBody2
  $v2 | ConvertTo-Json -Depth 8

  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/versions" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profile-versions/$($v2.id)" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profile-versions/compare?from_version_id=$($v1.id)&to_version_id=$($v2.id)" | ConvertTo-Json -Depth 8

  $signBody = @{
    signer_role = "Lanh dao phe duyet"
    sign_method = "MOCK"
    comment = "Ky so mo phong tu script v2.3"
  } | ConvertTo-Json
  $sig = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profile-versions/$($v2.id)/sign" -Body $signBody
  $sig | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/signatures" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/dossier/summary" | ConvertTo-Json -Depth 8
}
Write-Host "v2.3 digital signature and electronic dossier test completed" -ForegroundColor Green

Write-Host "Government Template Center v2.4" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/document-templates/center/summary" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/document-templates/variables" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/government-documents/types" | ConvertTo-Json -Depth 8
$templateCode = "TPL_TEST_" + (Get-Date -Format "yyyyMMddHHmmss")
$templateBody = @{
  code = $templateCode
  name = "Mau test v2.4"
  document_type = "PROFILE_EXPLANATION"
  category = "GOVERNMENT"
  version = "1.0"
  agency_name = "NGAN HANG CHINH SACH XA HOI"
  official_number_prefix = "/NHCS-CNTT"
  description = "Template tao tu script test v2.4"
  is_active = $true
  sort_order = 88
} | ConvertTo-Json
$template = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/document-templates" -Body $templateBody
$template | ConvertTo-Json -Depth 8
$templateFile = Join-Path $PSScriptRoot "template-test-v2.4.txt"
Set-Content -Path $templateFile -Value "Template test v2.4: {{ profile.profile_code }} - {{ system.name }}" -Encoding UTF8
& curl.exe -s -X POST "$BaseUrl/api/v1/document-templates/$($template.id)/upload" -H "Authorization: Bearer $token" -F "file=@$templateFile" | ConvertFrom-Json | ConvertTo-Json -Depth 8
Invoke-RestMethod -Method Post -Headers $headers "$BaseUrl/api/v1/document-templates/$($template.id)/activate" | ConvertTo-Json -Depth 8
if ($profiles.items.Count -gt 0) {
  $profileId = $profiles.items[0].id
  $previewBody = @{ profile_id = $profileId; template_code = $templateCode; document_type = "PROFILE_EXPLANATION" } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/document-templates/preview-context" -Body $previewBody | ConvertTo-Json -Depth 10
}
Write-Host "v2.4 government template center test completed" -ForegroundColor Green

Write-Host "SLA & Risk Register v2.5" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/risk-registers/summary" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/sla/policies/seed-defaults" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/sla/policies?limit=20" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/sla/summary" | ConvertTo-Json -Depth 10
$riskCode = "RR-TEST-" + (Get-Date -Format "yyyyMMddHHmmss")
$riskBody = @{
  risk_code = $riskCode
  title = "Rui ro test v2.5"
  description = "Rui ro tao tu script test SLA & Risk Register"
  category = "COMPLIANCE"
  likelihood = 4
  impact = 4
  owner = "Can bo ATTT"
  mitigation_plan = "Bo sung bien phap kiem soat va tai lieu minh chung"
} | ConvertTo-Json
if ($profiles.items.Count -gt 0) {
  $riskObj = $riskBody | ConvertFrom-Json
  $riskObj | Add-Member -NotePropertyName profile_id -NotePropertyValue $profiles.items[0].id
  $riskBody = $riskObj | ConvertTo-Json
}
$risk = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/risk-registers" -Body $riskBody
$risk | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/risk-registers?limit=20" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/risk-registers/summary" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/risk-registers/$($risk.id)/close" | ConvertTo-Json -Depth 8
Write-Host "v2.5 SLA and Risk Register test completed" -ForegroundColor Green
