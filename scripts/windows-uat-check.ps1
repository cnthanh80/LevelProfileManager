$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$BaseUrl = "http://localhost:8000"
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "LevelProfileManager UAT Check v4.1" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

Write-Host "1. Check Docker containers" -ForegroundColor Yellow
docker ps

Write-Host "2. Check backend health" -ForegroundColor Yellow
Invoke-RestMethod "$BaseUrl/api/v1/health" | ConvertTo-Json -Depth 10

Write-Host "3. Check database health" -ForegroundColor Yellow
Invoke-RestMethod "$BaseUrl/api/v1/health/db" | ConvertTo-Json -Depth 10

Write-Host "4. Login as admin" -ForegroundColor Yellow
$loginBody = "username=admin&password=Admin@123"
$login = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/auth/login" -ContentType "application/x-www-form-urlencoded" -Body $loginBody
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Write-Host "Login OK" -ForegroundColor Green

Write-Host "5. Check current user" -ForegroundColor Yellow
Invoke-RestMethod -Headers $headers "$BaseUrl/api/v1/auth/me" | ConvertTo-Json -Depth 10

Write-Host "6. Check core dashboards when available" -ForegroundColor Yellow
$dashboardEndpoints = @(
  "/api/v1/dashboard/summary",
  "/api/v1/enterprise-center/readiness",
  "/api/v1/enterprise-reporting/dashboard"
)
foreach ($ep in $dashboardEndpoints) {
  try {
    Write-Host "GET $ep" -ForegroundColor DarkCyan
    Invoke-RestMethod -Headers $headers "$BaseUrl$ep" | ConvertTo-Json -Depth 8
  } catch {
    Write-Host "WARN: $ep not available or returned non-2xx. Continue UAT check." -ForegroundColor DarkYellow
  }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "UAT CHECK COMPLETED" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "Swagger : http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Docs    : docs/uat/UAT_TEST_CASES_v4.1.md" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
