import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.analyzer import load_data, summarize
from src.anomaly import detect_anomalies
from src.alerts import get_daily_usage_sqlite, CAP_MB, WARN_THRESHOLD
from src.forecaster import forecast
from datetime import date, datetime

st.set_page_config(page_title="BytePulse", layout="wide")
st.title("BytePulse Dashboard")

# --- Sidebar ---
view = st.sidebar.selectbox("View", ["Daily", "Weekly", "Monthly"])
st.sidebar.markdown("---")
auto_refresh = st.sidebar.toggle("Auto Refresh", value=True)
refresh_interval = st.sidebar.selectbox(
    "Refresh Every",
    [1800, 900, 300, 60],
    format_func=lambda x: {1800: "30 min", 900: "15 min", 300: "5 min", 60: "1 min"}[x]
)

st.caption(f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}")

if st.button("🔄 Refresh Now"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data
def load_cached():
    return load_data()

df = load_cached()
df["hour"] = df["start_time"].dt.hour
df["day_name"] = df["start_time"].dt.day_name()

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

today = date.today()
today_df = df[df["start_time"].dt.date == today]
today_usage = round(today_df["usage_MB"].sum(), 2)

st.subheader("Totals")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Data (MB)", round(data["total_MB"].sum(), 2))
c2.metric("Total Sessions", int(data["sessions"].sum()))
c3.metric("Total Duration (min)", int(data["total_duration"].sum()))
c4.metric("Peak Usage (MB)", round(data["total_MB"].max(), 2))
c5.metric("Today's Usage (MB)", today_usage)

st.markdown("---")

if view == "Daily":
    st.subheader("Data Cap")
    cycle_usage = get_daily_usage_sqlite()
    usage_pct = min(cycle_usage / CAP_MB, 1.0)
    st.metric("Daily Usage (MB)", f"{cycle_usage:.0f} / {CAP_MB}", delta=f"{usage_pct*100:.1f}% used")
    st.progress(usage_pct)
    st.markdown("---")

st.subheader("Data Usage Over Time (MB)")
st.line_chart(data.set_index(x)["total_MB"])

st.subheader("Sessions Over Time")
st.bar_chart(data.set_index(x)["sessions"])

st.markdown("---")

st.subheader("Peak Hours")
peak = df.groupby("hour")["usage_MB"].sum().reset_index()
peak.columns = ["hour", "usage_MB"]
peak["hour"] = peak["hour"].astype(str) + ":00"
st.bar_chart(peak.set_index("hour")["usage_MB"])

st.markdown("---")

# --- Daily Heatmap ---
if view == "Daily":
    st.subheader("Hourly Usage Heatmap")

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    available_days = [d for d in day_order if d in df["day_name"].unique()]
    selected_day = st.selectbox("Select Day", available_days)

    heatmap_data = df[df["day_name"] == selected_day].groupby("hour")["usage_MB"].sum().reset_index()
    heatmap_data = heatmap_data.set_index("hour").reindex(range(24), fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 1.8))
    im = ax.imshow([heatmap_data["usage_MB"].values], aspect="auto", cmap="Blues")
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h}:00" for h in range(24)], rotation=45, ha="right", fontsize=8)
    ax.set_yticks([0])
    ax.set_yticklabels([selected_day], fontsize=9)
    ax.set_xlabel("Hour of Day")
    plt.colorbar(im, ax=ax, label="MB")
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")

# --- Weekly Heatmap ---
if view == "Weekly":
    st.subheader("Weekly Usage Heatmap")

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["week_label"] = df["start_time"].dt.strftime("W%U %Y")

    weekly_heat = df.groupby(["week_label", "day_name"])["usage_MB"].sum().reset_index()
    weekly_pivot = weekly_heat.pivot(index="week_label", columns="day_name", values="usage_MB")
    cols_present = [d for d in day_order if d in weekly_pivot.columns]
    weekly_pivot = weekly_pivot[cols_present].fillna(0)

    fig, ax = plt.subplots(figsize=(10, max(3, len(weekly_pivot) * 0.7)))
    im = ax.imshow(weekly_pivot.values, aspect="auto", cmap="Greens")
    ax.set_xticks(range(len(cols_present)))
    ax.set_xticklabels(cols_present, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(len(weekly_pivot)))
    ax.set_yticklabels(weekly_pivot.index, fontsize=9)
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Week")
    plt.colorbar(im, ax=ax, label="MB")
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")

# --- Forecast & Anomalies (Daily only) ---
if view == "Daily":
    st.subheader("7-Day Usage Forecast")
    forecast_df, _ = forecast(days=7)
    if forecast_df is None:
        st.info("Not enough data to forecast.")
    else:
        forecast_df["day_label"] = pd.to_datetime(forecast_df["date"]).dt.strftime("%A %d %b")

        fig2, ax2 = plt.subplots(figsize=(10, 3))
        ax2.plot(forecast_df["day_label"], forecast_df["predicted_MB"], marker="o", color="#1f77b4")
        ax2.fill_between(
            forecast_df["day_label"],
            forecast_df["lower_MB"],
            forecast_df["upper_MB"],
            alpha=0.2,
            color="#1f77b4"
        )
        ax2.set_xlabel("Day")
        ax2.set_ylabel("Predicted MB")
        ax2.tick_params(axis="x", rotation=15)
        plt.tight_layout()
        st.pyplot(fig2)

        display_df = forecast_df[["day_label", "predicted_MB", "lower_MB", "upper_MB"]].copy()
        display_df.columns = ["Day", "Predicted (MB)", "Lower (MB)", "Upper (MB)"]
        st.dataframe(display_df, use_container_width=True)

    st.markdown("---")

    st.subheader("Anomaly Detection")
    anomalies = detect_anomalies()

    def color_anomaly_row(row):
        if abs(row["z_score"]) >= 3:
            return ["background-color: #3d0000; color: #ff4c4c"] * len(row)
        elif abs(row["z_score"]) >= 2:
            return ["background-color: #3d2e00; color: #ffaa00"] * len(row)
        return [""] * len(row)

    if anomalies.empty:
        st.success("No anomalous sessions detected.")
    else:
        st.warning(f"{len(anomalies)} anomalous sessions detected.")
        st.dataframe(
            anomalies.tail(7).style.apply(color_anomaly_row, axis=1),
            use_container_width=True
        )

    st.markdown("---")

st.subheader("Detailed Data")
if view == "Daily":
    st.dataframe(data.tail(7), use_container_width=True)
else:
    st.dataframe(data, use_container_width=True)

# --- Auto Refresh (runs last so UI renders first) ---
if auto_refresh:
    time.sleep(refresh_interval)
    st.cache_data.clear()
    st.rerun()