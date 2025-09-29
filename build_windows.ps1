# Requires: Python venv activated and pyinstaller installed
# Usage:  .\build_windows.ps1

Write-Host "Packaging STTDesktop..."

# Ensure pyinstaller is installed
pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..."
    pip install pyinstaller
}

# Clean previous dist/build
if (Test-Path dist) { Remove-Item -Recurse -Force dist }
if (Test-Path build) { Remove-Item -Recurse -Force build }

# Build windowed, onefile; include PySide6 plugins automatically
$iconPath = Join-Path (Get-Location) "assets\app.ico"

$iconArg = ""
if (Test-Path $iconPath) { $iconArg = "--icon `"$iconPath`"" }

pyinstaller --noconfirm --noconsole --onefile $iconArg --name "STTDesktop" main.py

Write-Host "Build finished. EXE at: dist\STTDesktop.exe"
