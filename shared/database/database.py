import sqlite3
import os
from pathlib import Path

# Fix: Point to BytePulse root/data, not shared folder
BASE_DIR = Path(__file__).parent.parent.parent  # BytePulse/
DB_PATH = os.path.join(BASE_DIR, "data", "bytepulse.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL UNIQUE,
            end_time TEXT NOT NULL,
            duration_minutes REAL,
            bytes_sent INTEGER,
            bytes_received INTEGER,
            total_bytes INTEGER,
            usage_MB REAL
        )
    """)
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_start_time ON sessions(start_time)
    """)
    conn.commit()
    conn.close()

def save_to_db(record: dict):
    try:
        conn = get_connection()
        conn.execute("""
            INSERT OR IGNORE INTO sessions (start_time, end_time, duration_minutes, bytes_sent, bytes_received, total_bytes, usage_MB)
            VALUES (:start_time, :end_time, :duration_minutes, :bytes_sent, :bytes_received, :total_bytes, :usage_MB)
        """, record)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False