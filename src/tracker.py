import psutil
import time
import pandas as pd
from datetime import datetime
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FILE_PATH = os.path.join(DATA_DIR, "usage_log.csv")

POLL_INTERVAL = 5
AUTO_SAVE_INTERVAL = 1800

os.makedirs(DATA_DIR, exist_ok=True)


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def get_active_interface():
    stats = psutil.net_if_stats()
    for name, stat in stats.items():
        if stat.isup and "wi-fi" in name.lower():
            return name
    return None


def get_interface_counters(interface):
    try:
        counters = psutil.net_io_counters(pernic=True)
        return counters.get(interface, None)
    except:
        return None


def initialize_csv():
    try:
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
    except Exception as e:
        log(f"CSV init failed: {e}")
        sys.exit(1)


def save_session(start_data, end_data, start_time, end_time):
    try:
        if not start_data or not end_data:
            return False

        bytes_sent = end_data.bytes_sent - start_data.bytes_sent
        bytes_recv = end_data.bytes_recv - start_data.bytes_recv

        if bytes_sent < 0 or bytes_recv < 0:
            bytes_sent = max(0, bytes_sent)
            bytes_recv = max(0, bytes_recv)

        total_bytes = bytes_sent + bytes_recv
        mb_used = total_bytes / (1024 * 1024)
        duration = (end_time - start_time).total_seconds() / 60

        df = pd.DataFrame({
            "start_time": [start_time.strftime("%Y-%m-%d %H:%M:%S")],
            "end_time": [end_time.strftime("%Y-%m-%d %H:%M:%S")],
            "duration_minutes": [round(duration, 4)],
            "bytes_sent": [bytes_sent],
            "bytes_received": [bytes_recv],
            "total_bytes": [total_bytes],
            "usage_MB": [round(mb_used, 6)]
        })

        df.to_csv(FILE_PATH, mode='a', header=False, index=False)
        log(f"Saved: {mb_used:.6f} MB in {duration:.4f} mins")
        return True

    except PermissionError:
        log("Close CSV file if open.")
        return False
    except Exception as e:
        log(f"Save error: {e}")
        return False


def track_usage():
    initialize_csv()
    log("Tracker started (30-minute mode, full data)")

    connected = False
    interface = None
    start_data = None
    start_time = None
    last_save_time = None

    while True:
        try:
            current_interface = get_active_interface()
            now = datetime.now()

            if current_interface and not connected:
                data = get_interface_counters(current_interface)
                if data:
                    log(f"Connected: {current_interface}")
                    interface = current_interface
                    start_data = data
                    start_time = now
                    last_save_time = now
                    connected = True

            elif current_interface and connected:
                if current_interface != interface:
                    data = get_interface_counters(interface)
                    if data:
                        log("Interface changed → saving previous session")
                        save_session(start_data, data, start_time, now)

                    interface = current_interface
                    start_data = get_interface_counters(interface)
                    start_time = now
                    last_save_time = now

                elif (now - last_save_time).total_seconds() >= AUTO_SAVE_INTERVAL:
                    data = get_interface_counters(interface)
                    if data:
                        log("Auto-saving (30 min)")
                        save_session(start_data, data, start_time, now)
                        start_data = data
                        start_time = now
                        last_save_time = now

            elif not current_interface and connected:
                data = get_interface_counters(interface)
                if data:
                    log("Disconnected → saving session")
                    save_session(start_data, data, start_time, now)

                connected = False
                interface = None
                start_data = None

        except KeyboardInterrupt:
            log("Stopping tracker...")
            if connected and start_data:
                data = get_interface_counters(interface)
                if data:
                    save_session(start_data, data, start_time, datetime.now())
            sys.exit(0)

        except Exception as e:
            log(f"Unexpected error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    track_usage()