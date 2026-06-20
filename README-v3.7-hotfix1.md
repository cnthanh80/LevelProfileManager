# LevelProfileManager v3.7 Hotfix 1

Fixes:

- Backend import error: `ComplianceAutomationFindingRead` missing from `app.schemas.compliance_automation`.
- Updates `windows-test-api.ps1` banner from v2.7 to v3.7.
- Adds explicit final success summary to the PowerShell test script.

Deploy:

```powershell
cd D:\Projects\LevelProfileManager
docker compose down
# copy this hotfix over the current project
Get-ChildItem -Recurse *.ps1 | Unblock-File
docker compose up -d --build
powershell.exe -ExecutionPolicy Bypass -File .\scripts\windows-test-api.ps1
```

Commit:

```powershell
git add .
git commit -m "Hotfix v3.7.1 compliance automation schema import"
git tag v3.7.1
git push
git push origin v3.7.1
```
