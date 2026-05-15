import os
import sys
import time
import signal
import atexit
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tracker import track_usage

class Daemon:
    def __init__(self, pidfile):
        self.pidfile = pidfile

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            print(f"Fork failed: {e}", file=sys.stderr)
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            print(f"Second fork failed: {e}", file=sys.stderr)
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()

        with open("/dev/null", "r") as devnull:
            os.dup2(devnull.fileno(), sys.stdin.fileno())

        with open(self.pidfile, "w") as pf:
            pf.write(str(os.getpid()))

    def start(self):
        if os.path.exists(self.pidfile):
            try:
                with open(self.pidfile, "r") as pf:
                    pid = int(pf.read().strip())
                    os.kill(pid, 0)
                print("Daemon already running.")
                sys.exit(1)
            except (OSError, ValueError):
                os.remove(self.pidfile)

        self.daemonize()
        track_usage()

    def stop(self):
        if not os.path.exists(self.pidfile):
            print("Daemon not running.")
            return

        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                print("Daemon stopped.")
        except (OSError, ValueError) as e:
            print(f"Failed to stop daemon: {e}")

    def status(self):
        if not os.path.exists(self.pidfile):
            print("Daemon not running.")
            return

        try:
            with open(self.pidfile, "r") as pf:
                pid = int(pf.read().strip())
                os.kill(pid, 0)
                print(f"Daemon running (PID {pid})")
        except (OSError, ValueError):
            print("Daemon not running.")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pidfile = os.path.join(BASE_DIR, "bytepulse.pid")

    daemon = Daemon(pidfile)

    if len(sys.argv) < 2:
        print("Usage: python daemon.py {start|stop|status}")
        sys.exit(1)

    if sys.argv[1] == "start":
        daemon.start()
    elif sys.argv[1] == "stop":
        daemon.stop()
    elif sys.argv[1] == "status":
        daemon.status()
    else:
        print("Unknown command")
        sys.exit(1)