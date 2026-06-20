$ErrorActionPreference = "Stop"
$BackupDir = $env:LPM_BACKUP_DIR
if (-not $BackupDir) { $BackupDir = ".\backups" }
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outFile = Join-Path $BackupDir "level_profile_db_$timestamp.sql"

Write-Host "Creating PostgreSQL backup: $outFile" -ForegroundColor Cyan
docker exec lpm_postgres pg_dump -U lpm_user -d level_profile_db | Out-File -Encoding utf8 $outFile
Write-Host "Backup completed: $outFile" -ForegroundColor Green
