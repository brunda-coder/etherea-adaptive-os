$ErrorActionPreference = "Stop"

param(
    [string]$Version = ""
)

if ($Version.StartsWith("v")) {
    $Version = $Version.Substring(1)
}

if (-Not (Test-Path ".venv")) {
    python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-core.txt -r requirements-desktop.txt -r requirements-ui.txt
python -m pip install pyinstaller

if ($Version -eq "") {
    $Version = python -c "from corund.version import __version__; print(__version__)"
}

if ($Version.StartsWith("v")) {
    $Version = $Version.Substring(1)
}

if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

pyinstaller --clean --noconfirm --onefile etherea.spec

$exePath = "dist\Etherea.exe"
if (-Not (Test-Path $exePath)) {
    throw "Build failed: $exePath not found."
}

$target = "dist\Etherea-$Version-Windows.exe"
Move-Item -Force $exePath $target
$exePath = $target
if ($Version -ne "") {
    $target = "dist\Etherea-$Version-Windows.exe"
    Move-Item -Force $exePath $target
    $exePath = $target
}

$env:ETHEREA_DATA_DIR = "$(Get-Location)\selftest"
& $exePath --self-test
if ($LASTEXITCODE -ne 0) {
    throw "Self-test failed."
}
