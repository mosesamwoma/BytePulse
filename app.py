import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.analyzer import load_data, summarize
from datetime import date

st.set_page_config(page_title="BytePulse", layout="wide")
st.title("BytePulse Dashboard")

@st.cache_data
def load_cached():
    return load_data()

df = load_cached()
df["hour"] = df["start_time"].dt.hour
df["day_name"] = df["start_time"].dt.day_name()

view = st.sidebar.selectbox("View", ["Daily", "Weekly", "Monthly"])

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

if view == "Daily":
    st.subheader("Hourly Usage Heatmap")

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    heatmap_data = df.groupby(["day_name", "hour"])["usage_MB"].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="day_name", columns="hour", values="usage_MB").reindex(day_order).fillna(0)

    fig, ax = plt.subplots(figsize=(14, 4))
    im = ax.imshow(heatmap_pivot.values, aspect="auto", cmap="Blues")

    ax.set_xticks(range(len(heatmap_pivot.columns)))
    ax.set_xticklabels([f"{h}:00" for h in heatmap_pivot.columns], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(day_order)))
    ax.set_yticklabels(day_order, fontsize=9)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Day")

    plt.colorbar(im, ax=ax, label="MB")
    plt.tight_layout()

    st.pyplot(fig)

    st.markdown("---")

st.subheader("Detailed Data")
st.dataframe(data, use_container_width=True)