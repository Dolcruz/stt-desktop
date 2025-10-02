@echo off
REM STTDesktop mit Administrator-Rechten starten
REM Dadurch funktionieren die systemweiten Hotkeys (Alt+T, ESC) ueberall

echo.
echo ========================================
echo   STTDesktop - Admin-Modus
echo ========================================
echo.
echo Startet die App mit Administrator-Rechten.
echo Damit funktionieren Alt+T und ESC systemweit!
echo.

REM Pruefe ob die .exe existiert
if not exist "STTDesktop.exe" (
    echo FEHLER: STTDesktop.exe nicht gefunden!
    echo.
    echo Bitte diese .bat-Datei neben die STTDesktop.exe legen.
    echo.
    pause
    exit /b 1
)

REM Starte mit Admin-Rechten
echo Starte STTDesktop mit Admin-Rechten...
powershell -Command "Start-Process '%~dp0STTDesktop.exe' -Verb RunAs"

REM Warte kurz und schliesse
timeout /t 2 /nobreak >nul
exit

