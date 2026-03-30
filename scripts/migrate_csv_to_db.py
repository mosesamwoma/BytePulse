import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import init_db, get_connection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "usage_log.csv")


def migrate():
    init_db()
    df = pd.read_csv(CSV_PATH, parse_dates=["start_time", "end_time"])
    df["start_time"] = df["start_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["end_time"]   = df["end_time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    existing = set(
        row[0] for row in conn.execute("SELECT start_time FROM sessions").fetchall()
    )

    inserted = 0
    for _, row in df.iterrows():
        if row["start_time"] in existing:
            continue
        conn.execute("""
            INSERT INTO sessions (start_time, end_time, duration_minutes, bytes_sent, bytes_received, total_bytes, usage_MB)
            VALUES (:start_time, :end_time, :duration_minutes, :bytes_sent, :bytes_received, :total_bytes, :usage_MB)
        """, row.to_dict())
        inserted += 1

    conn.commit()
    conn.close()
    print(f"Migrated {inserted} rows. Skipped {len(df) - inserted} duplicates.")


if __name__ == "__main__":
    migrate()