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

    python_bin = "python3"

    try:
        print("[1/2] Starting background tracker...")
        subprocess.Popen(
            [python_bin, str(project_root / "src" / "tracker.py")],
            cwd=project_root
        )
        time.sleep(2)

        print("[2/2] Starting alerts service...")
        subprocess.Popen(
            [python_bin, str(project_root / "src" / "alerts.py")],
            cwd=project_root
        )
        time.sleep(1)

        print("\n✓ BytePulse started")
        print("  Logs: data/tracker.log")
        print("  Data: data/bytepulse.db")

    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    start_all()