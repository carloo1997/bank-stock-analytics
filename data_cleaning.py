"""
Data Cleaning Module
====================
Loads raw data from SQLite, applies standard data-quality checks and
writes a cleaned table (stock_prices_clean) back to the database.

Each check mirrors what a bank's data-quality process would do:
1. Missing values   -> prices can be missing on partial trading days
2. Duplicates       -> same date+ticker twice would distort KPIs
3. Outliers         -> fat-finger errors / bad feeds (>25% daily move flagged)
4. Type consistency -> dates as datetime, prices as float

Run: python3 data_cleaning.py
"""

import pandas as pd
import sqlite3

DB_PATH = "financial_data.db"


def load_raw(db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM stock_prices", conn, parse_dates=["Date"])
    conn.close()
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    report = {}

    # 1) Missing values: forward-fill prices per ticker (weekend/holiday gaps
    #    are expected; true missing quotes inherit the last known price).
    report["missing_before"] = int(df[["Open", "High", "Low", "Close"]].isna().sum().sum())
    df = df.sort_values(["Ticker", "Date"])
    price_cols = ["Open", "High", "Low", "Close"]
    df[price_cols] = df.groupby("Ticker")[price_cols].ffill()
    df["Volume"] = df["Volume"].fillna(0)

    # 2) Duplicates: one row per (Date, Ticker)
    report["duplicates"] = int(df.duplicated(subset=["Date", "Ticker"]).sum())
    df = df.drop_duplicates(subset=["Date", "Ticker"], keep="last")

    # 3) Outliers: flag daily moves > 25% (kept, but flagged for review —
    #    in finance you never silently delete data).
    df["DailyReturn"] = df.groupby("Ticker")["Close"].pct_change()
    df["OutlierFlag"] = (df["DailyReturn"].abs() > 0.25).astype(int)
    report["outliers_flagged"] = int(df["OutlierFlag"].sum())

    # 4) Types
    df["Date"] = pd.to_datetime(df["Date"])

    print("Cleaning report:")
    for k, v in report.items():
        print(f"  {k}: {v}")
    return df


def save_clean(df: pd.DataFrame, db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    df.to_sql("stock_prices_clean", conn, if_exists="replace", index=False)
    conn.close()
    print(f"\n✅ Step 2 complete: cleaned table 'stock_prices_clean' saved ({len(df)} rows).")


if __name__ == "__main__":
    save_clean(clean(load_raw()))
