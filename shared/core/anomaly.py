import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "usage_log.csv")

def detect_anomalies(threshold=2.0):
    df = pd.read_csv(CSV_PATH, parse_dates=["start_time", "end_time"])
    if df.empty or len(df) < 5:
        return pd.DataFrame()

    mean = df["usage_MB"].mean()
    std  = df["usage_MB"].std()

    if std == 0:
        return pd.DataFrame()

    df["z_score"] = (df["usage_MB"] - mean) / std
    df["anomaly"] = df["z_score"] > threshold

    return df[df["anomaly"]][["start_time", "end_time", "usage_MB", "z_score"]].reset_index(drop=True)

if __name__ == "__main__":
    anomalies = detect_anomalies()
    if anomalies.empty:
        print("No anomalies detected.")
    else:
        print(f"{len(anomalies)} anomalous sessions detected:\n")
        print(anomalies.to_string(index=False))