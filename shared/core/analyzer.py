import pandas as pd
from pathlib import Path
import os

# Fix: Point to BytePulse/data, not shared/data
PROJECT_ROOT = Path(__file__).parent.parent.parent  # BytePulse/
INPUT = os.path.join(PROJECT_ROOT, "data", "usage_log.csv")

def load_data():
    if not os.path.exists(INPUT):
        return pd.DataFrame(columns=[
            "start_time", "end_time", "duration_minutes",
            "bytes_sent", "bytes_received", "total_bytes", "usage_MB"
        ])
    
    df = pd.read_csv(INPUT, parse_dates=["start_time", "end_time"])
    
    # Fallback: ensure datetime conversion even if parse_dates fails
    if not pd.api.types.is_datetime64_any_dtype(df["start_time"]):
        df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
    if not pd.api.types.is_datetime64_any_dtype(df["end_time"]):
        df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")
    
    return df

def summarize(df, by):
    if df.empty:
        return pd.DataFrame()
    
    if by == "date":
        grouped = df.groupby(df["start_time"].dt.date).agg({
            "usage_MB": "sum",
            "duration_minutes": "sum",
            "bytes_sent": "count"  # Count sessions using a different column
        }).reset_index()
        grouped.columns = ["date", "total_MB", "total_duration", "sessions"]
        return grouped
    
    elif by == "week":
        grouped = df.groupby(df["start_time"].dt.isocalendar().week).agg({
            "usage_MB": "sum",
            "duration_minutes": "sum",
            "bytes_sent": "count"  # Count sessions using a different column
        }).reset_index()
        grouped.columns = ["week", "total_MB", "total_duration", "sessions"]
        return grouped
    
    elif by == "month":
        grouped = df.groupby(df["start_time"].dt.to_period("M")).agg({
            "usage_MB": "sum",
            "duration_minutes": "sum",
            "bytes_sent": "count"  # Count sessions using a different column
        }).reset_index()
        grouped.columns = ["month", "total_MB", "total_duration", "sessions"]
        grouped["month"] = grouped["month"].astype(str)
        return grouped
    
    return df