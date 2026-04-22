@echo off
cd /d "C:\path\to\BytePulse"

if not exist data mkdir data

set PYTHONW=C:\path\to\BytePulse\.venv\Scripts\pythonw.exe

if not exist "%PYTHONW%" (
    echo %date% %time% ERROR: pythonw not found at %PYTHONW% >> data\startup.log
    exit /b 1
)

if exist data\tracker.lock (
    for /f "tokens=1" %%i in (data\tracker.lock) do (
        C:\Windows\System32\taskkill.exe /F /PID %%i >nul 2>&1
    )
    del /f data\tracker.lock >nul 2>&1
)

if exist data\tray.lock (
    for /f "tokens=1" %%i in (data\tray.lock) do (
        C:\Windows\System32\taskkill.exe /F /PID %%i >nul 2>&1
    )
    del /f data\tray.lock >nul 2>&1
)

C:\Windows\System32\timeout.exe /t 3 /nobreak >nul

start "" "%PYTHONW%" src\tray.py
C:\Windows\System32\timeout.exe /t 5 /nobreak >nul
start "" "%PYTHONW%" src\tracker.py

echo %date% %time% BytePulse started >> data\startup.log
exit