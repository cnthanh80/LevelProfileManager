$docs = @(
  "docs\uat\UAT_PLAN_v4.1.md",
  "docs\uat\UAT_TEST_CASES_v4.1.md",
  "docs\user-guide\USER_GUIDE_ATTT_OFFICER.md",
  "docs\admin-guide\ADMIN_GUIDE.md",
  "docs\operations\OPERATIONS_RUNBOOK.md",
  "docs\security\SECURITY_TEST_CHECKLIST.md",
  "docs\release\RELEASE_NOTES_v4.1.md"
)
foreach ($doc in $docs) {
  if (Test-Path $doc) {
    Write-Host $doc
  }
}
Write-Host "Open docs folder..."
Invoke-Item "docs"
