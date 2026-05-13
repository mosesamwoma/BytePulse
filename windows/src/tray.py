import pystray
import subprocess
import os
import sys
import psutil
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK_PATH = os.path.join(BASE_DIR, "data", "tracker.lock")
TRAY_LOCK = os.path.join(BASE_DIR, "data", "tray.lock")


def acquire_tray_lock():
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
            img = Image.open(path).convert("RGBA")
            img = img.resize((64, 64), Image.LANCZOS)
            return img

    # fallback to default if neither found
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
    subprocess.Popen(
        ["streamlit", "run", os.path.join(BASE_DIR, "app.py")],
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def stop_tracker(icon, item):
    try:
        if os.path.exists(LOCK_PATH):
            with open(LOCK_PATH, "r") as f:
                pid = int(f.read().strip())
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=5)
    except (psutil.NoSuchProcess, psutil.TimeoutExpired, Exception):
        pass


def quit_all(icon, item):
    stop_tracker(icon, item)
    release_tray_lock()
    icon.stop()


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
        title="BytePulse",
        menu=menu
    )

    icon.run()
    release_tray_lock()


if __name__ == "__main__":
    run_tray()