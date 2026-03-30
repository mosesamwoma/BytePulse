import pandas as pd
import os
from prophet import Prophet

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "usage_log.csv")

def load_daily():
    df = pd.read_csv(CSV_PATH, parse_dates=["start_time"])
    df["date"] = df["start_time"].dt.date
    daily = df.groupby("date")["usage_MB"].sum().reset_index()
    daily.columns = ["ds", "y"]
    daily["ds"] = pd.to_datetime(daily["ds"])
    return daily

def forecast(days=7):
    daily = load_daily()

    if len(daily) < 10:
        return None, None

    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False,
        changepoint_prior_scale=0.1
    )
    model.fit(daily)

    future = model.make_future_dataframe(periods=days)
    forecast_df = model.predict(future)

    forecast_df = forecast_df[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(days)
    forecast_df.columns = ["date", "predicted_MB", "lower_MB", "upper_MB"]
    forecast_df["predicted_MB"] = forecast_df["predicted_MB"].clip(lower=0).round(2)
    forecast_df["lower_MB"]     = forecast_df["lower_MB"].clip(lower=0).round(2)
    forecast_df["upper_MB"]     = forecast_df["upper_MB"].clip(lower=0).round(2)

    return forecast_df, model

if __name__ == "__main__":
    result, model = forecast(days=7)
    if result is None:
        print("Not enough data.")
    else:
        print(result.to_string(index=False))