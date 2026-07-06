# UK Electricity Price Forecasting

Day-ahead forecasting of half-hourly GB electricity system prices using open data from [Elexon's Insights API](https://developer.data.elexon.co.uk/) (no API key required).

**Why it's interesting:** electricity prices swing wildly within a single day — knowing tomorrow's cheap and expensive periods matters for EV charging, battery storage, and demand-shifting. This project builds a gradient-boosted model and, crucially, benchmarks it against naive baselines to prove it adds real value.

## Results

| Model | MAE (£/MWh) | RMSE (£/MWh) |
|---|---|---|
| Gradient boosting | **38.73** | **53.97** |
| Naive (same time yesterday) | 42.01 | 63.82 |
| Naive (same time last week) | 42.57 | 64.45 |

The model beats the 24h-naive baseline by **7.8% on MAE**, trained and tested on one year of real half-hourly GB system prices with a strict chronological split.

Real system prices are highly volatile — the model captures the daily demand-driven pattern well but struggles with extreme spike events. Adding wind generation data is the planned next step, as wind is the largest driver of GB price spikes.
![Dashboard](dashboard.png)
## How it works

1. **Data** — half-hourly system prices and national demand outturn from Elexon, fetched via `src/fetch_data.py`.
2. **Features** — cyclical time-of-day encoding, day-of-week, month, price/demand lags at 24h, 48h and 1 week, and rolling statistics. All lags start ≥24h back so the day-ahead forecast never leaks future information.
3. **Model** — `HistGradientBoostingRegressor` with a strict chronological train/test split (no shuffling — this is time series).
4. **Evaluation** — MAE/RMSE vs two naive baselines. A model that can't beat "same time yesterday" isn't worth deploying.
5. **Dashboard** — Streamlit app showing forecasts vs actuals, error distribution, and the cheapest hours of the day.

## Run it

```bash
pip install -r requirements.txt

# Fetch a year of real data (takes a few minutes, ~365 API calls)
python src/fetch_data.py --days 365

# Or generate synthetic demo data to test the pipeline offline
python src/fetch_data.py --synthetic

# Train and evaluate
python src/train.py

# Launch the dashboard
streamlit run app.py
```

## Ideas for extension

- Add weather features (temperature, wind) from the free [Open-Meteo API](https://open-meteo.com/) — wind generation is a major price driver in GB
- Forecast quantiles instead of point estimates to capture price-spike risk
- Simulate a home battery: charge at forecast-cheap periods, discharge at peak, and report the £ saved
- Deploy the dashboard free on Streamlit Community Cloud and link it

## Data source

Contains BMRS data © Elexon Limited, reproduced under the [BSC open data licence](https://www.elexon.co.uk/data/balancing-mechanism-reporting-agent/copyright-licence-bmrs-data/).
