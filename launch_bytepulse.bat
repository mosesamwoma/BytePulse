@echo off
REM BytePulse Launcher
REM Starts both tray icon and tracker in background

cd /d "%~dp0"

echo Starting BytePulse...
echo.
echo Launching tray icon...
start "" pythonw.exe src\tray.py

echo Launching tracker...
start "" pythonw.exe src\tracker.py

echo.
echo BytePulse started. Look for the icon in your system tray (bottom-right corner).
echo.
echo Right-click the tray icon to:
echo   - View tracker status
echo   - Open the dashboard
echo   - Stop the tracker
echo   - Quit
echo.
pause
