@echo off
REM BytePulse Complete Setup
REM One-click: virtual environment, dependencies, database, and Task Scheduler registration
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
    echo A new admin window will open.
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
echo Installing venv, dependencies, database, and auto-startup registration
echo ======================================================================
echo.

echo [OK] Running as Administrator
echo.
set "ADMIN=1"
set "VENV_DIR=venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_PYTHONW=%VENV_DIR%\Scripts\pythonw.exe"

REM [1/9] Check Python
echo [1/9] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python not found in PATH
    echo Download from: https://www.python.org/downloads/release/python-3110/
    echo Check "Add Python to PATH" during installation
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set "PYTHON_VER=%%i"
echo [OK] %PYTHON_VER%
echo.

REM [2/9] Create virtual environment
echo [2/9] Creating virtual environment...
if exist "%VENV_DIR%" (
    echo [INFO] Virtual environment already exists
) else (
    python -m venv "%VENV_DIR%" >nul 2>&1
    if errorlevel 1 (
        color 0C
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo.

REM [3/9] Activate virtual environment
echo [3/9] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat" >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM [4/9] Install dependencies
echo [4/9] Installing dependencies...
if not exist "requirements.txt" (
    color 0C
    echo [ERROR] requirements.txt not found in windows/
    pause
    exit /b 1
)
echo       Upgrading pip...
"%VENV_PYTHON%" -m pip install --upgrade pip >nul 2>&1
echo       Installing packages...
"%VENV_PYTHON%" -m pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [WARNING] Some packages failed to install
    color 0F
) else (
    echo [OK] All dependencies installed
)
echo.

REM [5/9] Create directories
echo [5/9] Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "data\.gitkeep" (
    type nul > "data\.gitkeep"
)
echo [OK] Directories created
echo.

REM [6/9] Initialize database
echo [6/9] Initializing database...
"%VENV_PYTHON%" -c "import sys; sys.path.insert(0, '..'); from shared.database.database import init_db; init_db()" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Database will auto-create on first run
) else (
    echo [OK] Database initialized
)
echo.

REM [7/9] Verify required files
echo [7/9] Verifying required files...
set "FILES_OK=1"
if not exist "main.py" (
    echo [ERROR] main.py not found
    set "FILES_OK=0"
)
if not exist "app.py" (
    echo [ERROR] app.py not found
    set "FILES_OK=0"
)
if not exist "src\tracker.py" (
    echo [ERROR] src\tracker.py not found
    set "FILES_OK=0"
)
if not exist "src\tray.py" (
    echo [ERROR] src\tray.py not found
    set "FILES_OK=0"
)
if %FILES_OK%==0 (
    color 0C
    pause
    exit /b 1
)
echo [OK] All required files present
echo.

REM [8/9] Register Task Scheduler (admin only)
echo [8/9] Registering Task Scheduler tasks...
set "PROJECT_ROOT=%CD%"
set "PYTHONW=!PROJECT_ROOT!\%VENV_PYTHONW%"

echo       Registering BytePulse-Tray...
powershell -NoProfile -Command ^
    "$pythonw = '!PYTHONW!'; " ^
    "$base = '!PROJECT_ROOT!'; " ^
    "$trigger = New-ScheduledTaskTrigger -AtLogOn; " ^
    "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew; " ^
    "$action = New-ScheduledTaskAction -Execute $pythonw -Argument \"`\"$base\src\tray.py`\"\" -WorkingDirectory $base; " ^
    "Register-ScheduledTask -TaskName 'BytePulse-Tray' -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force | Out-Null; " ^
    "Write-Host 'OK'" >nul 2>&1

if !ERRORLEVEL!==0 (
    echo [OK] BytePulse-Tray registered
) else (
    color 0E
    echo [WARNING] BytePulse-Tray registration failed
    color 0F
)

echo       Registering BytePulse-Tracker (10s delay)...
powershell -NoProfile -Command ^
    "$pythonw = '!PYTHONW!'; " ^
    "$base = '!PROJECT_ROOT!'; " ^
    "$trigger = New-ScheduledTaskTrigger -AtLogOn; " ^
    "$trigger.Delay = 'PT10S'; " ^
    "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew; " ^
    "$action = New-ScheduledTaskAction -Execute $pythonw -Argument \"`\"$base\src\tracker.py`\"\" -WorkingDirectory $base; " ^
    "Register-ScheduledTask -TaskName 'BytePulse-Tracker' -Action $action -Trigger $triggerTracker -Settings $settings -RunLevel Highest -Force | Out-Null; " ^
    "Write-Host 'OK'" >nul 2>&1

if !ERRORLEVEL!==0 (
    echo [OK] BytePulse-Tracker registered (10s delay)
) else (
    color 0E
    echo [WARNING] BytePulse-Tracker registration failed
    color 0F
)
echo.

REM [9/9] Create launcher
echo [9/9] Creating launcher shortcut...
set "LAUNCHER_PATH=%CD%\launch_bytepulse.bat"
(
    echo @echo off
    echo REM BytePulse Launcher
    echo cd /d "%%~dp0"
    echo call venv\Scripts\activate.bat
    echo python main.py
    echo pause
) > "%LAUNCHER_PATH%"
echo [OK] Created: launch_bytepulse.bat
echo.

REM Success
color 0A
echo ======================================================================
echo ! BytePulse Setup Complete!
echo ======================================================================
echo.
echo What was installed:
echo   * Python virtual environment (venv/)
echo   * All Python dependencies
echo   * SQLite database initialized
echo   * data/ and logs/ directories
echo   * Task Scheduler auto-startup (BytePulse-Tray + BytePulse-Tracker)
echo.
echo How to launch:
echo   Option 1: Double-click launch_bytepulse.bat
echo   Option 2: Activate venv, then: python main.py
echo   Option 3: Auto-starts on boot (Task Scheduler registered)
echo.
echo System tray icon menu:
echo   - Status: Shows if tracker is running
echo   - Open Dashboard: View usage stats at http://localhost:8501
echo   - Stop Tracker: Stop background monitoring
echo   - Quit: Close everything
echo.
echo Data locations:
echo   * %CD%\data\bytepulse.db
echo   * %CD%\data\tracker.log
echo.
color 0F

REM Ask to launch
set /p LAUNCH="Launch BytePulse now? (y/n): "
if /i "%LAUNCH%"=="y" (
    echo.
    echo Starting BytePulse...
    echo.
    start "" "%LAUNCHER_PATH%"
) else (
    echo.
    echo Setup complete! Launch anytime with: launch_bytepulse.bat
    echo.
    pause
)
