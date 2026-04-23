@echo off
echo ===============================================
echo   Telegram Shop Pro - Windows Quick Setup
echo ===============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found. Install Python 3.11+ first.
    pause
    exit /b 1
)

echo [*] Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)

echo.
echo [*] Launching desktop GUI...
python scripts\run_gui.py
pause
