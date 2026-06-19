$ErrorActionPreference = "Stop"
Write-Host "Applying v2.2.3 hotfix..."
$old = "backend\alembic\versions\0014_multi_organization_management.py"
if (Test-Path $old) {
    Remove-Item $old -Force
    Write-Host "Removed old migration: $old"
}
Write-Host "Hotfix cleanup completed. Now run: docker compose up -d --build"
