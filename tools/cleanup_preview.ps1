# Cleanup Preview for Etherea repo (Windows PowerShell)
# This script ONLY PREVIEWS what would be deleted.
# Run in repo root:   powershell -ExecutionPolicy Bypass -File tools\cleanup_preview.ps1

$patterns = @(
  "*.save", "*.bak", "*.old", "*.tmp", "*.swp",
  "*_backup*", "*backup*", "*~",
  "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
  "build", "dist", "*.egg-info",
  "*.log"
)

Write-Host "`n=== Preview files/folders matching cleanup patterns ===`n"
foreach ($p in $patterns) {
  Get-ChildItem -Path . -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like $p -or $_.FullName -like "*\$p\*" } |
    Select-Object FullName
}

Write-Host "`nTip: Use git status first. Only delete if you understand what you're removing.`n"
