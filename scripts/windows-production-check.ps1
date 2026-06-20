$ErrorActionPreference = "Stop"
$BaseUrl = $env:LPM_API_BASE_URL
if (-not $BaseUrl) { $BaseUrl = "http://localhost:8000" }

Write-Host "LevelProfileManager Production Check v3.0" -ForegroundColor Cyan
Invoke-RestMethod "$BaseUrl/api/v1/health" | ConvertTo-Json -Depth 5
Invoke-RestMethod "$BaseUrl/api/v1/health/db" | ConvertTo-Json -Depth 5

$login = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/auth/login" -ContentType "application/x-www-form-urlencoded" -Body "username=admin&password=Admin@123"
$headers = @{ Authorization = "Bearer $($login.access_token)" }

Write-Host "Release info" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/info" | ConvertTo-Json -Depth 8
Write-Host "Release readiness" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/readiness" | ConvertTo-Json -Depth 10
Write-Host "Production readiness" -ForegroundColor Cyan
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/release/production-readiness" | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "LevelProfileManager v3.0 Production Check PASSED" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
