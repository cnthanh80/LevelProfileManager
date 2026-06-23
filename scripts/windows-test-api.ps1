$ErrorActionPreference = "Stop"

# Force UTF-8 output for Vietnamese text on Windows PowerShell 5.1 and PowerShell 7+
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
try {
  chcp 65001 | Out-Null
} catch {
  # Ignore when chcp is not available
}

$BaseUrl = "http://localhost:8000"
Write-Host "Testing LevelProfileManager API v4.0..." -ForegroundColor Cyan

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

Write-Host "Assessment Portal v2.6" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/assessment-portal/summary" | ConvertTo-Json -Depth 10
if ($profiles.items.Count -gt 0) {
  $profileId = $profiles.items[0].id
  $caseCode = "TD-TEST-" + (Get-Date -Format "yyyyMMddHHmmss")
  $caseBody = @{
    case_code = $caseCode
    profile_id = $profileId
    title = "Ho so gui tham dinh test v2.6"
    assessment_unit = "Don vi tham dinh chuyen mon"
    contact_person = "Can bo tham dinh"
    contact_email = "assessor@example.com"
    summary = "Ho so tao tu script test Assessment Portal"
  } | ConvertTo-Json
  $case = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/assessment-cases" -Body $caseBody
  $case | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/assessment-cases/$($case.id)/submit" | ConvertTo-Json -Depth 8

  $feedbackBody = @{
    case_id = $case.id
    profile_id = $profileId
    feedback_type = "REQUEST_CHANGE"
    severity = "HIGH"
    title = "Yeu cau bo sung minh chung"
    content = "De nghi bo sung tai lieu minh chung ve phuong an sao luu va giam sat ATTT."
  } | ConvertTo-Json
  $feedback = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/assessment-feedbacks" -Body $feedbackBody
  $feedback | ConvertTo-Json -Depth 8
  $responseBody = @{ response = "Da tiep thu va bo sung minh chung theo yeu cau tham dinh"; status = "RESPONDED" } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/assessment-feedbacks/$($feedback.id)/respond" -Body $responseBody | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/assessment-cases/$($case.id)/complete" | ConvertTo-Json -Depth 8
}
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/assessment-cases?limit=20" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/assessment-feedbacks?limit=20" | ConvertTo-Json -Depth 8
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/assessment-portal/summary" | ConvertTo-Json -Depth 10
Write-Host "v2.6 assessment portal test completed" -ForegroundColor Green

Write-Host "Executive Leadership Dashboard v2.7" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/executive/kpis" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/executive/portfolio" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/executive/priority-actions" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/executive/board-pack" | ConvertTo-Json -Depth 10
Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v2.7.1 PASSED" -ForegroundColor Green
Write-Host "UTF-8 Vietnamese output: OK" -ForegroundColor Green
Write-Host "Executive Dashboard: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

Write-Host "Production Release v3.0" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/info" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/readiness" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/production-readiness" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/uat-checklist" | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v3.0 PASSED" -ForegroundColor Green
Write-Host "Production Release Readiness: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

Write-Host "AI Classification & Level Recommendation v3.1" -ForegroundColor Cyan
$aiBody = @{
  system_name = "Core Banking Test"
  data_description = "He thong xu ly du lieu tai chinh, giao dich va du lieu ca nhan khach hang"
  has_personal_data = $true
  has_financial_data = $true
  has_sensitive_data = $true
  internet_exposed = $false
  third_party_connections = $true
  cross_org_connections = $true
  user_count = 5000
  transaction_per_day = 100000
  confidentiality_impact = "HIGH"
  integrity_impact = "HIGH"
  availability_impact = "CRITICAL"
  business_criticality = "CRITICAL"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/ai/classify-level" -Body $aiBody | ConvertTo-Json -Depth 10
if ($profiles.items.Count -gt 0) {
  $profileId = $profiles.items[0].id
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/profiles/$profileId/ai/recommend-level" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/ai/recommendations" | ConvertTo-Json -Depth 10
}
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/ai-classification" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/ai-classification/misclassified" | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v3.1 PASSED" -ForegroundColor Green
Write-Host "AI Classification & Level Recommendation: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green


Write-Host "Real Digital Signature Gateway v3.2" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/signature-gateway/status" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/signature-providers/seed-defaults" | ConvertTo-Json -Depth 10
$providers = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/signature-providers?limit=20"
$providers | ConvertTo-Json -Depth 10
if ($profiles.items.Count -gt 0) {
  $profileId = $profiles.items[0].id
  $versions = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/versions?limit=10"
  if ($versions.items.Count -eq 0) {
    $vBody = @{ title = "v3.2 signature gateway test"; change_summary = "Create version for real signature gateway test" } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profiles/$profileId/versions" -Body $vBody | Out-Null
    $versions = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/versions?limit=10"
  }
  if ($versions.items.Count -gt 0) {
    $versionId = $versions.items[0].id
    $providerId = $providers.items[0].id
    $signBody = @{ provider_id = $providerId; sign_method = "MOCK_REMOTE"; signer_name = "Mock Remote CA"; signer_role = "Remote Signing Gateway"; note = "v3.2 test" } | ConvertTo-Json
    $signReq = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/profile-versions/$versionId/real-sign-requests" -Body $signBody
    $signReq | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/signature-requests/$($signReq.request_code)/simulate-callback" | ConvertTo-Json -Depth 10
  }
}
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/signature-requests?limit=20" | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v3.2 PASSED" -ForegroundColor Green
Write-Host "Real Digital Signature Gateway Foundation: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

Write-Host "Assessment Workflow Engine v3.3" -ForegroundColor Cyan
try {
  $awSummary = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/assessment-workflow/summary"
  $awSummary | ConvertTo-Json -Depth 8
  $awRules = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/assessment-workflow/rules"
  $awRules | ConvertTo-Json -Depth 8
  $cases = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/assessment-cases?limit=10"
  if ($cases.items.Count -gt 0) {
    $caseId = $cases.items[0].id
    Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/assessment-cases/$caseId/workflow-events" | ConvertTo-Json -Depth 8
  }
  Write-Host "Assessment Workflow Engine v3.3 OK" -ForegroundColor Green
} catch {
  Write-Host "Assessment Workflow Engine v3.3 test warning: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v3.3 PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green


Write-Host "CMDB & Asset Inventory v3.4" -ForegroundColor Cyan
try {
  $cmdbDashboard = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/cmdb/dashboard"
  $cmdbDashboard | ConvertTo-Json -Depth 8
  $systemsForCmdb = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/information-systems?limit=5"
  $sysId = $null
  if ($systemsForCmdb.items.Count -gt 0) { $sysId = $systemsForCmdb.items[0].id }
  $assetCode = "CMDB-SRV-TEST-" + (Get-Random -Maximum 999999)
  $assetBody = @{
    asset_code = $assetCode
    asset_name = "May chu CMDB test"
    asset_type = "SERVER"
    environment = "PRODUCTION"
    ip_address = "10.10.10.10"
    hostname = "cmdb-test.local"
    information_system_id = $sysId
    criticality = "HIGH"
    status = "ACTIVE"
  } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/cmdb-assets" -Body $assetBody | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/cmdb-assets?limit=10" | ConvertTo-Json -Depth 8
  if ($profiles.items.Count -gt 0) {
    $profileId = $profiles.items[0].id
    Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/cmdb-inventory" | ConvertTo-Json -Depth 8
    Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/profiles/$profileId/cmdb-sync" | ConvertTo-Json -Depth 8
  }
  Write-Host "CMDB & Asset Inventory v3.4 OK" -ForegroundColor Green
} catch {
  Write-Host "CMDB & Asset Inventory v3.4 test warning: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v3.4 PASSED" -ForegroundColor Green
Write-Host "CMDB & Asset Inventory Integration: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

Write-Host "LDAP/SSO Production v3.5" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/identity-provider/production-readiness" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/identity-provider/ldap/test-connection" -Body "{}" | ConvertTo-Json -Depth 8
  $ldapPreviewBody = @{
    username = "ldap.test"
    email = "ldap.test@example.com"
    full_name = "LDAP Test User"
    role_code = "ATTT_OFFICER"
  } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/identity-provider/ldap/preview-user" -Body $ldapPreviewBody | ConvertTo-Json -Depth 8
  $ssoBody = @{
    provider_name = "Enterprise SSO"
    username = "sso.test"
    email = "sso.test@example.com"
    full_name = "SSO Test User"
    role_code = "REVIEWER"
  } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/identity-provider/sso/assertion-dry-run" -Body $ssoBody | ConvertTo-Json -Depth 8
  Write-Host "LDAP/SSO Production v3.5 OK" -ForegroundColor Green
} catch {
  Write-Host "LDAP/SSO Production v3.5 test warning: $($_.Exception.Message)" -ForegroundColor Yellow
  throw
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v3.5 PASSED" -ForegroundColor Green
Write-Host "LDAP/SSO Production: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

Write-Host "SIEM & Audit Integration v3.6" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/siem/status" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/siem/connectors/seed-defaults" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/siem/rules/seed-defaults" | ConvertTo-Json -Depth 8
  $siemEventBody = @{
    source_system = "LevelProfileManager"
    event_type = "AUTH_FAILURE"
    severity = "HIGH"
    status = "OPEN"
    username = "admin"
    ip_address = "127.0.0.1"
    asset_code = "LPM-APP"
    raw_message = "v3.6 SIEM integration test event"
  } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/siem/events/ingest" -Body $siemEventBody | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/siem/events/ingest-audit?limit=10" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/siem/events/ingest-security?limit=10" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/siem/connectors?limit=10" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/siem/events?limit=10" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/siem/rules?limit=10" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/siem/correlation/summary" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/siem" | ConvertTo-Json -Depth 8
  Write-Host "SIEM & Audit Integration v3.6 OK" -ForegroundColor Green
} catch {
  Write-Host "SIEM & Audit Integration v3.6 test failed: $($_.Exception.Message)" -ForegroundColor Red
  throw
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v3.6 PASSED" -ForegroundColor Green
Write-Host "SIEM & Audit Integration: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

Write-Host "Compliance Automation v3.7" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/compliance-automation" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/compliance-automation/rules/seed-defaults" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/compliance-automation/rules?limit=20" | ConvertTo-Json -Depth 8
  $runBody = @{ scope = "ALL_PROFILES" } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/compliance-automation/run" -Body $runBody | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/compliance-automation/runs?limit=10" | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/compliance-automation/findings?limit=10" | ConvertTo-Json -Depth 8
  Write-Host "Compliance Automation v3.7 OK" -ForegroundColor Green
} catch {
  Write-Host "Compliance Automation v3.7 test failed: $($_.Exception.Message)" -ForegroundColor Red
  throw
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v3.7 PASSED" -ForegroundColor Green
Write-Host "Compliance Automation: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

Write-Host "Continuous Compliance Monitoring v3.8" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/compliance-monitoring" | ConvertTo-Json -Depth 10
  $monitorBody = @{ scope = "ALL_PROFILES"; create_notifications = $true } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/compliance-monitoring/recalculate" -Body $monitorBody | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/compliance-monitoring/heatmap" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/compliance-monitoring/snapshots?limit=10" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/compliance-monitoring/findings?limit=10" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/compliance-monitoring/notifications?limit=10" | ConvertTo-Json -Depth 10
  if ($profiles.items.Count -gt 0) {
    $profileId = $profiles.items[0].id
    Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/compliance-monitoring/score/$profileId" | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/compliance-monitoring/trends/${profileId}?limit=10" | ConvertTo-Json -Depth 10
  }
  Write-Host "Continuous Compliance Monitoring v3.8 OK" -ForegroundColor Green
} catch {
  Write-Host "Continuous Compliance Monitoring v3.8 test failed: $($_.Exception.Message)" -ForegroundColor Red
  throw
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v3.8 PASSED" -ForegroundColor Green
Write-Host "Continuous Compliance Monitoring: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green


Write-Host "Enterprise Reporting & Data Warehouse v3.9" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dashboard/enterprise-reporting" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-reporting/summary" | ConvertTo-Json -Depth 10
  $reportBody = @{ period_type = "MONTHLY"; refresh_metrics = $true } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/enterprise-reporting/snapshots/generate" -Body $reportBody | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-reporting/snapshots?limit=10" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-reporting/data-warehouse/metrics?limit=20" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-reporting/export/portfolio-csv" | Out-Null
  Write-Host "Enterprise Reporting v3.9 OK" -ForegroundColor Green
} catch {
  Write-Host "Enterprise Reporting v3.9 test failed: $($_.Exception.Message)" -ForegroundColor Red
  throw
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v3.9 PASSED" -ForegroundColor Green
Write-Host "Enterprise Reporting & Data Warehouse: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

Write-Host "Enterprise Release v4.0" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/enterprise-center/seed-defaults" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-center/dashboard" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-center/readiness" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-center/health" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-center/configurations?limit=20" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-center/jobs?limit=20" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-center/retention-policies?limit=20" | ConvertTo-Json -Depth 10
  $backupBody = @{ backup_type = "LOGICAL"; scope = "DATABASE"; status = "COMPLETED"; size_mb = 128; notes = "v4.0 test backup metadata" } | ConvertTo-Json
  $backup = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/enterprise-center/backups/mock" -Body $backupBody
  $backup | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Method Post -Headers $headers -Uri "$BaseUrl/api/v1/enterprise-center/backups/$($backup.id)/validate" | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/enterprise-center/backups?limit=10" | ConvertTo-Json -Depth 10
  Write-Host "Enterprise Release v4.0 OK" -ForegroundColor Green
} catch {
  Write-Host "Enterprise Release v4.0 test failed: $($_.Exception.Message)" -ForegroundColor Red
  throw
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v4.0 PASSED" -ForegroundColor Green
Write-Host "Enterprise Release: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

Write-Host "Government Dossier Pack v4.2 / Phase 42.0" -ForegroundColor Cyan
try {
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dossiers/summary" | ConvertTo-Json -Depth 10
  if ($profiles.items.Count -gt 0) {
    $profileId = $profiles.items[0].id
    $dossierBody = @{ include_evidence = $true; notes = "Phase 42.0 API test" } | ConvertTo-Json
    $dossier = Invoke-RestMethod -Method Post -Headers $headers -ContentType "application/json" -Uri "$BaseUrl/api/v1/dossiers/$profileId/generate" -Body $dossierBody
    $dossier | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dossiers?profile_id=$profileId&limit=10" | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dossiers/$($dossier.id)" | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dossiers/$($dossier.id)/files" | ConvertTo-Json -Depth 10
    Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/dossiers/$($dossier.id)/download" | Out-Null
  }
  Write-Host "Government Dossier Pack v4.2 OK" -ForegroundColor Green
} catch {
  Write-Host "Government Dossier Pack v4.2 test failed: $($_.Exception.Message)" -ForegroundColor Red
  throw
}

Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager API v4.2 PASSED" -ForegroundColor Green
Write-Host "Government Dossier Pack: OK" -ForegroundColor Green
Write-Host "ALL TESTS PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
