# Build Script fuer Release
# Baut die .exe und bereitet sie fuer GitHub Release vor

Write-Host "Building STTDesktop Release..." -ForegroundColor Cyan
Write-Host ""

# Pruefe ob VERSION existiert
if (-not (Test-Path "VERSION")) {
    Write-Host "VERSION Datei nicht gefunden!" -ForegroundColor Red
    exit 1
}

$version = Get-Content "VERSION" -Raw
$version = $version.Trim()
Write-Host "Building Version: $version" -ForegroundColor Cyan
Write-Host ""

# Pruefe ob venv existiert
if (-not (Test-Path ".venv")) {
    Write-Host "Virtual Environment nicht gefunden!" -ForegroundColor Yellow
    Write-Host "Erstelle Virtual Environment..." -ForegroundColor Green
    python -m venv .venv
}

# Aktiviere venv
Write-Host "Aktiviere Virtual Environment..." -ForegroundColor Green
& ".venv\Scripts\Activate.ps1"

# Installiere Dependencies
Write-Host "Installiere Dependencies..." -ForegroundColor Green
pip install -r requirements.txt --quiet --upgrade

# Installiere PyInstaller
Write-Host "Installiere PyInstaller..." -ForegroundColor Green
pip install pyinstaller --quiet --upgrade

# Loesche alte Builds
Write-Host "Loesche alte Builds..." -ForegroundColor Green
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Baue .exe
Write-Host "Baue STTDesktop.exe (Version $version)..." -ForegroundColor Green
Write-Host ""
pyinstaller --clean --noconfirm STTDesktop.spec

# Pruefe ob Build erfolgreich
if (Test-Path "dist\STTDesktop.exe") {
    Write-Host ""
    Write-Host "Build erfolgreich!" -ForegroundColor Green
    Write-Host ""
    
    # Teste Version in .exe
    Write-Host "Teste ob VERSION inkludiert ist..." -ForegroundColor Cyan
    $fileSize = (Get-Item "dist\STTDesktop.exe").Length / 1MB
    Write-Host "Dateigroesse: $([math]::Round($fileSize, 2)) MB" -ForegroundColor White
    
    Write-Host ""
    Write-Host "Die fertige .exe befindet sich in:" -ForegroundColor Cyan
    Write-Host "dist\STTDesktop.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "Naechste Schritte:" -ForegroundColor Yellow
    Write-Host "1. Teste die .exe: .\dist\STTDesktop.exe" -ForegroundColor White
    Write-Host "2. Pruefe ob Version $version angezeigt wird" -ForegroundColor White
    Write-Host "3. Wenn alles OK: GitHub Release erstellen" -ForegroundColor White
    Write-Host "https://github.com/Dolcruz/stt-desktop/releases/new" -ForegroundColor Cyan
    Write-Host "4. Tag: v$version" -ForegroundColor White
    Write-Host "5. Lade dist\STTDesktop.exe hoch" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Build fehlgeschlagen!" -ForegroundColor Red
    Write-Host "Pruefe die Fehler oben." -ForegroundColor Yellow
    exit 1
}
