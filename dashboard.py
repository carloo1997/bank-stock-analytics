"""
Interactive Financial Analytics Dashboard (Streamlit)
=====================================================
Run locally:  streamlit run dashboard.py

Tabs:
1. Performance  — normalized chart, KPI cards
2. Technical    — candlestick + moving averages
3. Risk         — drawdown, rolling volatility, return distribution
4. Correlation  — heatmap + volatility comparison
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import kpi_analysis as kpi

st.set_page_config(page_title="Bank Stock Analytics", page_icon="🏦", layout="wide")

# ---------- Data ----------
@st.cache_data
def get_data():
    df = kpi.load_clean()
    return df, kpi.close_matrix(df)

df, close_all = get_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
companies = st.sidebar.multiselect(
    "Companies", list(close_all.columns), default=list(close_all.columns)
)
period = st.sidebar.selectbox("Period", ["6M", "1Y", "2Y"], index=2)
days = {"6M": 126, "1Y": 252, "2Y": 10_000}[period]

close = close_all[companies].tail(days)
if close.empty or not companies:
    st.warning("Select at least one company.")
    st.stop()

st.title("🏦 Bank Stock Analytics Dashboard")
st.caption("Deutsche Bank · BNP Paribas · HSBC — daily data via yfinance, stored in SQLite")

# ---------- KPI cards ----------
summary = kpi.kpi_summary(close)
cols = st.columns(len(summary))
for col, (_, row) in zip(cols, summary.iterrows()):
    col.metric(
        row["Company"],
        f"{row['Last Price']}",
        f"{row['Total Return %']} % total",
    )
    col.caption(f"Vol {row['Ann. Volatility %']}% · Sharpe {row['Sharpe Ratio']} · MaxDD {row['Max Drawdown %']}%")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance", "🕯️ Technical", "⚠️ Risk", "🔗 Correlation"])

# ---------- Tab 1: Performance ----------
with tab1:
    norm = kpi.normalized(close)
    fig = px.line(norm, title=f"Normalized Performance (Base 100) — {period}")
    fig.add_hline(y=100, line_dash="dash", line_color="gray")
    fig.update_layout(yaxis_title="Performance (Base 100)", legend_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(summary, use_container_width=True, hide_index=True)

# ---------- Tab 2: Technical ----------
with tab2:
    company = st.selectbox("Company for candlestick", companies)
    ticker_df = df[df["CompanyName"] == company].set_index("Date").tail(days)
    ma = kpi.with_moving_averages(close_all, company).tail(days)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=ticker_df.index, open=ticker_df["Open"], high=ticker_df["High"],
        low=ticker_df["Low"], close=ticker_df["Close"], name=company,
    ))
    fig.add_trace(go.Scatter(x=ma.index, y=ma["MA50"], name="MA 50", line=dict(width=1.5)))
    fig.add_trace(go.Scatter(x=ma.index, y=ma["MA200"], name="MA 200", line=dict(width=1.5)))
    fig.update_layout(title=f"{company} — Candlestick with Moving Averages",
                      xaxis_rangeslider_visible=False, height=550)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Tab 3: Risk ----------
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        dd = kpi.drawdown_series(close) * 100
        fig = px.line(dd, title="Drawdown from Peak (%)")
        fig.update_layout(yaxis_title="Drawdown %", legend_title="")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        rv = kpi.rolling_volatility(close)
        fig = px.line(rv, title="30-Day Rolling Volatility (annualized, %)")
        fig.update_layout(yaxis_title="Volatility %", legend_title="")
        st.plotly_chart(fig, use_container_width=True)

    rets = kpi.daily_returns(close) * 100
    fig = px.histogram(rets.melt(var_name="Company", value_name="Daily Return %"),
                       x="Daily Return %", color="Company", barmode="overlay",
                       nbins=80, title="Distribution of Daily Returns")
    st.plotly_chart(fig, use_container_width=True)

# ---------- Tab 4: Correlation ----------
with tab4:
    c1, c2 = st.columns(2)
    with c1:
        corr = kpi.correlation_matrix(close)
        fig = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r",
                        zmin=-1, zmax=1, title="Correlation of Daily Returns")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        vol = kpi.kpi_summary(close)[["Company", "Ann. Volatility %"]]
        fig = px.bar(vol, x="Company", y="Ann. Volatility %",
                     title="Annualized Volatility Comparison", color="Company")
        st.plotly_chart(fig, use_container_width=True)
