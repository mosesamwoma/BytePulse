import pandas as pd
import os
import sqlite3
import time
from datetime import date
from win10toast import ToastNotifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "bytepulse.db")

CAP_MB = 10240  # 10GB in MB
WARN_THRESHOLD = 0.8
CHECK_INTERVAL = 1800  # 30 minutes in seconds

alert_states = {"warn": False, "limit": False}

def get_daily_usage_sqlite():
    try:
        conn = sqlite3.connect(DB_PATH)
        today = date.today().isoformat()
        query = "SELECT SUM(usage_MB) FROM sessions WHERE date(start_time) = ?"
        df = pd.read_sql_query(query, conn, params=(today,))
        conn.close()
        return df.iloc[0, 0] or 0.0
    except Exception:
        return 0.0

def check_alerts():
    global alert_states
    usage_MB = get_daily_usage_sqlite()
    usage_pct = usage_MB / CAP_MB
    toaster = ToastNotifier()

    if usage_pct >= 1.0 and not alert_states["limit"]:
        toaster.show_toast(
            "BytePulse — Daily Cap Reached",
            f"You have used {usage_MB:.0f} MB ({usage_pct:.0f}%).",
            duration=10, threaded=True
        )
        alert_states["limit"] = True
    
    elif usage_pct >= WARN_THRESHOLD and not alert_states["warn"] and not alert_states["limit"]:
        toaster.show_toast(
            "BytePulse — Daily Data Warning",
            f"80% of daily cap used ({usage_MB:.0f} MB).",
            duration=10, threaded=True
        )
        alert_states["warn"] = True

if __name__ == "__main__":
    while True:
        check_alerts()
        time.sleep(CHECK_INTERVAL)