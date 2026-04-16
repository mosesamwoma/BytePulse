@echo off
cd /d "."

if not exist data mkdir data

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. >> data\startup.log
    exit /b 1
)

:: Kill any running instances cleanly
if exist data\tracker.lock (
    for /f %%i in (data\tracker.lock) do (
        C:\Windows\System32\taskkill.exe /F /PID %%i >nul 2>&1
    )
    del /f data\tracker.lock >nul 2>&1
)

if exist data\tray.lock (
    for /f %%i in (data\tray.lock) do (
        C:\Windows\System32\taskkill.exe /F /PID %%i >nul 2>&1
    )
    del /f data\tray.lock >nul 2>&1
)

C:\Windows\System32\wbem\wmic.exe process where "name='pythonw.exe' and commandline like '%%tracker%%'" delete >nul 2>&1
C:\Windows\System32\wbem\wmic.exe process where "name='pythonw.exe' and commandline like '%%tray%%'" delete >nul 2>&1

C:\Windows\System32\timeout.exe /t 3 /nobreak >nul

:: Start tray first, then tracker after a short delay
start "" pythonw src\tray.py
C:\Windows\System32\timeout.exe /t 5 /nobreak >nul
start "" pythonw src\tracker.py

exit