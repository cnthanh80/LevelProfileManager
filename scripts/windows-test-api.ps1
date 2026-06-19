$ErrorActionPreference = "Stop"

$BaseUrl = "http://localhost:8000"
Write-Host "Testing LevelProfileManager API v0.4..." -ForegroundColor Cyan

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

Write-Host "Security requirements" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/security-requirements?limit=5" | ConvertTo-Json -Depth 5

Write-Host "Level 3 requirements" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/security-requirements/by-level/3" | ConvertTo-Json -Depth 5

Write-Host "Profiles" -ForegroundColor Cyan
$profiles = Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/level-profiles?limit=5"
$profiles | ConvertTo-Json -Depth 5

if ($profiles.items.Count -gt 0) {
  $profileId = $profiles.items[0].id
  Write-Host "Generate checklist for profile $profileId" -ForegroundColor Cyan
  Invoke-RestMethod -Method Post -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/generate-checklist" | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/checklist" | ConvertTo-Json -Depth 6
  Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/profiles/$profileId/compliance-summary" | ConvertTo-Json -Depth 6
}

Write-Host "v0.4 API test completed" -ForegroundColor Green
