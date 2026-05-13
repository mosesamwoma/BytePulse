import subprocess
import sys
import time
from pathlib import Path

def start_all():
    project_root = Path(__file__).parent
    
    data_dir = project_root / "data"
    logs_dir = project_root / "logs"
    gitkeep = data_dir / ".gitkeep"
    
    data_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    if not gitkeep.exists():
        gitkeep.touch()
    
    print("Starting BytePulse...\n")
    
    if sys.platform == "win32":
        venv_python = project_root / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = project_root / "venv" / "bin" / "python"
    
    if not venv_python.exists():
        print("[ERROR] Virtual environment not found!")
        print("Run: python setup.py")
        sys.exit(1)
    
    try:
        print("[1/3] Starting tray app...")
        subprocess.Popen(
            [str(venv_python), str(project_root / "src" / "tray.py")],
            cwd=project_root
        )
        time.sleep(1)
        
        print("[2/3] Starting tracker (10s delay)...")
        time.sleep(10)
        subprocess.Popen(
            [str(venv_python), str(project_root / "src" / "tracker.py")],
            cwd=project_root
        )
        time.sleep(1)
        
        print("[3/3] Starting dashboard...")
        subprocess.Popen(
            [str(venv_python), str(project_root / "app.py")],
            cwd=project_root
        )
        
        print("\n✓ BytePulse started")
        print("  Tray: System tray icon (bottom-right)")
        print("  Dashboard: http://localhost:8501")
        print("  Logs: data/tracker.log")
        
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    start_all()
