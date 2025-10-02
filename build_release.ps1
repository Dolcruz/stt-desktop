# Build Script für Release
# Baut die .exe und bereitet sie für GitHub Release vor

Write-Host "🏗️  Building STTDesktop Release..." -ForegroundColor Cyan
Write-Host ""

# Prüfe ob venv existiert
if (-not (Test-Path ".venv")) {
    Write-Host "❌ Virtual Environment nicht gefunden!" -ForegroundColor Red
    Write-Host "Bitte führe zuerst aus: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Aktiviere venv
Write-Host "📦 Aktiviere Virtual Environment..." -ForegroundColor Green
& ".venv\Scripts\Activate.ps1"

# Installiere Dependencies
Write-Host "📥 Installiere Dependencies..." -ForegroundColor Green
pip install -r requirements.txt --quiet

# Installiere PyInstaller
Write-Host "📥 Installiere PyInstaller..." -ForegroundColor Green
pip install pyinstaller --quiet

# Lösche alte Builds
Write-Host "🧹 Lösche alte Builds..." -ForegroundColor Green
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Baue .exe
Write-Host "🔨 Baue STTDesktop.exe..." -ForegroundColor Green
Write-Host ""
pyinstaller --clean STTDesktop.spec

# Prüfe ob Build erfolgreich
if (Test-Path "dist\STTDesktop.exe") {
    Write-Host ""
    Write-Host "✅ Build erfolgreich!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 Die fertige .exe befindet sich in:" -ForegroundColor Cyan
    Write-Host "   dist\STTDesktop.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "📤 Nächste Schritte:" -ForegroundColor Yellow
    Write-Host "   1. Teste die .exe: .\dist\STTDesktop.exe" -ForegroundColor White
    Write-Host "   2. Erhöhe VERSION (z.B. 1.0.0 -> 1.0.1)" -ForegroundColor White
    Write-Host "   3. Erstelle GitHub Release:" -ForegroundColor White
    Write-Host "      https://github.com/Dolcruz/stt-desktop/releases/new" -ForegroundColor Cyan
    Write-Host "   4. Lade dist\STTDesktop.exe hoch" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Build fehlgeschlagen!" -ForegroundColor Red
    Write-Host "Prüfe die Fehler oben." -ForegroundColor Yellow
    exit 1
}

