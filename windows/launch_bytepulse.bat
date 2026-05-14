@echo off
REM BytePulse Launcher
REM Activates venv, handles process cleanup, starts tray + tracker with staggered startup

cd /d "%~dp0"

if not exist venv (
    color 0C
    echo [ERROR] Virtual environment not found
    echo Run setup_bytepulse.bat first to create venv and install dependencies
    color 0F
    pause
    exit /b 1
)

if not exist data (
    mkdir data
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    color 0C
    echo [ERROR] Failed to activate virtual environment
    color 0F
    pause
    exit /b 1
)

set PYTHONW=%CD%\venv\Scripts\pythonw.exe

if exist data\tracker.lock (
    for /f "tokens=1" %%i in (data\tracker.lock) do (
        taskkill.exe /F /PID %%i >nul 2>&1
    )
    del /f data\tracker.lock >nul 2>&1
)

if exist data\tray.lock (
    for /f "tokens=1" %%i in (data\tray.lock) do (
        taskkill.exe /F /PID %%i >nul 2>&1
    )
    del /f data\tray.lock >nul 2>&1
)

timeout.exe /t 2 /nobreak >nul 2>&1

start "" "%PYTHONW%" src\tray.py
timeout.exe /t 5 /nobreak >nul 2>&1
start "" "%PYTHONW%" src\tracker.py

echo %date% %time% BytePulse started >> data\startup.log