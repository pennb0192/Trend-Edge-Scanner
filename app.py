#!/usr/bin/env python3
# 1:1 Rule — Trend Edge Scanner (MVP SaaS: Auth + Charts + LIVE + TradingView)
import time
import pandas as pd
import numpy as np
import streamlit as st
from streamlit.components.v1 import html

# ---------- AUTH ----------
# pip install streamlit-authenticator
import streamlit_authenticator as stauth

st.set_page_config(page_title="1:1 Trend Edge Scanner", layout="wide")

# Load auth + stripe config from Streamlit Secrets
# (You will paste this in Streamlit Cloud later.)
AUTH = st.secrets.get("auth_config", None)
STRIPE = st.secrets.get("stripe", {})
CHECKOUT_URL = STRIPE.get("checkout_url", "https://stripe.com")  # fallback link

if AUTH is None:
    st.error("Auth not configured. Add 'auth_config' to Streamlit secrets.")
    st.stop()

# Build authenticator object
credentials = AUTH["credentials"]
cookie_cfg = AUTH["cookie"]
authenticator = stauth.Authenticate(
    credentials,
    cookie_cfg["name"],
    cookie_cfg["key"],
    cookie_cfg.get("expiry_days", 30),
)

# Public landing (login box)
st.title("📈 1:1 Rule — Trend Edge Scanner")

name, auth_status, username = authenticator.login("Login", "main")

if auth_status is False:
    st.error("Invalid username or password.")
    st.link_button("Subscribe to get access", CHECKOUT_URL)
    st.stop()
elif auth_status is None:
    st.info("Enter your email and password to continue.")
    st.link_button("Subscribe to get access", CHECKOUT_URL)
    st.stop()

# If logged in:
authenticator.logout("Logout", "sidebar")
st.caption(f"Welcome, **{name}**")

# ---------- APP IMPORTS ----------
try:
    import yfinance as yf
except Exception:
    st.error("yfinance is required. Install with: pip install yfinance")
    st.stop()

# ---------------- Settings ----------------
with st.sidebar:
    st.subheader("Scanner Settings")
    tickers = st.text_input(
        "Tickers (comma-separated)",
        "SPY,AAPL,MSFT,TSLA,NVDA,AMD,META,GOOGL,AMZN,SBUX,QQQ",
    )
    period = st.selectbox("History period", ["1d","5d","7d","3mo","6mo","1y","2y"], index=4)
    interval = st.selectbox("Bar interval", ["1m","5m","15m","30m","1h","1d"], index=5)
    tolerance = st.number_input("Tolerance around band (price units)", value=0.05, step=0.05, format="%.2f")
    st.divider()
    tv_exchange = st.text_input("TradingView exchange (e.g., NASDAQ, NYSE)", value="NASDAQ")
    st.divider()
    live = st.toggle("Live mode (auto-refresh)", value=False)
    refresh_secs = st.number_input("Refresh every (seconds)", min_value=5, max_value=120, value=15, step=5)
    st.caption("Tip: for live mode use 1m/5m intervals and a small ticker list to avoid rate limits.")

# --------------- Indicator Helpers ----------------
def normalize(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if "Close" in df and isinstance(df["Close"], pd.DataFrame):
        df["Close"] = df["Close"].iloc[:, 0]
    return df

def sma(series: pd.Series, n: int) -> pd.Series:
    return series.rolling(n).mean()

def ema(series: pd.Series, n: int) -> pd.Series:
    return series.ewm(span=n, adjust=False).mean()

def rsi(series: pd.Series, n: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.clip(lower=0)).ewm(alpha=1/n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def adl(df: pd.DataFrame) -> pd.Series:
    high, low, close, vol = df["High"], df["Low"], df["Close"], df["Volume"]
    mfm = ((close - low) - (high - close)) / (high - low)
    mfm = mfm.replace([np.inf, -np.inf], 0).fillna(0)
    return (mfm * vol).cumsum()

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["SMA5"] = sma(df["Close"], 5)
    df["SMA10"] = sma(df["Close"], 10)
    df["SMA20"] = sma(df["Close"], 20)
    stdev = df["Close"].rolling(20).std(ddof=0)
    df["BB_UPPER"] = df["SMA20"] + 2 * stdev
    df["BB_LOWER"] = df["SMA20"] - 2 * stdev
    df["RSI14"] = rsi(df["Close"], 14)
    df["MACD"], df["MACD_SIGNAL"], df["MACD_HIST"] = macd(df["Close"])
    df["ADL"] = adl(df)
    return df

def reason_text(row, signal):
    if signal == "BEARISH":
        return (f"Price at/above upper Bollinger with SMA order 5 > 10 > 20 → "
                f"potential top / bull exhaustion. Target: SMA5 ≈ {row['sma5']:.2f}.")
    return (f"Price at/below lower Bollinger with SMA order 5 < 10 < 20 → "
            f"potential bottom / bear exhaustion. Target: SMA5 ≈ {row['sma5']:.2f}.")

def check_setup_lastbar(df: pd.DataFrame, tol: float = 0.0):
    last = df.dropna().iloc[-1] if len(df.dropna()) else None
    if last is None:
        return None
    c, s5, s10, s20, up, lo = float(last["Close"]), float(last["SMA5"]), float(last["SMA10"]), float(last["SMA20"]), float(last["BB_UPPER"]), float(last["BB_LOWER"])
    if (s5 > s10 > s20) and (c >= up - tol):
        return "BEARISH"
    if (s5 < s10 < s20) and (c <= lo + tol):
        return "BULLISH"
    return None

# --------------- TradingView embed ----------------
def tradingview_widget(symbol: str, exchange: str = "NASDAQ", height: int = 520, interval: str = "5"):
    """
    Embed a live TradingView chart. interval options: 1,3,5,15,30,60,240,D,W,M
    """
    tvsym = f"{exchange}:{symbol}"
    html(f"""
    <div class="tradingview-widget-container">
      <div id="tv_{symbol}"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
        new TradingView.widget({{
          "container_id": "tv_{symbol}",
          "symbol": "{tvsym}",
          "interval": "{interval}",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "hide_top_toolbar": false,
          "allow_symbol_change": true,
          "withdateranges": true,
          "studies": [],
          "width": "100%",
          "height": {height}
        }});
      </script>
    </div>
    """, height=height+20)

# --------------- Scan ----------------
def scan(symbols, period, interval, tolerance):
    # yfinance rule: 1m data available only for last ~7 days.
    if interval == "1m" and period not in {"1d","5d","7d"}:
        period = "5d"
    rows = []
    for sym in symbols:
        try:
            df = yf.download(sym, period=period, interval=interval, progress=False, auto_adjust=True)
            if df is None or df.empty:
                continue
            df = normalize(df)
            df = compute_indicators(df)
            sig = check_setup_lastbar(df, tol=tolerance)
            if sig:
                last = df.dropna().iloc[-1]
                rows.append(dict(
                    symbol=sym, signal=sig, time=str(last.name),
                    close=float(last["Close"]),
                    sma5=float(last["SMA5"]), sma10=float(last["SMA10"]), sma20=float(last["SMA20"]),
                    bb_upper=float(last["BB_UPPER"]), bb_lower=float(last["BB_LOWER"]),
                    rsi14=float(last["RSI14"])
                ))
        except Exception as e:
            st.warning(f"{sym}: {e}")
    if not rows:
        return pd.DataFrame(columns=[
            "symbol","signal","time","close","sma5","sma10","sma20","bb_upper","bb_lower","rsi14"
        ])
    out = pd.DataFrame(rows)
    out["distance_to_sma5"] = (out["close"] - out["sma5"]).abs()
    out["distance_to_sma5_pct"] = (out["distance_to_sma5"] / out["close"]) * 100
    return out

# --------------- Charts ----------------
def plot_chart(df: pd.DataFrame, sym: str):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 4))
    dfp = df.dropna().iloc[-200:]
    ax.plot(dfp.index, dfp["Close"], label="Close")
    ax.plot(dfp.index, dfp["SMA5"], label="SMA5")
    ax.plot(dfp.index, dfp["SMA10"], label="SMA10")
    ax.plot(dfp.index, dfp["SMA20"], label="SMA20")
    ax.plot(dfp.index, dfp["BB_UPPER"], label="BB Upper", linestyle="--")
    ax.plot(dfp.index, dfp["BB_LOWER"], label="BB Lower", linestyle="--")
    ax.set_title(f"{sym} — Price, SMA5/10/20, Bollinger(20,2)")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.2)
    st.pyplot(fig)

def plot_indicators(df: pd.DataFrame, sym: str):
    import matplotlib.pyplot as plt
    dfi = df.dropna().iloc[-200:]
    # RSI
    fig1, ax1 = plt.subplots(figsize=(10, 2.8))
    ax1.plot(dfi.index, dfi["RSI14"], label="RSI(14)")
    ax1.axhline(70, linestyle="--", linewidth=1)
    ax1.axhline(30, linestyle="--", linewidth=1)
    ax1.set_title(f"{sym} — RSI(14)")
    ax1.grid(True, alpha=0.2)
    st.pyplot(fig1)
    # MACD
    fig2, ax2 = plt.subplots(figsize=(10, 2.8))
    macd_line, signal_line, hist = macd(dfi["Close"])
    ax2.plot(dfi.index, macd_line, label="MACD")
    ax2.plot(dfi.index, signal_line, label="Signal")
    ax2.bar(dfi.index, hist, label="Hist")
    ax2.set_title(f"{sym} — MACD(12,26,9)")
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.2)
    st.pyplot(fig2)
    # ADL
    fig3, ax3 = plt.subplots(figsize=(10, 2.8))
    ax3.plot(dfi.index, adl(dfi), label="ADL")
    ax3.set_title(f"{sym} — Accumulation/Distribution Line")
    ax3.grid(True, alpha=0.2)
    st.pyplot(fig3)

# --------------- UI ----------------
syms = [s.strip().upper() for s in tickers.split(",") if s.strip()]
df = scan(syms, period, interval, tolerance)

st.subheader("Results")
if df.empty:
    st.info("No setups found for the current list and settings. Try 1m/5m or add tolerance.")
else:
    st.dataframe(
        df[["symbol","signal","time","close","sma5","sma10","sma20","bb_upper","bb_lower","rsi14","distance_to_sma5_pct"]]
          .sort_values(["signal","symbol"]).reset_index(drop=True),
        use_container_width=True
    )
    st.markdown("### Details")
    for _, row in df.sort_values(["signal","symbol"]).iterrows():
        sym = row["symbol"]
        with st.expander(f"{sym} — {row['signal']}  |  Close {row['close']:.2f}  |  RSI(14) {row['rsi14']:.1f}%"):
            st.write(reason_text(row, row["signal"]))
            tab1, tab2 = st.tabs(["Built-in charts", "TradingView (live)"])
            # Built-in charts
            with tab1:
                try:
                    raw = yf.download(sym, period=period, interval=interval, progress=False, auto_adjust=True)
                    raw = normalize(raw)
                    raw = compute_indicators(raw)
                    plot_chart(raw, sym)
                    plot_indicators(raw, sym)
                except Exception as ex:
                    st.warning(f"Could not render built-in charts for {sym}: {ex}")
            # TradingView
            with tab2:
                st.caption(f"Live TradingView — {tv_exchange}:{sym}")
                tradingview_widget(sym, exchange=tv_exchange, interval="5", height=520)
                st.link_button("Open in TradingView", f"https://www.tradingview.com/chart/?symbol={tv_exchange}%3A{sym}")

# ----- LIVE MODE -----
if live:
    st.toast(f"Live mode: auto-refreshing every {int(refresh_secs)}s", icon="⏱️")
    time.sleep(int(refresh_secs))
    st.rerun()
