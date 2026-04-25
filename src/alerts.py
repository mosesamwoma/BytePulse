import pandas as pd
import os
import sqlite3
import time
from datetime import date, datetime
from win10toast import ToastNotifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "bytepulse.db")

CAP_MB = 10240          # 10GB daily cap in MB
MONTHLY_CAP_MB = 307200 # 10240 * 30 monthly cap in MB
WARN_THRESHOLD = 0.8    # 80% warning threshold
MONTHLY_WARN_THRESHOLD = 0.8
CHECK_INTERVAL = 1800   # 30 minutes in seconds

alert_states = {"warn": False, "limit": False, "monthly_warn": False, "monthly_limit": False}

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

def get_monthly_usage_sqlite():
    try:
        conn = sqlite3.connect(DB_PATH)
        now = datetime.now()
        df = pd.read_sql_query(
            "SELECT SUM(usage_MB) FROM sessions WHERE strftime('%Y-%m', start_time) = ?",
            conn,
            params=(now.strftime("%Y-%m"),)
        )
        conn.close()
        return round(df.iloc[0, 0] or 0.0, 2)
    except Exception:
        return 0.0

def check_alerts():
    global alert_states
    toaster = ToastNotifier()

    # --- Daily alerts ---
    usage_MB = get_daily_usage_sqlite()
    usage_pct = usage_MB / CAP_MB

    if usage_pct >= 1.0 and not alert_states["limit"]:
        toaster.show_toast(
            "BytePulse — Daily Cap Reached",
            f"You have used {usage_MB:.0f} MB ({usage_pct*100:.0f}%).",
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

    # --- Monthly alerts ---
    monthly_MB = get_monthly_usage_sqlite()
    monthly_pct = monthly_MB / MONTHLY_CAP_MB

    if monthly_pct >= 1.0 and not alert_states["monthly_limit"]:
        toaster.show_toast(
            "BytePulse — Monthly Cap Reached",
            f"You have used {monthly_MB:.0f} MB of your {MONTHLY_CAP_MB:.0f} MB monthly cap.",
            duration=10, threaded=True
        )
        alert_states["monthly_limit"] = True

    elif monthly_pct >= MONTHLY_WARN_THRESHOLD and not alert_states["monthly_warn"] and not alert_states["monthly_limit"]:
        toaster.show_toast(
            "BytePulse — Monthly Data Warning",
            f"80% of monthly cap used ({monthly_MB:.0f} MB).",
            duration=10, threaded=True
        )
        alert_states["monthly_warn"] = True

if __name__ == "__main__":
    while True:
        check_alerts()
        time.sleep(CHECK_INTERVAL)