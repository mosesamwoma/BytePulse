@echo off
cd /d "C:\path\to\BytePulse"

if not exist data mkdir data

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found.
    pause
    exit /b 1
)

:loop
echo Starting WiFi tracker...
python src\tracker.py
echo Tracker stopped, restarting in 10 seconds...
timeout /t 10 /nobreak >nul
goto loop