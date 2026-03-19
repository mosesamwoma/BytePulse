import streamlit as st
import pandas as pd
from src.analyzer import load_data, summarize

st.set_page_config(page_title="BytePulse", layout="wide")
st.title("BytePulse Dashboard")

@st.cache_data
def load_cached():
    return load_data()

df = load_cached()

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

st.subheader("Totals")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Data (MB)", round(data["total_MB"].sum(), 2))
c2.metric("Total Sessions", int(data["sessions"].sum()))
c3.metric("Total Duration (min)", int(data["total_duration"].sum()))
c4.metric("Peak Usage (MB)", round(data["total_MB"].max(), 2))

st.markdown("---")

st.subheader("Data Usage Over Time (MB)")
st.line_chart(data.set_index(x)["total_MB"])

st.subheader("Sessions Over Time")
st.bar_chart(data.set_index(x)["sessions"])

st.markdown("---")

st.subheader("Peak Hours")
df["hour"] = df["start_time"].dt.hour
peak = df.groupby("hour")["usage_MB"].sum().reset_index()
peak.columns = ["hour", "usage_MB"]
peak["hour"] = peak["hour"].astype(str) + ":00"
st.bar_chart(peak.set_index("hour")["usage_MB"])

st.markdown("---")

st.subheader("Detailed Data")
st.dataframe(data, width="stretch")