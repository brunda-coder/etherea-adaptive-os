# Cleanup Apply for Etherea repo (Windows PowerShell)
# WARNING: This DELETES files/folders. Read it first.
# Run in repo root:   powershell -ExecutionPolicy Bypass -File tools\cleanup_apply.ps1

$targets = @(
  "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
  "build", "dist"
)

Write-Host "`n=== Deleting common cache/build folders (safe) ===`n"
foreach ($t in $targets) {
  Get-ChildItem -Path . -Recurse -Force -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq $t } |
    ForEach-Object { Remove-Item -Recurse -Force $_.FullName; Write-Host "Deleted: $($_.FullName)" }
}

Write-Host "`n=== Deleting common backup file extensions (careful) ===`n"
Get-ChildItem -Path . -Recurse -Force -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match "\.(save|bak|old|tmp|swp)$" } |
  ForEach-Object { Remove-Item -Force $_.FullName; Write-Host "Deleted: $($_.FullName)" }

Write-Host "`nDone. Run: git status`n"
