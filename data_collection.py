"""
Data Collection Module
======================
Downloads 2 years of daily OHLCV data for Deutsche Bank, BNP Paribas
and HSBC via yfinance and stores it in a SQLite database in a clean,
normalized long format (one row per date per ticker).

Why long format? It is the standard for relational databases:
easier to query with SQL, easier to extend with new tickers,
and it avoids the messy "('Close', 'BNP.PA')" column names.

Run: python3 data_collection.py
"""

import yfinance as yf
import pandas as pd
import sqlite3

DB_PATH = "financial_data.db"
TICKERS = {
    "DBK.DE": "Deutsche Bank",
    "BNP.PA": "BNP Paribas",
    "HSBA.L": "HSBC",
}


def download_stock_data(period: str = "2y") -> pd.DataFrame:
    """Download OHLCV data and reshape it into a tidy long format."""
    print(f"Downloading {period} of data for: {', '.join(TICKERS)}")
    raw = yf.download(list(TICKERS.keys()), period=period, interval="1d")

    # raw has MultiIndex columns like (Close, DBK.DE) -> stack to long format
    df = (
        raw.stack(level=1, future_stack=True)
        .rename_axis(["Date", "Ticker"])
        .reset_index()
    )
    df["CompanyName"] = df["Ticker"].map(TICKERS)
    df = df.dropna(subset=["Close"])  # drop rows without prices
    return df[["Date", "Ticker", "CompanyName", "Open", "High", "Low", "Close", "Volume"]]


def save_to_database(df: pd.DataFrame, db_path: str = DB_PATH) -> None:
    """Store the tidy dataframe in SQLite (table: stock_prices)."""
    conn = sqlite3.connect(db_path)
    df.to_sql("stock_prices", conn, if_exists="replace", index=False)

    # Quick sanity check via SQL
    check = pd.read_sql(
        "SELECT Ticker, COUNT(*) AS rows, MIN(Date) AS first_day, MAX(Date) AS last_day "
        "FROM stock_prices GROUP BY Ticker",
        conn,
    )
    conn.close()
    print("\nDatabase saved. Overview:")
    print(check.to_string(index=False))


if __name__ == "__main__":
    data = download_stock_data()
    save_to_database(data)
    print("\n✅ Step 1 complete: data collected and stored in SQLite.")
