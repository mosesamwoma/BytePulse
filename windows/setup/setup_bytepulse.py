import subprocess
import sys
import os
from pathlib import Path

def check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("[ERROR] Python 3.11 required")
        sys.exit(1)
    if version.major == 3 and version.minor > 11:
        print("[WARNING] Python 3.12+ detected. psutil may have compatibility issues.")
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")

def create_venv():
    print("[2/8] Creating virtual environment...")
    venv_dir = Path("venv")
    
    if venv_dir.exists():
        print("[INFO] Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], 
                      check=True, capture_output=True)
        print("[OK] Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to create virtual environment")
        return False

def get_venv_python():
    venv_python = Path("venv") / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")
    return str(venv_python)

def install_dependencies():
    print("[3/8] Installing dependencies...")
    req_file = Path("requirements.txt")
    
    if not req_file.exists():
        print("[ERROR] requirements.txt not found")
        sys.exit(1)
    
    venv_python = get_venv_python()
    
    try:
        print("       Upgrading pip...")
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"],
                      capture_output=True, check=True)
        
        print("       Installing packages...")
        subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"],
                      capture_output=True, check=True)
        
        print("[OK] All dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] Some packages failed to install: {e}")
        return False

def create_directories():
    print("[4/8] Creating directories...")
    data_dir = Path("data")
    logs_dir = Path("logs")
    gitkeep = data_dir / ".gitkeep"
    
    data_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    if not gitkeep.exists():
        gitkeep.touch()
    
    print("[OK] Directories created")

def init_database():
    print("[5/8] Initializing database...")
    venv_python = get_venv_python()
    
    try:
        subprocess.run([venv_python, "-c", 
                       "import sys; sys.path.insert(0, '..'); from shared.database.database import init_db; init_db()"],
                      capture_output=True, check=True, cwd=Path.cwd())
        print("[OK] Database initialized")
        return True
    except subprocess.CalledProcessError:
        print("[INFO] Database will auto-create on first run")
        return True

def verify_files():
    print("[6/8] Final verification...")
    required = ["main.py", "app.py", "src/tracker.py", "src/tray.py"]
    
    for file in required:
        if not Path(file).exists():
            print(f"[ERROR] {file} not found")
            sys.exit(1)
    
    print("[OK] All required files present")

def create_launcher():
    print("[7/8] Creating launcher shortcut...")
    launcher_path = Path("launch_bytepulse.bat")
    
    launcher_content = """@echo off
REM BytePulse Launcher
REM Activates venv, handles process cleanup, starts tray + tracker with staggered startup

cd /d "%~dp0"

if not exist venv (
    color 0C
    echo [ERROR] Virtual environment not found
    echo Run setup.py first to create venv and install dependencies
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
    for /f "tokens=1" %%%%i in (data\tracker.lock) do (
        taskkill.exe /F /PID %%%%i >nul 2>&1
    )
    del /f data\tracker.lock >nul 2>&1
)

if exist data\tray.lock (
    for /f "tokens=1" %%%%i in (data\tray.lock) do (
        taskkill.exe /F /PID %%%%i >nul 2>&1
    )
    del /f data\tray.lock >nul 2>&1
)

timeout.exe /t 2 /nobreak >nul 2>&1

start "" "%PYTHONW%" src\tray.py
timeout.exe /t 5 /nobreak >nul 2>&1
start "" "%PYTHONW%" src\tracker.py

echo %date% %time% BytePulse started >> data\startup.log
"""
    
    try:
        launcher_path.write_text(launcher_content)
        print("[OK] Created: launch_bytepulse.bat")
        return True
    except Exception as e:
        print(f"[WARNING] Failed to create launcher: {e}")
        return False

def print_summary():
    print()
    print("=" * 70)
    print("! BytePulse Setup Complete!")
    print("=" * 70)
    print()
    print("What was installed:")
    print("  * Python virtual environment (venv/)")
    print("  * All Python dependencies")
    print("  * SQLite database initialized")
    print("  * data/ and logs/ directories")
    print("  * launch_bytepulse.bat launcher")
    print()
    print("How to launch:")
    print("  Option 1: Double-click launch_bytepulse.bat")
    print("  Option 2: Activate venv, then: python main.py")
    print()
    print("System tray icon menu:")
    print("  - Status: Shows if tracker is running")
    print("  - Open Dashboard: View usage stats at http://localhost:8501")
    print("  - Stop Tracker: Stop background monitoring")
    print("  - Quit: Close everything")
    print()
    print("Data locations:")
    print(f"  * {Path.cwd() / 'data' / 'bytepulse.db'}")
    print(f"  * {Path.cwd() / 'data' / 'tracker.log'}")
    print()
    print("For Task Scheduler auto-startup (Windows admin only):")
    print("  Run: setup_bytepulse.bat (as Administrator)")
    print()

def setup():
    print()
    print("=" * 70)
    print("BytePulse Setup")
    print("=" * 70)
    print()
    
    print("[1/8] Checking Python installation...")
    check_python()
    print()
    
    if not create_venv():
        sys.exit(1)
    print()
    
    if not install_dependencies():
        print("[WARNING] Setup continuing despite dependency warnings")
    print()
    
    create_directories()
    print()
    
    init_database()
    print()
    
    verify_files()
    print()
    
    create_launcher()
    print()
    
    print_summary()

if __name__ == "__main__":
    setup()