param(
  [Parameter(Mandatory=$true)]
  [string]$BackupFile
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path $BackupFile)) { throw "Backup file not found: $BackupFile" }

Write-Host "Restoring PostgreSQL backup: $BackupFile" -ForegroundColor Yellow
Write-Host "This will load SQL into level_profile_db. Make sure you understand the impact before continuing." -ForegroundColor Yellow
$confirm = Read-Host "Type RESTORE to continue"
if ($confirm -ne "RESTORE") { Write-Host "Restore cancelled"; exit 0 }

Get-Content $BackupFile | docker exec -i lpm_postgres psql -U lpm_user -d level_profile_db
Write-Host "Restore completed" -ForegroundColor Green
