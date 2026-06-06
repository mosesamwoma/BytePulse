import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from pathlib import Path

# Fix: Add BytePulse root to path (app.py is in linux/)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Now safe to import from shared
from shared.core.analyzer import load_data, summarize
from shared.core.anomaly import detect_anomalies
from shared.core.forecaster import forecast

# Import alerts functions directly
import importlib.util
alerts_path = PROJECT_ROOT / "linux" / "src" / "alerts.py"
spec = importlib.util.spec_from_file_location("alerts_module", alerts_path)
alerts_module = importlib.util.module_from_spec(spec)
sys.modules["alerts_module"] = alerts_module
spec.loader.exec_module(alerts_module)
get_daily_usage_sqlite = alerts_module.get_daily_usage_sqlite
get_monthly_usage_sqlite = alerts_module.get_monthly_usage_sqlite
CAP_MB = alerts_module.CAP_MB
MONTHLY_CAP_MB = alerts_module.MONTHLY_CAP_MB

from datetime import date, datetime

st.set_page_config(page_title="BytePulse", layout="wide")

# Sidebar
with st.sidebar:
    st.title("BytePulse")
    view = st.selectbox("View", ["Daily", "Weekly", "Monthly"])
    st.divider()
    st.caption(f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

@st.cache_data
def load_cached():
    return load_data()

@st.cache_data
def load_forecast_cached():
    return forecast(days=7)

# Load data
df = load_cached()

# Ensure datetime types are set
if not df.empty:
    if not pd.api.types.is_datetime64_any_dtype(df["start_time"]):
        df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
    if not pd.api.types.is_datetime64_any_dtype(df["end_time"]):
        df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")

# Check if data is empty BEFORE trying to use dt accessor
if df.empty or df["start_time"].isna().all():
    st.warning("No data available yet. Tracker is collecting data...")
    st.stop()

df["hour"] = df["start_time"].dt.hour
df["day_name"] = df["start_time"].dt.day_name()

# ============ MAIN: 7-Day Forecast (TOP PRIORITY) ============
st.header("7-Day Usage Forecast")

forecast_df, model = load_forecast_cached()
if forecast_df is None:
    st.info("📊 Not enough data to forecast. Please wait for more tracking data.")
else:
    # Create forecast visualization
    forecast_df["day_label"] = pd.to_datetime(forecast_df["date"]).dt.strftime("%A %d %b")
    
    # Create the chart
    fig, ax = plt.subplots(figsize=(12, 4))
    
    # Convert to numeric for plotting
    y_pred = pd.to_numeric(forecast_df["predicted_MB"], errors='coerce')
    y_lower = pd.to_numeric(forecast_df["lower_MB"], errors='coerce')
    y_upper = pd.to_numeric(forecast_df["upper_MB"], errors='coerce')
    x_range = range(len(forecast_df))
    
    # Plot confidence interval as filled area
    ax.fill_between(x_range, y_lower, y_upper, alpha=0.3, color="#1f77b4", label="Confidence Range")
    
    # Plot main line
    ax.plot(x_range, y_pred, marker="o", color="#1f77b4", linewidth=2, markersize=8, label="Predicted")
    
    # Styling
    ax.set_xticks(x_range)
    ax.set_xticklabels(forecast_df["day_label"], rotation=15, ha="right")
    ax.set_xlabel("Day", fontsize=11)
    ax.set_ylabel("Predicted MB", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor("#f8f9fa")
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Display forecast table
    display_df = forecast_df[["day_label", "predicted_MB", "lower_MB", "upper_MB"]].copy()
    display_df.columns = ["Day", "Predicted (MB)", "Lower (MB)", "Upper (MB)"]
    
    # Format numbers
    for col in ["Predicted (MB)", "Lower (MB)", "Upper (MB)"]:
        display_df[col] = pd.to_numeric(display_df[col], errors='coerce').round(2)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

# ============ Summary Metrics ============
if view == "Daily":
    data = summarize(df, "date")
    x = "date"
elif view == "Weekly":
    data = summarize(df, "week")
    x = "week"
else:
    data = summarize(df, "month")
    x = "month"

data = data.reset_index(drop=True)

if data.empty:
    st.warning("No data available yet. Tracker is collecting data...")
    st.stop()

today = date.today()
today_df = df[df["start_time"].dt.date == today]
today_usage = round(today_df["usage_MB"].sum(), 2)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Data (MB)", f"{data['total_MB'].sum():.2f}")
col2.metric("Sessions", f"{int(data['sessions'].sum())}")
col3.metric("Peak Day (MB)", f"{data['total_MB'].max():.2f}")
col4.metric("Today (MB)", f"{today_usage}")
col5.metric("Days Tracked", len(data))

st.divider()

# ============ Data Cap Info ============
if view == "Daily":
    st.subheader("Daily Data Cap")
    cycle_usage = get_daily_usage_sqlite()
    usage_pct = min(cycle_usage / CAP_MB, 1.0)
    col1, col2 = st.columns(2)
    col1.metric("Used", f"{cycle_usage:.0f} MB")
    col2.metric("Cap", f"{CAP_MB} MB")
    st.progress(usage_pct)

elif view == "Monthly":
    st.subheader("Monthly Data Cap")
    monthly_usage = get_monthly_usage_sqlite()
    monthly_pct = min(monthly_usage / MONTHLY_CAP_MB, 1.0)
    col1, col2 = st.columns(2)
    col1.metric("Used", f"{monthly_usage:.0f} MB")
    col2.metric("Cap", f"{MONTHLY_CAP_MB} MB")
    st.progress(monthly_pct)

st.divider()

# ============ Usage Charts ============
if view == "Daily":
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Usage Over Time")
        st.line_chart(data.set_index(x)["total_MB"], use_container_width=True)
    
    with col2:
        st.subheader("Sessions Over Time")
        st.bar_chart(data.set_index(x)["sessions"], use_container_width=True)

st.divider()

# ============ Hourly Heatmap ============
if view == "Daily":
    st.subheader("Hourly Usage Pattern (MB)")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_data = df.groupby(["day_name", "hour"])["usage_MB"].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="day_name", columns="hour", values="usage_MB").reindex(day_order).fillna(0)
    
    fig, ax = plt.subplots(figsize=(14, 4))
    im = ax.imshow(heatmap_pivot.values, aspect="auto", cmap="Blues")
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h}:00" for h in range(24)], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(day_order)))
    ax.set_yticklabels(day_order, fontsize=9)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day")
    plt.colorbar(im, ax=ax, label="MB")
    plt.tight_layout()
    st.pyplot(fig)

st.divider()

# ============ Peak Hours ============
if view == "Daily":
    st.subheader("Peak Hours")
    peak = df.groupby("hour")["usage_MB"].sum().reset_index()
    peak.columns = ["hour", "usage_MB"]
    peak["hour"] = peak["hour"].astype(str) + ":00"
    st.bar_chart(peak.set_index("hour")["usage_MB"])

st.divider()

# ============ Anomalies ============
st.subheader("Anomaly Detection")
anomalies = detect_anomalies()

def color_anomaly_row(row):
    if abs(row["z_score"]) >= 3:
        return ["background-color: #3d0000; color: #ff4c4c"] * len(row)
    elif abs(row["z_score"]) >= 2:
        return ["background-color: #3d2e00; color: #ffaa00"] * len(row)
    return [""] * len(row)

if anomalies.empty:
    st.success("✓ No anomalous sessions detected.")
else:
    st.warning(f"⚠️ {len(anomalies)} anomalous sessions detected.")
    st.dataframe(anomalies.tail(7).style.apply(color_anomaly_row, axis=1), use_container_width=True)

st.divider()

# ============ Detailed Data Table ============
st.subheader("Recent Data Summary")
st.dataframe(data.tail(10), use_container_width=True, hide_index=True)