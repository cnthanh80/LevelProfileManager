$ErrorActionPreference = "Stop"

$BaseUrl = "http://localhost:8000"
Write-Host "Testing LevelProfileManager API v0.6..." -ForegroundColor Cyan

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
}

Write-Host "v0.6 API test completed" -ForegroundColor Green
