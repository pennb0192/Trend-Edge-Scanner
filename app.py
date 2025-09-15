# app.py  — Trend Edge Scanner (auth + RSI/MACD/ADL scanner w/ charts)

import json
import math
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Trend Edge Scanner", layout="wide")

# -------------------- BOOT LOG --------------------
st.write("BOOT 1: app.py loaded")

# -------------------- Load & prepare secrets --------------------
try:
    # Expected in Streamlit Cloud "Secrets":
    # [credentials.usernames.<youruser>]
    # email = "you@example.com"
    # name = "Your Name"
    # password = "$2b$12$....."   (bcrypt hash)
    #
    # [cookie]
    # name = "trend_edge_auth"
    # key = "any_random_string"
    # expiry_days = 30
    sec = st.secrets

    src_users = sec["credentials"]["usernames"]
    usernames = {u: dict(src_users[u]) for u in src_users}   # detach from Secrets object
    credentials = {"usernames": usernames}

    cookie_cfg = sec["cookie"]
    cookie_name = cookie_cfg.get("name", "trend_edge_auth")
    cookie_key = cookie_cfg.get("key", "replace_me")
    cookie_days = int(cookie_cfg.get("expiry_days", 30))

    st.write("BOOT 2: secrets loaded")
    st.json({"credentials": "ok", "cookie": "ok"})
    st.write("BOOT 3: credentials & cookie prepared")
except Exception as e:
    st.error("ERROR loading/preparing secrets")
    st.exception(e)
    st.stop()

# -------------------- Authenticator --------------------
try:
    import streamlit_authenticator as stauth

    st.write("BOOT 4: streamlit_authenticator imported")
    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        cookie_key,
        cookie_days,
    )
    st.write("BOOT 5: authenticator created")
except Exception as e:
    st.error("ERROR creating authenticator")
    st.exception(e)
    st.stop()

# ------------- Login UI -------------
try:
    # pass location only once
    login_result = authenticator.login("Login", location="main")  # v0.4.x returns None until submit

    # If the user hasn't pressed the Login button yet, stop rendering here
    if login_result is None:
        st.stop()

    # After submit, unpack the tuple
    name, auth_status, username = login_result

    if auth_status is False:
        st.error("Username/password is incorrect.")
        st.stop()
    elif auth_status is None:
        st.warning("Please enter your username and password.")
        st.stop()
    else:
        st.success(f"Welcome, {name}! ✅ You are logged in as {username}")

except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# -------------------- Main app (only if logged in) --------------------
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}! ✅ You are logged in as {username}")
    st.title("Trend Edge Scanner")

    # -------- Sidebar controls --------
    with st.sidebar:
        st.subheader("Scan Settings")
        tickers_input = st.text_area(
            "Tickers (comma or space separated)",
            value="AAPL, MSFT, NVDA, TSLA, META",
            height=100,
        )
        tickers = sorted(
            {t.strip().upper() for t in tickers_input.replace("\n", " ").replace(",", " ").split() if t.strip()}
        )

        period = st.selectbox("History window", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
        interval = st.selectbox("Candle interval", ["1d", "1h", "30m", "15m"], index=0)

        st.caption("Signals: Bullish = MACD>Signal & RSI>55 & Close>EMA50; Bearish = MACD<Signal & RSI<45 & Close<EMA50.")
        run_btn = st.button("Run Scan")

    # -------- Data helpers (no extra TA libs required) --------
    @st.cache_data(show_spinner=False)
    def load_ohlcv(ticker: str, period: str, interval: str) -> pd.DataFrame:
        import yfinance as yf

        df = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
        if df.empty:
            return df
        df = df.rename(
            columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Adj Close": "adj_close", "Volume": "volume"}
        )
        df.dropna(inplace=True)
        return df

    def ema(series: pd.Series, span: int) -> pd.Series:
        return series.ewm(span=span, adjust=False).mean()

    def rsi(series: pd.Series, length: int = 14) -> pd.Series:
        delta = series.diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)
        avg_gain = gain.ewm(alpha=1/length, min_periods=length, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/length, min_periods=length, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi_val = 100 - (100 / (1 + rs))
        return rsi_val

    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        macd_line = ema(series, fast) - ema(series, slow)
        signal_line = ema(macd_line, signal)
        hist = macd_line - signal_line
        return macd_line, signal_line, hist

    def adl(df: pd.DataFrame) -> pd.Series:
        # Accumulation/Distribution Line
        mfm = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"]).replace(0, np.nan)
        mfv = mfm * df["volume"]
        return mfv.cumsum()

    def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["ema20"] = ema(out["close"], 20)
        out["ema50"] = ema(out["close"], 50)
        out["rsi14"] = rsi(out["close"], 14)
        out["macd"], out["macd_signal"], out["macd_hist"] = macd(out["close"])
        out["adl"] = adl(out)
        return out

    def classify_row(row) -> str:
        try:
            bullish = (row["macd"] > row["macd_signal"]) and (row["rsi14"] > 55) and (row["close"] > row["ema50"])
            bearish = (row["macd"] < row["macd_signal"]) and (row["rsi14"] < 45) and (row["close"] < row["ema50"])
            if bullish:
                return "Bullish"
            if bearish:
                return "Bearish"
            return "Neutral"
        except Exception:
            return "Neutral"

    def analyze_ticker(ticker: str, period: str, interval: str):
        df = load_ohlcv(ticker, period, interval)
        if df.empty:
            return None, None
        df = compute_indicators(df)
        last = df.iloc[-1]
        summary = {
            "Ticker": ticker,
            "Close": round(float(last["close"]), 2),
            "RSI(14)": round(float(last["rsi14"]), 2),
            "MACD": round(float(last["macd"]), 4),
            "Signal": round(float(last["macd_signal"]), 4),
            "MACD Hist": round(float(last["macd_hist"]), 4),
            "EMA50": round(float(last["ema50"]), 2),
            "SignalClass": classify_row(last),
        }
        return df, summary

    # -------- Run scan --------
    if run_btn and tickers:
        results = []
        per_ticker_frames = {}

        with st.spinner("Scanning tickers..."):
            for t in tickers:
                df, summary = analyze_ticker(t, period, interval)
                if summary is not None:
                    results.append(summary)
                    per_ticker_frames[t] = df

        if not results:
            st.warning("No data returned. Try a different period/interval or check ticker symbols.")
            st.stop()

        # -------- Results table --------
        res_df = pd.DataFrame(results).set_index("Ticker")
        # Order by signal, then strongest MACD hist
        ordering = pd.Categorical(res_df["SignalClass"], categories=["Bullish", "Neutral", "Bearish"], ordered=True)
        res_df = res_df.assign(_order=ordering).sort_values(by=["_order", "MACD Hist"], ascending=[True, False]).drop(columns="_order")

        st.subheader("Scan Results")
        st.dataframe(res_df, use_container_width=True)

        # -------- Charts --------
        st.subheader("Charts")
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        for t in res_df.index:
            df = per_ticker_frames[t].copy()
            df = df.tail(180)  # keep plot readable

            # Build 3-row chart: Price/EMA + MACD + RSI
            fig = make_subplots(
                rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                row_heights=[0.55, 0.25, 0.20],
                specs=[[{"type": "xy"}], [{"type": "xy"}], [{"type": "xy"}]]
            )

            # Candles
            fig.add_trace(
                go.Candlestick(
                    x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"],
                    name="Price"
                ),
                row=1, col=1
            )
            # EMAs
            fig.add_trace(go.Scatter(x=df.index, y=df["ema20"], mode="lines", name="EMA20"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["ema50"], mode="lines", name="EMA50"), row=1, col=1)

            # MACD
            fig.add_trace(go.Scatter(x=df.index, y=df["macd"], mode="lines", name="MACD"), row=2, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["macd_signal"], mode="lines", name="Signal"), row=2, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df["macd_hist"], name="Hist"), row=2, col=1)

            # RSI
            fig.add_trace(go.Scatter(x=df.index, y=df["rsi14"], mode="lines", name="RSI(14)"), row=3, col=1)
            fig.add_hline(y=70, line_dash="dot", row=3, col=1)
            fig.add_hline(y=30, line_dash="dot", row=3, col=1)

            fig.update_layout(
                title=f"{t} — {res_df.loc[t, 'SignalClass']}  |  Close: {res_df.loc[t, 'Close']}",
                xaxis_rangeslider_visible=False,
                height=700,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        # Initial instructions screen (before pressing Run)
        st.info("Enter tickers in the sidebar and click **Run Scan** to analyze RSI, MACD, ADL, and view charts.")

elif auth_status is False:
    st.error("Username/password is incorrect.")
else:
    st.info("Please log in.")
