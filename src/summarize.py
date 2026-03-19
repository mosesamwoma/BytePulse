import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

INPUT = os.path.join(DATA_DIR, "usage_log.csv")
DAILY = os.path.join(DATA_DIR, "daily_summary.csv")
WEEKLY = os.path.join(DATA_DIR, "weekly_summary.csv")
MONTHLY = os.path.join(DATA_DIR, "monthly_summary.csv")


def load_data():
    df = pd.read_csv(INPUT, parse_dates=["start_time", "end_time"])
    df["date"] = df["start_time"].dt.date
    df["week"] = df["start_time"].dt.to_period("W").astype(str)
    df["month"] = df["start_time"].dt.to_period("M").astype(str)
    return df


def summarize(df, group_col, label):
    summary = df.groupby(group_col).agg(
        sessions=("usage_MB", "count"),
        total_MB=("usage_MB", "sum"),
        total_bytes_sent=("bytes_sent", "sum"),
        total_bytes_received=("bytes_received", "sum"),
        total_bytes=("total_bytes", "sum"),
        total_duration_minutes=("duration_minutes", "sum")
    ).reset_index()
    summary.rename(columns={group_col: label}, inplace=True)
    summary["total_MB"] = summary["total_MB"].round(4)
    summary["total_duration_minutes"] = summary["total_duration_minutes"].round(2)
    return summary


def run():
    if not os.path.exists(INPUT):
        print("No usage_log.csv found. Run the tracker first.")
        return

    df = load_data()

    if df.empty:
        print("No data found in usage_log.csv.")
        return

    daily = summarize(df, "date", "date")
    weekly = summarize(df, "week", "week")
    monthly = summarize(df, "month", "month")

    daily.to_csv(DAILY, index=False)
    weekly.to_csv(WEEKLY, index=False)
    monthly.to_csv(MONTHLY, index=False)

    print(f"Daily summary   → {DAILY}")
    print(f"Weekly summary  → {WEEKLY}")
    print(f"Monthly summary → {MONTHLY}")

    print("\n--- DAILY ---")
    print(daily.to_string(index=False))
    print("\n--- WEEKLY ---")
    print(weekly.to_string(index=False))
    print("\n--- MONTHLY ---")
    print(monthly.to_string(index=False))


if __name__ == "__main__":
    run()