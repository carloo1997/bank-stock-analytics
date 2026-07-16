"""
KPI Analysis Module
===================
Calculates the financial KPIs used throughout the project.
Every function takes the cleaned data and returns analysis-ready
DataFrames, so the dashboard can reuse the exact same logic.

KPIs implemented:
- Daily & cumulative returns
- Normalized performance (base 100)
- Annualized volatility (std of daily returns * sqrt(252))
- Sharpe ratio (assumes 2% risk-free rate)
- Maximum drawdown
- Moving averages (50d / 200d)
- 30-day rolling volatility
- Correlation matrix of daily returns

Run: python3 kpi_analysis.py  (prints a KPI summary table)
"""

import numpy as np
import pandas as pd
import sqlite3

DB_PATH = "financial_data.db"
TRADING_DAYS = 252
RISK_FREE_RATE = 0.02  # 2% p.a., simple assumption


def load_clean(db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM stock_prices_clean", conn, parse_dates=["Date"])
    conn.close()
    return df


def close_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot to wide format: one column of Close prices per company."""
    return df.pivot(index="Date", columns="CompanyName", values="Close").sort_index()


def daily_returns(close: pd.DataFrame) -> pd.DataFrame:
    return close.pct_change().dropna()


def normalized(close: pd.DataFrame) -> pd.DataFrame:
    return close / close.iloc[0] * 100


def max_drawdown(series: pd.Series) -> float:
    """Largest peak-to-trough loss, as a negative percentage."""
    cummax = series.cummax()
    drawdown = series / cummax - 1
    return float(drawdown.min())


def drawdown_series(close: pd.DataFrame) -> pd.DataFrame:
    return close / close.cummax() - 1


def kpi_summary(close: pd.DataFrame) -> pd.DataFrame:
    rets = daily_returns(close)
    rows = []
    for company in close.columns:
        r = rets[company]
        ann_vol = r.std() * np.sqrt(TRADING_DAYS)
        ann_ret = (1 + r.mean()) ** TRADING_DAYS - 1
        sharpe = (ann_ret - RISK_FREE_RATE) / ann_vol if ann_vol > 0 else np.nan
        rows.append({
            "Company": company,
            "Last Price": round(close[company].iloc[-1], 2),
            "Total Return %": round((close[company].iloc[-1] / close[company].iloc[0] - 1) * 100, 1),
            "Ann. Volatility %": round(ann_vol * 100, 1),
            "Sharpe Ratio": round(sharpe, 2),
            "Max Drawdown %": round(max_drawdown(close[company]) * 100, 1),
            "52W High": round(close[company].tail(TRADING_DAYS).max(), 2),
            "52W Low": round(close[company].tail(TRADING_DAYS).min(), 2),
        })
    return pd.DataFrame(rows)


def with_moving_averages(close: pd.DataFrame, company: str) -> pd.DataFrame:
    out = close[[company]].rename(columns={company: "Close"}).copy()
    out["MA50"] = out["Close"].rolling(50).mean()
    out["MA200"] = out["Close"].rolling(200).mean()
    return out


def rolling_volatility(close: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    return daily_returns(close).rolling(window).std() * np.sqrt(TRADING_DAYS) * 100


def correlation_matrix(close: pd.DataFrame) -> pd.DataFrame:
    return daily_returns(close).corr().round(2)


if __name__ == "__main__":
    close = close_matrix(load_clean())
    print("📊 KPI SUMMARY\n" + "=" * 60)
    print(kpi_summary(close).to_string(index=False))
    print("\nCorrelation of daily returns:")
    print(correlation_matrix(close).to_string())
    print("\n✅ Steps 3-4 complete: EDA statistics and KPIs calculated.")
