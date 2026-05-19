import pystray
import subprocess
import os
import sys
import psutil
from PIL import Image, ImageDraw
from pathlib import Path
import time

# Point to BytePulse root/data (not linux/data)
BASE_DIR = Path(__file__).parent.parent.parent  # BytePulse/
LOCK_PATH = os.path.join(BASE_DIR, "data", "tracker.lock")
TRAY_LOCK = os.path.join(BASE_DIR, "data", "tray.lock")


def acquire_tray_lock():
    os.makedirs(os.path.dirname(TRAY_LOCK), exist_ok=True)
    
    if os.path.exists(TRAY_LOCK):
        try:
            with open(TRAY_LOCK, "r") as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                try:
                    proc = psutil.Process(pid)
                    if "python" in proc.name().lower() and proc.status() != psutil.STATUS_ZOMBIE:
                        sys.exit(0)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
        try:
            os.remove(TRAY_LOCK)
        except Exception:
            pass

    with open(TRAY_LOCK, "w") as f:
        f.write(str(os.getpid()))


def release_tray_lock():
    try:
        if os.path.exists(TRAY_LOCK):
            with open(TRAY_LOCK, "r") as f:
                pid = int(f.read().strip())
            if pid == os.getpid():
                os.remove(TRAY_LOCK)
    except Exception:
        pass


def is_tracker_running():
    if not os.path.exists(LOCK_PATH):
        return False
    try:
        with open(LOCK_PATH, "r") as f:
            pid = int(f.read().strip())
        return psutil.pid_exists(pid)
    except Exception:
        return False


def create_icon():
    primary = os.path.join(BASE_DIR, "assets", "8.png")
    backup = os.path.join(BASE_DIR, "assets", "7.png")

    for path in [primary, backup]:
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                img = img.resize((64, 64), Image.LANCZOS)
                return img
            except Exception:
                pass

    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse([4, 4, size - 4, size - 4], fill=(0, 120, 215))
    draw.rectangle([28, 16, 36, 36], fill="white")
    draw.rectangle([28, 40, 36, 48], fill="white")
    return image


def get_status():
    if is_tracker_running():
        try:
            with open(LOCK_PATH, "r") as f:
                pid = f.read().strip()
            return f"Running (PID {pid})"
        except Exception:
            return "Running"
    return "Stopped"


def open_dashboard(icon, item):
    try:
        app_path = os.path.join(BASE_DIR, "linux", "app.py")
        log_path = os.path.join(BASE_DIR, "logs", "dashboard.log")
        
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Use venv Python explicitly
        venv_python = os.path.join(BASE_DIR, "linux", "venv", "bin", "python3")
        
        # Set up environment with PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BASE_DIR)
        
        # Run streamlit with error logging
        with open(log_path, "w") as log_file:
            subprocess.Popen(
                [venv_python, "-m", "streamlit", "run", app_path],
                cwd=str(BASE_DIR),
                env=env,
                stdout=log_file,
                stderr=log_file
            )
        print(f"[BytePulse] Opening dashboard: {app_path}")
    except Exception as e:
        print(f"[BytePulse] Error opening dashboard: {e}")
        import traceback
        traceback.print_exc()


def stop_tracker(icon, item):
    try:
        if os.path.exists(LOCK_PATH):
            with open(LOCK_PATH, "r") as f:
                pid = int(f.read().strip())
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=5)
            print("[BytePulse] Tracker stopped")
    except (psutil.NoSuchProcess, psutil.TimeoutExpired, Exception) as e:
        print(f"[BytePulse] Error stopping tracker: {e}")


def quit_all(icon, item):
    print("[BytePulse] Quitting tray")
    stop_tracker(icon, item)
    release_tray_lock()
    icon.stop()
    sys.exit(0)


def run_tray():
    acquire_tray_lock()

    menu = pystray.Menu(
        pystray.MenuItem(lambda _: f"Status: {get_status()}", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Open Dashboard", open_dashboard),
        pystray.MenuItem("Stop Tracker", stop_tracker),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_all),
    )

    icon = pystray.Icon(
        name="BytePulse",
        icon=create_icon(),
        title="BytePulse WiFi Tracker",
        menu=menu
    )

    print("[BytePulse] Tray icon started")
    icon.run()
    release_tray_lock()


if __name__ == "__main__":
    run_tray()