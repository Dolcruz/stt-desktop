@echo off
REM Speech-to-Text App mit Admin-Rechten starten
REM Dadurch funktionieren die globalen Hotkeys (Alt+T, ESC) systemweit

echo Starting Speech-to-Text with Administrator privileges...
echo This enables global hotkeys (Alt+T, ESC) to work everywhere.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH!
    echo Please install Python or add it to your PATH.
    pause
    exit /b 1
)

REM Start the app with admin rights
powershell -Command "Start-Process python -ArgumentList 'main.py' -Verb RunAs -WorkingDirectory '%cd%'"

echo.
echo App started! Close this window.
timeout /t 2 >nul
exit
