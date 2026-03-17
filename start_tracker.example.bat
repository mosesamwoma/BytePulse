@echo off
cd /d "C:\path\to\BytePulse"
if not exist data mkdir data
python src\tracker.py
if %errorlevel% neq 0 (
    echo Tracker exited with error code %errorlevel%
    pause
)