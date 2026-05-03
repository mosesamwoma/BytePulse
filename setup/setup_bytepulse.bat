@echo off
REM BytePulse Complete Setup
REM One-click: dependencies, database, AND Task Scheduler registration
REM Auto-elevates to Administrator if needed

setlocal enabledelayedexpansion

REM Check if running as admin
net session >nul 2>&1
if errorlevel 1 (
    REM Not admin - elevate
    echo.
    echo ======================================================================
    echo BytePulse Setup - Requesting Administrator Privileges
    echo ======================================================================
    echo.
    echo This script needs admin rights to register auto-startup tasks.
    echo.
    echo A new admin PowerShell window will open.
    echo Please click 'Yes' on the UAC security prompt.
    echo.
    pause
    
    REM Get the full path to this batch file
    set "BATCH_FILE=%~f0"
    
    REM Re-run as admin
    powershell -Command "Start-Process cmd -ArgumentList '/c', '!BATCH_FILE!' -Verb RunAs"
    exit /b
)

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

cls
echo.
echo ======================================================================
echo BytePulse Complete Setup
echo Installing dependencies, database, and auto-startup registration
echo ======================================================================
echo.

echo [OK] Running as Administrator
echo.
set "ADMIN=1"

REM [1/8] Check Python
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python not found in PATH
    echo Download from: https://www.python.org/downloads/
    echo Check "Add Python to PATH" during installation
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set "PYTHON_VER=%%i"
echo [OK] %PYTHON_VER%
echo.

REM [2/8] Install dependencies
echo [2/8] Installing dependencies...
if not exist "requirements.txt" (
    color 0C
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)
echo       Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo       Installing packages...
python -m pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [WARNING] Some packages failed to install
    color 0F
) else (
    echo [OK] All dependencies installed
)
echo.

REM [3/8] Create directories
echo [3/8] Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo [OK] Directories created
echo.

REM [4/8] Initialize database
echo [4/8] Initializing database...
python -c "import sys; sys.path.insert(0, '.'); from database.database import init_db; init_db()" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Database will auto-create on first run
) else (
    echo [OK] Database initialized
)
echo.

REM [5/8] Admin check
echo [5/8] Checking Administrator privileges...
if %ADMIN%==1 (
    echo [OK] Running as Administrator
) else (
    color 0E
    echo [WARNING] NOT running as Administrator
    color 0F
)
echo.

REM [6/8] Register Task Scheduler (admin only)
if %ADMIN%==1 (
    echo [6/8] Registering Task Scheduler tasks...
    
    REM Get pythonw.exe path
    for /f "tokens=*" %%i in ('python -c "from pathlib import Path; import sys; print(str(Path(sys.executable).parent / 'pythonw.exe'))"') do set "PYTHONW=%%i"
    
    echo       Registering BytePulse-Tray...
    powershell -NoProfile -Command ^
        "$trigger = New-ScheduledTaskTrigger -AtLogOn;" ^
        "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew;" ^
        "Register-ScheduledTask -TaskName 'BytePulse-Tray' -Action (New-ScheduledTaskAction -Execute '!PYTHONW!' -Argument '\"%SCRIPT_DIR%src\tray.py\"' -WorkingDirectory '%SCRIPT_DIR%') -Trigger $trigger -Settings $settings -RunLevel Highest -Force" >nul 2>&1
    
    if !ERRORLEVEL!==0 (
        echo [OK] BytePulse-Tray registered
    ) else (
        color 0E
        echo [WARNING] BytePulse-Tray registration failed
        color 0F
    )
    
    echo       Registering BytePulse-Tracker (10s delay)...
    powershell -NoProfile -Command ^
        "$trigger = New-ScheduledTaskTrigger -AtLogOn;" ^
        "$trigger.Delay = 'PT10S';" ^
        "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew;" ^
        "Register-ScheduledTask -TaskName 'BytePulse-Tracker' -Action (New-ScheduledTaskAction -Execute '!PYTHONW!' -Argument '\"%SCRIPT_DIR%src\tracker.py\"' -WorkingDirectory '%SCRIPT_DIR%') -Trigger $trigger -Settings $settings -RunLevel Highest -Force" >nul 2>&1
    
    if !ERRORLEVEL!==0 (
        echo [OK] BytePulse-Tracker registered (10s delay)
    ) else (
        color 0E
        echo [WARNING] BytePulse-Tracker registration failed
        color 0F
    )
    echo.
) else (
    echo [6/8] Skipping Task Scheduler registration (requires admin)
    echo.
)

REM [7/8] Create launcher
echo [7/8] Creating launcher shortcut...
(
    echo @echo off
    echo REM BytePulse Launcher
    echo cd /d "%SCRIPT_DIR%"
    echo start "" pythonw.exe src\tray.py
    echo start "" pythonw.exe src\tracker.py
    echo exit
) > "%SCRIPT_DIR%launch_bytepulse.bat"
echo [OK] Created: launch_bytepulse.bat
echo.

REM [8/8] Final checks
echo [8/8] Final verification...
if not exist "app.py" (
    color 0C
    echo [ERROR] app.py not found
    pause
    exit /b 1
)
if not exist "src\tracker.py" (
    color 0C
    echo [ERROR] src\tracker.py not found
    pause
    exit /b 1
)
if not exist "src\tray.py" (
    color 0C
    echo [ERROR] src\tray.py not found
    pause
    exit /b 1
)
echo [OK] All required files present
echo.

REM Success
color 0A
echo ======================================================================
echo ^! BytePulse Setup Complete!
echo ======================================================================
echo.
echo What was installed:
echo   * All Python dependencies
echo   * SQLite database initialized
echo   * data/ and logs/ directories
if %ADMIN%==1 (
    echo   * Task Scheduler auto-startup (BytePulse-Tray + BytePulse-Tracker)
) else (
    echo   * Task Scheduler auto-startup (SKIPPED - run as admin)
)
echo.
echo How to launch:
echo   Option 1: Double-click launch_bytepulse.bat
echo   Option 2: python src\tray.py + python src\tracker.py (separately)
echo   Option 3: Auto-starts on boot (if admin registered tasks)
echo.
echo What happens when you launch:
echo   1. System tray icon appears in taskbar
echo   2. WiFi tracking starts in background
echo   3. Right-click tray icon for menu:
echo      - Status: Shows tracker running
echo      - Open Dashboard: View usage stats
echo      - Stop Tracker: Stop background monitoring
echo      - Quit: Close everything
echo.
echo Data saved to:
echo   * %SCRIPT_DIR%data\usage_log.csv
echo   * %SCRIPT_DIR%data\usage_log.json
echo   * %SCRIPT_DIR%data\bytepulse.db
echo   * %SCRIPT_DIR%data\tracker.log
echo.
if %ADMIN%==0 (
    echo To enable auto-startup:
    echo   1. Right-click setup_bytepulse.bat
    echo   2. Select "Run as administrator"
    echo   3. Run again
    echo.
)
color 0F

REM Ask to launch
set /p LAUNCH="Launch BytePulse now? (y/n): "
if /i "%LAUNCH%"=="y" (
    echo.
    echo Starting BytePulse...
    echo.
    start "" launch_bytepulse.bat
) else (
    echo.
    echo Setup complete! Launch anytime with: launch_bytepulse.bat
    echo.
    pause
)
