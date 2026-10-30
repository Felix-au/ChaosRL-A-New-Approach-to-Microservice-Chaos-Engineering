@echo off
echo ========================================================
echo ChaosRL Presentation UI Launcher
echo ========================================================
cd /d "%~dp0"

echo [1/2] Verifying and updating data bundle...
python scripts/build_data.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Data build failed. Aborting.
    pause
    exit /b 1
)

echo [2/2] Launching Presentation Web Server...
npm run present

