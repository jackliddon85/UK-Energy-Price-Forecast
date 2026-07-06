"""Streamlit dashboard: UK electricity price forecast vs actuals.

Run with:  streamlit run app.py
"""
import json

import pandas as pd
import streamlit as st

st.set_page_config(page_title="UK Energy Price Forecast", layout="wide")
st.title("UK Electricity Price Forecasting")
st.caption(
    "Day-ahead half-hourly system price forecasts, trained on Elexon open data. "
    "Model: gradient-boosted trees vs naive baselines."
)

try:
    results = pd.read_csv("data/results.csv", parse_dates=["timestamp"])
    metrics = json.load(open("data/metrics.json"))
except FileNotFoundError:
    st.error("No results found. Run `python src/fetch_data.py` then `python src/train.py` first.")
    st.stop()

# Headline metrics
c1, c2, c3 = st.columns(3)
c1.metric("Model MAE (£/MWh)", metrics["model"]["MAE"])
c2.metric("Naive 24h MAE (£/MWh)", metrics["naive_24h"]["MAE"])
improvement = 1 - metrics["model"]["MAE"] / metrics["naive_24h"]["MAE"]
c3.metric("Improvement vs naive", f"{improvement:.1%}")

# Date range selector
min_d, max_d = results["timestamp"].min().date(), results["timestamp"].max().date()
default_start = max(min_d, max_d - pd.Timedelta(days=7))
start, end = st.slider(
    "Date range", min_value=min_d, max_value=max_d,
    value=(default_start, max_d), format="DD MMM YYYY",
)
mask = (results["timestamp"].dt.date >= start) & (results["timestamp"].dt.date <= end)
view = results[mask].set_index("timestamp")

st.subheader("Actual vs predicted price")
st.line_chart(view[["price", "predicted"]], height=380)

st.subheader("Cheapest hours of the day (test period average)")
hourly = (
    results.assign(hour=results["timestamp"].dt.hour)
    .groupby("hour")["price"].mean()
)
st.bar_chart(hourly, height=300)
cheapest = hourly.nsmallest(3).index.tolist()
st.info(f"Cheapest hours on average: {', '.join(f'{h:02d}:00' for h in sorted(cheapest))} "
        "— useful for scheduling EV charging or appliances.")

st.subheader("Error distribution")
view = view.assign(error=view["predicted"] - view["price"])
st.line_chart(view["error"], height=250)
