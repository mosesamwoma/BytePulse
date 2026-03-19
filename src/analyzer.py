import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT = os.path.join(DATA_DIR, "usage_log.csv")

def load_data():
    df = pd.read_csv(INPUT)
    
    for col in ["start_time", "end_time"]:
        df[col] = pd.to_datetime(df[col], format="mixed", dayfirst=True)
    
    df["date"] = df["start_time"].dt.date
    df["week"] = df["start_time"].dt.to_period("W").astype(str)
    df["month"] = df["start_time"].dt.to_period("M").astype(str)
    return df

def summarize(df, group_col):
    return df.groupby(group_col).agg(
        sessions=("usage_MB", "count"),
        total_MB=("usage_MB", "sum"),
        total_duration=("duration_minutes", "sum")
    ).reset_index()