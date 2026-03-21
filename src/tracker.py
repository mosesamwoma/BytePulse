import psutil
import time
import pandas as pd
from datetime import datetime
import os
import sys
import logging
import signal
import atexit
import socket
import json
import tempfile
import shutil
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FILE_PATH = os.path.join(DATA_DIR, "usage_log.csv")
JSON_PATH = os.path.join(DATA_DIR, "usage_log.json")
LOG_PATH  = os.path.join(DATA_DIR, "tracker.log")
LOCK_PATH = os.path.join(DATA_DIR, "tracker.lock")

os.makedirs(DATA_DIR, exist_ok=True)

POLL_INTERVAL      = 5
AUTO_SAVE_INTERVAL = 1800

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    logging.info(msg)

def acquire_lock():
    if os.path.exists(LOCK_PATH):
        try:
            with open(LOCK_PATH, "r") as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                log(f"Tracker already running (PID {pid}). Exiting.")
                sys.exit(0)
            else:
                log("Stale lock file found — removing.")
                os.remove(LOCK_PATH)
        except Exception:
            try:
                os.remove(LOCK_PATH)
            except Exception:
                pass
    with open(LOCK_PATH, "w") as f:
        f.write(str(os.getpid()))

def release_lock():
    try:
        if os.path.exists(LOCK_PATH):
            os.remove(LOCK_PATH)
    except Exception:
        pass

def atomic_json_append(path, record: dict):
    records = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                records = json.load(f)
            if not isinstance(records, list):
                records = []
        except (json.JSONDecodeError, OSError):
            backup = path + ".corrupted"
            try:
                shutil.copy2(path, backup)
                log(f"Corrupted JSON backed up to {backup}")
            except Exception:
                pass
            records = []

    records.append(record)

    dir_name = os.path.dirname(path)
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        shutil.move(tmp_path, path)
        return True
    except Exception as e:
        log(f"JSON atomic write failed: {e}")
        try:
            if tmp_path:
                os.remove(tmp_path)
        except Exception:
            pass
        return False

def merge_pending_csv():
    pending = FILE_PATH + ".pending"
    if not os.path.exists(pending):
        return
    try:
        df = pd.read_csv(pending)
        df.to_csv(FILE_PATH, mode="a", header=False, index=False)
        os.remove(pending)
        log(f"Merged {len(df)} pending rows into main CSV.")
    except Exception as e:
        log(f"Pending CSV merge failed: {e}")

def has_ip_address(interface):
    try:
        addrs = psutil.net_if_addrs()
        if interface not in addrs:
            return False
        for addr in addrs[interface]:
            if addr.family == socket.AF_INET and addr.address:
                return True
        return False
    except Exception:
        return False

def get_active_interface():
    try:
        stats = psutil.net_if_stats()
        for name, stat in stats.items():
            if stat.isup and "wi-fi" in name.lower():
                if has_ip_address(name):
                    return name
        return None
    except Exception as e:
        log(f"Interface check failed: {e}")
        return None

def get_interface_counters(interface):
    try:
        counters = psutil.net_io_counters(pernic=True)
        return counters.get(interface, None)
    except Exception as e:
        log(f"Counter read failed: {e}")
        return None

def initialize_csv():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(FILE_PATH):
            df = pd.DataFrame(columns=[
                "start_time",
                "end_time",
                "duration_minutes",
                "bytes_sent",
                "bytes_received",
                "total_bytes",
                "usage_MB"
            ])
            df.to_csv(FILE_PATH, index=False)
            log("CSV initialized.")
        else:
            try:
                df = pd.read_csv(FILE_PATH, nrows=1)
                expected = ["start_time", "end_time", "duration_minutes", "bytes_sent", "bytes_received", "total_bytes", "usage_MB"]
                if not all(c in df.columns for c in expected):
                    raise ValueError("Missing columns")
            except Exception:
                backup = FILE_PATH + ".corrupted"
                shutil.copy2(FILE_PATH, backup)
                log(f"Corrupted CSV backed up to {backup} — recreating.")
                pd.DataFrame(columns=[
                    "start_time", "end_time", "duration_minutes",
                    "bytes_sent", "bytes_received", "total_bytes", "usage_MB"
                ]).to_csv(FILE_PATH, index=False)
    except Exception as e:
        log(f"CSV init failed: {e}")
        sys.exit(1)

def initialize_json():
    try:
        if not os.path.exists(JSON_PATH):
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)
            log("JSON initialized.")
        else:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("JSON root is not a list")
    except Exception:
        backup = JSON_PATH + ".corrupted"
        try:
            shutil.copy2(JSON_PATH, backup)
            log(f"Corrupted JSON backed up to {backup} — recreating.")
        except Exception:
            pass
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

def save_session(start_data, end_data, start_time, end_time, retries=3):
    if start_data is None or end_data is None:
        log("Save skipped: missing data.")
        return False
    if start_time is None or end_time is None:
        log("Save skipped: missing timestamps.")
        return False

    bytes_sent = end_data.bytes_sent - start_data.bytes_sent
    bytes_recv = end_data.bytes_recv - start_data.bytes_recv

    if bytes_sent < 0 or bytes_recv < 0:
        log("Counter rollover detected, adjusting.")
        bytes_sent = max(0, bytes_sent)
        bytes_recv = max(0, bytes_recv)

    total_bytes = bytes_sent + bytes_recv
    mb_used     = total_bytes / (1024 * 1024)
    duration    = (end_time - start_time).total_seconds() / 60

    if duration <= 0:
        log("Save skipped: zero duration.")
        return False

    record = {
        "start_time":       start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time":         end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_minutes": round(duration, 4),
        "bytes_sent":       bytes_sent,
        "bytes_received":   bytes_recv,
        "total_bytes":      total_bytes,
        "usage_MB":         round(mb_used, 6)
    }

    csv_row = pd.DataFrame([record])

    csv_ok = False
    for attempt in range(retries):
        try:
            csv_row.to_csv(FILE_PATH, mode='a', header=False, index=False)
            csv_ok = True
            break
        except PermissionError:
            log(f"Save attempt {attempt + 1}/{retries} failed: CSV open in Excel. Retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            log(f"Save error: {e}")
            break

    if not csv_ok:
        pending = FILE_PATH + ".pending"
        try:
            csv_row.to_csv(pending, mode="a", header=not os.path.exists(pending), index=False)
            log(f"Session saved to pending file: {pending}")
        except Exception as e:
            log(f"Pending CSV write also failed: {e}")

    json_ok = atomic_json_append(JSON_PATH, record)

    if csv_ok:
        log(f"Saved: {mb_used:.4f} MB in {duration:.2f} mins")
    if not csv_ok and not json_ok:
        log("CRITICAL: Both CSV and JSON saves failed. Data lost for this session.")
        return False
    if not csv_ok:
        log("CSV failed — data preserved in JSON.")
    if not json_ok:
        log("JSON failed — data preserved in CSV.")

    return True

_state = {}
_shutdown_lock = threading.Lock()
_shutdown_done = False

def do_shutdown_save():
    global _shutdown_done
    with _shutdown_lock:
        if _shutdown_done:
            return
        _shutdown_done = True
        if _state.get("connected") and _state.get("start_data"):
            data = get_interface_counters(_state.get("interface"))
            end_data = data if data else _state.get("last_data")
            if end_data:
                log("Saving session before exit...")
                save_session(
                    _state["start_data"],
                    end_data,
                    _state["start_time"],
                    datetime.now()
                )

def shutdown_handler(*args):
    log("Shutdown detected.")
    do_shutdown_save()
    release_lock()
    log("Tracker stopped.")
    sys.exit(0)

def reset_state():
    _state["connected"]  = False
    _state["interface"]  = None
    _state["start_data"] = None
    _state["last_data"]  = None
    _state["start_time"] = None

def track_usage():
    acquire_lock()
    initialize_csv()
    initialize_json()
    merge_pending_csv()

    log("Tracker started (30-minute auto-save)")

    atexit.register(do_shutdown_save)
    atexit.register(release_lock)
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    reset_state()
    last_save_time       = None
    consecutive_failures = 0

    while True:
        try:
            current_interface = get_active_interface()
            now = datetime.now()
            consecutive_failures = 0

            if current_interface and not _state["connected"]:
                data = get_interface_counters(current_interface)
                if data:
                    log(f"Connected: {current_interface}")
                    _state["interface"]  = current_interface
                    _state["start_data"] = data
                    _state["last_data"]  = data
                    _state["start_time"] = now
                    _state["connected"]  = True
                    last_save_time       = now
                else:
                    log("Connected but counter read failed, retrying...")

            elif current_interface and _state["connected"]:
                data = get_interface_counters(_state["interface"])
                if data:
                    _state["last_data"] = data

                if current_interface != _state["interface"]:
                    log(f"Interface changed: {_state['interface']} → {current_interface}")
                    end_data = data if data else _state.get("last_data")
                    if end_data:
                        save_session(_state["start_data"], end_data, _state["start_time"], now)
                    new_data = get_interface_counters(current_interface)
                    _state["interface"]  = current_interface
                    _state["start_data"] = new_data
                    _state["last_data"]  = new_data
                    _state["start_time"] = now
                    last_save_time       = now

                elif last_save_time and (now - last_save_time).total_seconds() >= AUTO_SAVE_INTERVAL:
                    if data:
                        log("Auto-saving (30 min)")
                        save_session(_state["start_data"], data, _state["start_time"], now)
                        _state["start_data"] = data
                        _state["start_time"] = now
                        last_save_time       = now
                    else:
                        log("Auto-save skipped: counter read failed.")

            elif not current_interface and _state["connected"]:
                log("Disconnected → saving session")
                end_data = get_interface_counters(_state["interface"]) or _state.get("last_data")
                if end_data:
                    save_session(_state["start_data"], end_data, _state["start_time"], now)
                else:
                    log("Disconnect save skipped: no counter data available.")
                reset_state()
                last_save_time = None

        except Exception as e:
            consecutive_failures += 1
            log(f"Unexpected error ({consecutive_failures}): {e}")
            if consecutive_failures >= 10:
                log("Too many consecutive failures, resetting state...")
                reset_state()
                last_save_time       = None
                consecutive_failures = 0

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    track_usage()