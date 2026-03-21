@echo off
cd /d "C:\path\to\BytePulse"

if not exist data mkdir data

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found.
    pause
    exit /b 1
)

if exist data\tracker.lock (
    for /f %%i in (data\tracker.lock) do (
        taskkill /F /PID %%i >nul 2>&1
    )
    del /f data\tracker.lock >nul 2>&1
    timeout /t 2 /nobreak >nul
)

wmic process where "name='python.exe' and commandline like '%%tracker%%'" delete >nul 2>&1
timeout /t 1 /nobreak >nul

:loop
echo Starting WiFi tracker...
python src\tracker.py
echo Tracker stopped, restarting in 10 seconds...
timeout /t 10 /nobreak >nul
goto loop