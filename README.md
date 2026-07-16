# 🏦 Bank Stock Analytics — End-to-End Financial Data Analysis

A complete data analytics project analyzing the stock performance of three major European banks — **Deutsche Bank (DBK.DE)**, **BNP Paribas (BNP.PA)** and **HSBC (HSBA.L)** — over the last two years. Built as a portfolio project targeting Data Analyst roles in the financial sector.

![Dashboard Screenshot](screenshots/dashboard.png)

## 🎯 What this project demonstrates

- **Data engineering**: automated data collection (yfinance API) into a normalized SQLite database
- **Data quality**: documented cleaning pipeline (missing values, duplicates, outlier flagging)
- **Financial analytics**: returns, annualized volatility, Sharpe ratio, maximum drawdown, moving averages, rolling volatility, correlation analysis
- **Visualization & BI**: interactive multi-tab Streamlit dashboard with Plotly charts
- **Software practices**: modular code, separation of concerns, reproducible setup

## 🛠️ Tech Stack

Python 3.13 · pandas · NumPy · SQLite · Plotly · Streamlit · yfinance

## 📁 Project Structure

```
project1-financial-dashboard/
├── data_collection.py   # Step 1: download OHLCV data -> SQLite (long format)
├── data_cleaning.py     # Step 2: data-quality pipeline -> stock_prices_clean
├── kpi_analysis.py      # Steps 3-4: EDA statistics + financial KPIs
├── dashboard.py         # Steps 5-6: interactive Streamlit dashboard
├── requirements.txt
└── README.md
```

## 🚀 Setup & Run

```bash
pip install -r requirements.txt

python3 data_collection.py   # 1. fetch data & build the database
python3 data_cleaning.py     # 2. clean the data
python3 kpi_analysis.py      # 3. print KPI summary in the terminal
streamlit run dashboard.py   # 4. open the interactive dashboard
```

The dashboard opens at `http://localhost:8501`.

## ☁️ Live Demo (free deployment)

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub
3. Select the repo and `dashboard.py` as the entry point
4. **Note:** commit `financial_data.db` to the repo (or call the collection script at startup) so the cloud app has data

## 📊 Key Insights (2024 – 2026)

- **Deutsche Bank was the top performer** (~+120% total return), driven by the strong recovery of European banking stocks
- **All three banks fell sharply in April 2025** — the market-wide tariff shock — visible as the deepest synchronized drawdown in the period
- **HSBC delivered the best risk-adjusted profile** among the three in parts of the period (lower rolling volatility at comparable returns)
- **Daily returns are highly correlated (≈0.6–0.8)** — the three stocks offer limited diversification against sector-wide shocks
- **Drawdown analysis** shows recoveries within weeks, reflecting a resilient bull market for European banks

*(Regenerate these numbers after each data refresh — `kpi_analysis.py` prints the current values.)*

## ⚠️ Disclaimer

Educational portfolio project. Not investment advice.
