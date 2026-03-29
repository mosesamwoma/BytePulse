from fastapi import APIRouter
from datetime import date
from .database import get_connection

router = APIRouter()

@router.get("/sessions")
def get_sessions():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM sessions ORDER BY start_time DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/sessions/today")
def get_today():
    conn = get_connection()
    today = date.today().isoformat()
    rows = conn.execute(
        "SELECT * FROM sessions WHERE start_time LIKE ? ORDER BY start_time DESC",
        (f"{today}%",)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/sessions/daily")
def get_daily():
    conn = get_connection()
    rows = conn.execute("""
        SELECT DATE(start_time) as date,
               COUNT(*) as sessions,
               ROUND(SUM(usage_MB), 4) as total_MB,
               ROUND(SUM(duration_minutes), 2) as total_duration_minutes,
               SUM(bytes_sent) as total_bytes_sent,
               SUM(bytes_received) as total_bytes_received
        FROM sessions
        GROUP BY DATE(start_time)
        ORDER BY date DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/sessions/weekly")
def get_weekly():
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-W%W', start_time) as week,
               COUNT(*) as sessions,
               ROUND(SUM(usage_MB), 4) as total_MB,
               ROUND(SUM(duration_minutes), 2) as total_duration_minutes,
               SUM(bytes_sent) as total_bytes_sent,
               SUM(bytes_received) as total_bytes_received
        FROM sessions
        GROUP BY week
        ORDER BY week DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/sessions/monthly")
def get_monthly():
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', start_time) as month,
               COUNT(*) as sessions,
               ROUND(SUM(usage_MB), 4) as total_MB,
               ROUND(SUM(duration_minutes), 2) as total_duration_minutes,
               SUM(bytes_sent) as total_bytes_sent,
               SUM(bytes_received) as total_bytes_received
        FROM sessions
        GROUP BY month
        ORDER BY month DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]