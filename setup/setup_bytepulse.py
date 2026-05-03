#!/usr/bin/env python3
"""
BytePulse Complete Setup
One-click setup: dependencies, database, AND Task Scheduler registration (requires admin)
No README needed. Just run this once.
"""

import os
import sys
import subprocess
import time
import ctypes
from pathlib import Path
from typing import Optional

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def colored(text: str, color: str) -> str:
    return f"{color}{text}{Colors.ENDC}"

def print_banner():
    print(f"\n{colored('=' * 70, Colors.BOLD)}")
    print(colored("BytePulse Complete Setup", Colors.BOLD))
    print(colored("Installing dependencies, initializing database, and registering auto-startup", Colors.CYAN))
    print(f"{colored('=' * 70, Colors.BOLD)}\n")

def print_step(step: int, total: int, title: str):
    print(colored(f"[{step}/{total}]", Colors.BOLD) + f" {title}")

def print_success(msg: str):
    print(colored(f"  ✓ {msg}", Colors.GREEN))

def print_error(msg: str):
    print(colored(f"  ✗ {msg}", Colors.RED))

def print_info(msg: str):
    print(colored(f"  → {msg}", Colors.BLUE))

def print_warn(msg: str):
    print(colored(f"  ⚠ {msg}", Colors.YELLOW))

def get_project_root() -> Path:
    script_dir = Path(__file__).parent.absolute()
    setup_dir = script_dir
    
    # Look for BytePulse root (one level up from setup/)
    if setup_dir.name == "setup":
        potential_root = setup_dir.parent
        if (potential_root / "src").exists() and (potential_root / "app.py").exists():
            return potential_root
    
    # Check if script_dir is the root
    if (script_dir / "src").exists() and (script_dir / "app.py").exists():
        return script_dir
    
    # Check current working directory
    if Path.cwd().name == "BytePulse" or (Path.cwd() / "src").exists():
        return Path.cwd()
    
    print_error("BytePulse root directory not found!")
    print_info("Make sure you run this script from: BytePulse/setup/")
    print_info("Or from the BytePulse root folder")
    sys.exit(1)

def is_admin() -> bool:
    """Check if running as Administrator"""
    try:
        return ctypes.windll.shell.IsUserAnAdmin()
    except AttributeError:
        return False

def run_command(cmd: list, cwd: Optional[Path] = None) -> bool:
    try:
        subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except Exception:
        return False

def step_1_check_python() -> bool:
    print_step(1, 8, "Checking Python installation")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        version = result.stdout.strip() + result.stderr.strip()
        print_success(f"Found {version}")
        if sys.version_info < (3, 7):
            print_error("Python 3.7+ required")
            return False
        return True
    except Exception as e:
        print_error(f"Python check failed: {e}")
        return False

def step_2_install_dependencies(project_root: Path) -> bool:
    print_step(2, 8, "Installing dependencies")
    
    req_file = project_root / "requirements.txt"
    if not req_file.exists():
        print_error(f"requirements.txt not found")
        return False
    
    print_info("Upgrading pip...")
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"]):
        print_error("Failed to upgrade pip")
        return False
    
    print_info("Installing packages...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", str(req_file)], cwd=project_root):
        print_error("Failed to install packages")
        return False
    
    print_success("All dependencies installed")
    return True

def step_3_create_directories(project_root: Path) -> bool:
    print_step(3, 8, "Creating directories")
    
    dirs = [project_root / "data", project_root / "logs"]
    
    for d in dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
            print_info(f"Ensured {d.name}/ exists")
        except Exception as e:
            print_error(f"Failed to create {d.name}: {e}")
            return False
    
    print_success("Directories created")
    return True

def step_4_init_database(project_root: Path) -> bool:
    print_step(4, 8, "Initializing database")
    
    try:
        print_info("Creating database schema...")
        cmd = [
            sys.executable, "-c",
            "import sys; sys.path.insert(0, '.'); from database.database import init_db; init_db()"
        ]
        
        if not run_command(cmd, cwd=project_root):
            print_info("Database will auto-create on first run")
        else:
            print_success("Database initialized")
        return True
    except Exception as e:
        print_info(f"Database init skipped ({e}) - will auto-create on first run")
        return True

def step_5_check_admin() -> bool:
    print_step(5, 8, "Checking Administrator privileges")
    
    if is_admin():
        print_success("Running as Administrator")
        return True
    else:
        print_warn("NOT running as Administrator")
        print_info("Task Scheduler registration requires admin rights")
        return False

def step_6_register_tasks(project_root: Path, admin: bool) -> bool:
    print_step(6, 8, "Registering Task Scheduler tasks")
    
    if not admin:
        print_warn("Skipped - requires Administrator")
        print_info("To enable auto-startup:")
        print_info("  1. Right-click this script")
        print_info("  2. Select 'Run as administrator'")
        print_info("  3. Run again")
        return True
    
    try:
        pythonw = Path(sys.executable).parent / "pythonw.exe"
        
        if not pythonw.exists():
            print_error(f"pythonw.exe not found at {pythonw}")
            return False
        
        tray_py = project_root / "src" / "tray.py"
        tracker_py = project_root / "src" / "tracker.py"
        
        # Register Tray task
        print_info("Registering BytePulse-Tray task...")
        tray_cmd = [
            "powershell", "-Command",
            f"""
$pythonw = '{pythonw}'
$base = '{project_root}'
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "BytePulse-Tray" `
    -Action (New-ScheduledTaskAction -Execute $pythonw -Argument "`"$base\\src\\tray.py`"" -WorkingDirectory $base) `
    -Trigger $trigger -Settings $settings -RunLevel Highest -Force | Out-Null
Write-Host "OK"
"""
        ]
        
        result = subprocess.run(tray_cmd, capture_output=True, text=True)
        if "OK" in result.stdout:
            print_success("BytePulse-Tray registered")
        else:
            print_error(f"BytePulse-Tray registration failed: {result.stderr}")
            return False
        
        # Register Tracker task
        print_info("Registering BytePulse-Tracker task (10s delay)...")
        tracker_cmd = [
            "powershell", "-Command",
            f"""
$pythonw = '{pythonw}'
$base = '{project_root}'
$trigger = New-ScheduledTaskTrigger -AtLogOn
$trigger.Delay = "PT10S"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "BytePulse-Tracker" `
    -Action (New-ScheduledTaskAction -Execute $pythonw -Argument "`"$base\\src\\tracker.py`"" -WorkingDirectory $base) `
    -Trigger $trigger -Settings $settings -RunLevel Highest -Force | Out-Null
Write-Host "OK"
"""
        ]
        
        result = subprocess.run(tracker_cmd, capture_output=True, text=True)
        if "OK" in result.stdout:
            print_success("BytePulse-Tracker registered (10s delay)")
        else:
            print_error(f"BytePulse-Tracker registration failed: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        print_error(f"Task registration failed: {e}")
        return False

def step_7_create_launcher(project_root: Path) -> bool:
    print_step(7, 8, "Creating launcher shortcut")
    
    try:
        launcher = project_root / "launch_bytepulse.bat"
        content = f"""@echo off
REM BytePulse Launcher
cd /d "{project_root}"
start "" pythonw.exe src\\tray.py
start "" pythonw.exe src\\tracker.py
exit
"""
        
        with open(launcher, "w") as f:
            f.write(content)
        
        print_success(f"Created {launcher.name}")
        return True
    except Exception as e:
        print_info(f"Could not create launcher: {e}")
        return True

def step_8_final_checks(project_root: Path) -> bool:
    print_step(8, 8, "Final verification")
    
    required = [
        project_root / "app.py",
        project_root / "src" / "tracker.py",
        project_root / "src" / "tray.py",
        project_root / "database" / "database.py",
    ]
    
    all_good = True
    for f in required:
        if f.exists():
            print_info(f"Found {f.relative_to(project_root)}")
        else:
            print_error(f"Missing {f.relative_to(project_root)}")
            all_good = False
    
    if all_good:
        print_success("All files present")
    return all_good

def print_summary(project_root: Path, admin: bool):
    print(f"\n{colored('=' * 70, Colors.BOLD)}")
    print(colored("✓ BytePulse Setup Complete!", Colors.GREEN + Colors.BOLD))
    print(f"{colored('=' * 70, Colors.BOLD)}\n")
    
    print(colored("What was installed:", Colors.BOLD))
    print(f"  ✓ All Python dependencies (from requirements.txt)")
    print(f"  ✓ SQLite database initialized")
    print(f"  ✓ data/ and logs/ directories")
    if admin:
        print(f"  ✓ Task Scheduler auto-startup (BytePulse-Tray + BytePulse-Tracker)")
    else:
        print(f"  ⚠ Task Scheduler auto-startup (SKIPPED - run as admin to enable)")
    
    print(f"\n{colored('How to launch BytePulse:', Colors.BOLD)}")
    print(f"  Option 1: Double-click launch_bytepulse.bat")
    print(f"  Option 2: python src/tray.py (tray icon)")
    print(f"            python src/tracker.py (background tracking)")
    print(f"  Option 3: Auto-starts on boot (if admin registered tasks)")
    
    print(f"\n{colored('What happens when you launch:', Colors.BOLD)}")
    print(f"  1. src/tray.py starts → system tray icon appears")
    print(f"  2. src/tracker.py starts → WiFi tracking begins")
    print(f"  3. Right-click tray icon for:")
    print(f"     • Status (shows tracker running)")
    print(f"     • Open Dashboard (launches Streamlit)")
    print(f"     • Stop Tracker (stops background monitoring)")
    print(f"     • Quit (closes everything)")
    
    print(f"\n{colored('Data locations:', Colors.BOLD)}")
    print(f"  CSV:  {project_root / 'data' / 'usage_log.csv'}")
    print(f"  JSON: {project_root / 'data' / 'usage_log.json'}")
    print(f"  DB:   {project_root / 'data' / 'bytepulse.db'}")
    print(f"  Log:  {project_root / 'data' / 'tracker.log'}")
    
    if not admin:
        print(f"\n{colored('To enable auto-startup:', Colors.BOLD)}")
        print(f"  1. Right-click this script: setup_bytepulse.py")
        print(f"  2. Select 'Run with PowerShell as Administrator'")
        print(f"  3. Run again")
    
    print(f"\n{colored('=' * 70, Colors.ENDC)}\n")

def elevate_to_admin():
    """Re-run this script as Administrator"""
    script_path = Path(__file__).absolute()
    
    print(colored("\n" + "=" * 70, Colors.BOLD))
    print(colored("Administrator Privileges Required", Colors.YELLOW + Colors.BOLD))
    print(colored("=" * 70, Colors.ENDC))
    print()
    print("BytePulse setup needs admin rights to register auto-startup tasks.")
    print()
    print("A new PowerShell window will open as Administrator.")
    print("Please click 'Yes' on the UAC security prompt.")
    print()
    input(colored("Press Enter to elevate and continue... ", Colors.CYAN))
    
    # Use powershell to elevate
    ps_command = f'python "{script_path}"'
    
    try:
        subprocess.run(
            ["powershell", "-Command", f"Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd \"{Path(__file__).parent.parent}\"; {ps_command}' -Verb RunAs"],
            check=False
        )
    except Exception as e:
        print_error(f"Failed to elevate: {e}")
    
    sys.exit(0)

def main():
    # Check for admin rights - elevate if needed
    if not is_admin():
        elevate_to_admin()
    
    print_banner()
    
    project_root = get_project_root()
    print_info(f"Project root: {project_root}\n")
    
    admin = is_admin()
    
    steps = [
        ("Python check", step_1_check_python),
        ("Dependencies", lambda: step_2_install_dependencies(project_root)),
        ("Directories", lambda: step_3_create_directories(project_root)),
        ("Database", lambda: step_4_init_database(project_root)),
        ("Admin check", step_5_check_admin),
        ("Task Scheduler", lambda: step_6_register_tasks(project_root, admin)),
        ("Launcher", lambda: step_7_create_launcher(project_root)),
        ("Final checks", lambda: step_8_final_checks(project_root)),
    ]
    
    failed = False
    for title, func in steps:
        try:
            if not func():
                print_error(f"{title} failed")
                if title in ["Python check", "Dependencies", "Final checks"]:
                    print_error("Setup cannot continue")
                    sys.exit(1)
                failed = True
        except Exception as e:
            print_error(f"{title} error: {e}")
            if title in ["Python check", "Dependencies"]:
                sys.exit(1)
            failed = True
    
    print_summary(project_root, admin)
    
    if not failed:
        print(colored("Launch BytePulse now? (y/n): ", Colors.CYAN), end="")
        try:
            if input().strip().lower() == 'y':
                print_info("Starting launcher...\n")
                time.sleep(1)
                launcher = project_root / "launch_bytepulse.bat"
                os.startfile(launcher)
        except KeyboardInterrupt:
            print("\n" + colored("You can launch later with: launch_bytepulse.bat", Colors.CYAN))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + colored("Setup cancelled", Colors.YELLOW))
        sys.exit(0)
    except Exception as e:
        print("\n" + colored(f"Fatal error: {e}", Colors.RED))
        sys.exit(1)
