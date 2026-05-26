import subprocess
import os
import sys
import psutil
from pathlib import Path
import time
import socket
from contextlib import closing
import threading

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QAction, QBrush, QColor, QDesktopServices, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

BASE_DIR = Path(__file__).parent.parent.parent
LOCK_PATH = os.path.join(BASE_DIR, "data", "tracker.lock")
TRAY_LOCK = os.path.join(BASE_DIR, "data", "tray.lock")
DASHBOARD_PORT = 8501
DASHBOARD_URL = f"http://127.0.0.1:{DASHBOARD_PORT}"
DASHBOARD_LOG = os.path.join(BASE_DIR, "logs", "dashboard.log")
APP_PATH = os.path.join(BASE_DIR, "linux", "app.py")
VENV_PYTHON = os.path.join(BASE_DIR, "linux", "venv", "bin", "python3")


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
            icon = QIcon(path)
            if not icon.isNull():
                return icon

    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor("#1e88e5")))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(4, 4, 56, 56)
    painter.end()
    return QIcon(pixmap)


def dashboard_is_running():
    try:
        with closing(socket.create_connection(("127.0.0.1", DASHBOARD_PORT), timeout=0.5)):
            return True
    except OSError:
        return False


def wait_for_dashboard(timeout_seconds=15):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if dashboard_is_running():
            return True
        time.sleep(0.5)
    return False


def launch_dashboard_process():
    if dashboard_is_running():
        return True

    os.makedirs(os.path.dirname(DASHBOARD_LOG), exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)

    python_bin = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
    with open(DASHBOARD_LOG, "a", encoding="utf-8") as log_file:
        subprocess.Popen(
            [
                python_bin,
                "-m",
                "streamlit",
                "run",
                APP_PATH,
                "--server.port",
                str(DASHBOARD_PORT),
                "--server.address",
                "127.0.0.1",
                "--server.headless",
                "true",
                "--browser.gatherUsageStats",
                "false",
                "--logger.level",
                "error",
            ],
            cwd=str(BASE_DIR),
            env=env,
            stdout=log_file,
            stderr=log_file,
            start_new_session=True,
        )

    return wait_for_dashboard()


def open_dashboard_browser():
    return QDesktopServices.openUrl(QUrl(DASHBOARD_URL))


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
    def worker():
        print("[BytePulse] Opening dashboard...")
        try:
            if not dashboard_is_running():
                if launch_dashboard_process():
                    print(f"[BytePulse] Dashboard ready at {DASHBOARD_URL}")
                else:
                    print(f"[BytePulse] Dashboard did not respond within timeout; check {DASHBOARD_LOG}")

            print("[BytePulse] Opening browser...")
            if not open_dashboard_browser():
                print(f"[BytePulse] Unable to open browser automatically. Visit {DASHBOARD_URL}")
        except Exception as e:
            print(f"[BytePulse] Error: {e}")
            import traceback
            traceback.print_exc()

    threading.Thread(target=worker, daemon=True).start()


def stop_tracker(icon, item):
    print("[BytePulse] Stopping tracker...")
    try:
        if os.path.exists(LOCK_PATH):
            with open(LOCK_PATH, "r") as f:
                pid = int(f.read().strip())
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=5)
            print("[BytePulse] Tracker stopped")
    except (psutil.NoSuchProcess, psutil.TimeoutExpired, Exception) as e:
        print(f"[BytePulse] Error: {e}")


def quit_all(icon, item):
    print("[BytePulse] Quitting tray")
    release_tray_lock()
    icon.stop()
    QApplication.instance().quit()


def run_tray():
    acquire_tray_lock()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("BytePulse")

    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("[BytePulse] System tray is not available in this session")
        release_tray_lock()
        sys.exit(1)

    tray = QSystemTrayIcon(create_icon())
    tray.setToolTip("BytePulse WiFi Tracker")

    menu = QMenu()
    status_action = QAction(f"Status: {get_status()}")
    status_action.setEnabled(False)
    menu.addAction(status_action)
    menu.addSeparator()

    open_action = QAction("Open Dashboard")
    open_action.triggered.connect(lambda: open_dashboard(tray, None))
    menu.addAction(open_action)

    stop_action = QAction("Stop Tracker")
    stop_action.triggered.connect(lambda: stop_tracker(tray, None))
    menu.addAction(stop_action)

    menu.addSeparator()

    quit_action = QAction("Quit")
    quit_action.triggered.connect(lambda: quit_all(tray, None))
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.activated.connect(lambda reason: open_dashboard(tray, None) if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick) else None)
    tray.show()

    print("[BytePulse] Tray icon started")
    exit_code = app.exec()
    release_tray_lock()
    sys.exit(exit_code)


if __name__ == "__main__":
    run_tray()