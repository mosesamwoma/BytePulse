import pandas as pd
import os
from datetime import date
from win10toast import ToastNotifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "usage_log.csv")

CAP_MB         = 6144
WARN_THRESHOLD = 0.8

def get_cycle_usage():
    df = pd.read_csv(CSV_PATH, parse_dates=["start_time"])
    today = date.today()
    df = df[df["start_time"].dt.date == today]
    return df["usage_MB"].sum()

def check_alerts():
    usage_MB  = get_cycle_usage()
    usage_pct = usage_MB / CAP_MB

    toaster = ToastNotifier()

    if usage_pct >= 1.0:
        toaster.show_toast(
            "BytePulse — Daily Cap Reached",
            f"You have used {usage_MB:.0f} MB of your {CAP_MB} MB daily cap.",
            duration=10,
            threaded=True
        )
    elif usage_pct >= WARN_THRESHOLD:
        toaster.show_toast(
            "BytePulse — Daily Data Warning",
            f"{usage_pct*100:.0f}% of daily cap used ({usage_MB:.0f} / {CAP_MB} MB).",
            duration=10,
            threaded=True
        )

if __name__ == "__main__":
    check_alerts()