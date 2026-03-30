import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "bytepulse.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_minutes REAL,
            bytes_sent INTEGER,
            bytes_received INTEGER,
            total_bytes INTEGER,
            usage_MB REAL
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(record: dict):
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO sessions (start_time, end_time, duration_minutes, bytes_sent, bytes_received, total_bytes, usage_MB)
            VALUES (:start_time, :end_time, :duration_minutes, :bytes_sent, :bytes_received, :total_bytes, :usage_MB)
        """, record)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False