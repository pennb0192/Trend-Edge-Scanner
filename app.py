# app.py
import json
import time
from datetime import date, timedelta

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Trend Edge Scanner", layout="wide")

# ----------------- BOOT & AUTH (same as your working flow) -----------------
st.write("BOOT 1: app.py loaded")

# ---------- Load & prepare secrets ----------
try:
    sec = st.secrets  # immutable mapping

    # Make *mutable* copies for streamlit-authenticator
    src_users = sec["credentials"]["usernames"]
    usernames = {u: dict(src_users[u]) for u in src_users}  # plain dict copy
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

# ---------- Import and create authenticator ----------
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

# ---------- Login UI ----------
try:
    auth_result = authenticator.login("Login", "main")  # location ONLY
    if auth_result is None:
        st.stop()
    name, auth_status, username = auth_result
except Exception as e:
    st.error("ERROR during login()")
    st.exception(e)
    st.stop()

# ----------------- APP CONTENT (only after login) -----------------
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome, {name}! ✅ You are logged in as {username}")
    st.title("Trend Edge Scanner")

    # ====== SIDEBAR CONTROLS ======
    with st.sidebar:
        st.header("Scan Settings")
        raw = st.text_area(
            "Tickers (comma/space/newline separated)",
            value="AAPL, MSFT, NVDA, TSLA, AMZN, META",
            height=100,
        )
        # clean tickers
        tickers = sorted(
            list(
                {
                    t.strip().upper()
                    for chunk in raw.replace(",", " ").split()
                    if (t := chunk.strip())
                }
            )
        )

        col = st.columns(2)
        with col[0]:
            start = st.date_input("Start date", value=date.today() - timedelta(days=365))
        with col[1]:
            end = st.date_input("End date", value=date.today())

        interval = st.selectbox(
            "Interval",
            options=["1d", "1h", "30m", "15m"],
            index=0,
            help="Data granularity for indicators & charts",
        )

        st.markdown("---")
        st.subheader("Indicators")
        rsi_len = st.number_input("RSI length", min_value=2, max_value=100, value=14, step=1)
        macd_fast = st.number_input("MACD fast", min_value=2, max_value=50, value=12, step=1)
        macd_slow = st.number_input("MACD slow", min_value=5, max_value=200, value=26, step=1)
        macd_signal = st.number_input("MACD signal", min_value=2, max_value=50, value=9, step=1)
        sma_len = st.number_input("Trend SMA", min_value=2, max_value=250, value=50, step=1)

        st.markdown("---")
        st.subheader("Signals")
        rsi_buy = st.slider("RSI oversold (≤)", min_value=5, max_value=60, value=30)
        rsi_sell = st.slider("RSI overbought (≥)", min_value=40, max_value=95, value=70)

        run = st.button("Run Scanner", use_container_width=True)

    # ====== DATA & INDICATORS ======
    @st.cache_data(show_spinner=False)
    def load_prices(tickers, start, end, interval):
        import yfinance as yf

        data = {}
        for t in tickers:
            try:
                df = yf.download(
                    t, start=start, end=end + timedelta(days=1), interval=interval, auto_adjust=False, progress=False
                )
                if isinstance(df.columns, pd.MultiIndex):  # in case of multi-level columns
                    df.columns = [c[0] for c in df.columns]
                df = df.rename(columns=str.title)  # Open, High, Low, Close, Adj Close, Volume
                df.dropna(how="any", inplace=True)
                if not df.empty:
                    data[t] = df
            except Exception:
                pass
        return data

    def ema(s, n):
        return s.ewm(span=n, adjust=False).mean()

    def rsi(close: pd.Series, n=14):
        delta = close.diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        roll_up = ema(up, n)
        roll_down = ema(down, n)
        rs = roll_up / roll_down.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    def macd(close: pd.Series, fast=12, slow=26, signal=9):
        macd_line = ema(close, fast) - ema(close, slow)
        signal_line = ema(macd_line, signal)
        hist = macd_line - signal_line
        return macd_line, signal_line, hist

    def adl(df: pd.DataFrame):
        # Accumulation/Distribution Line (Chaikin)
        high, low, close, vol = df["High"], df["Low"], df["Close"], df["Volume"]
        clv = ((close - low) - (high - close)) / (high - low).replace(0, np.nan)
        clv = clv.fillna(0.0)
        return (clv * vol).cumsum()

    def sma(close: pd.Series, n=50):
        return close.rolling(n).mean()

    def classify_row(row, rsi_buy=30, rsi_sell=70):
        # Simple rule set combining trend + momentum
        signals = []
        if row["MACD_Hist"] > 0:
            signals.append("MACD↑")
        elif row["MACD_Hist"] < 0:
            signals.append("MACD↓")

        if row["RSI"] <= rsi_buy:
            signals.append("RSI oversold")
        elif row["RSI"] >= rsi_sell:
            signals.append("RSI overbought")

        if row["Price"] > row["SMA"]:
            trend = "Up"
        else:
            trend = "Down"
        signals.append(f"Trend {trend}")

        # headline verdict
        if row["MACD_Hist"] > 0 and row["Price"] > row["SMA"] and row["RSI"] < rsi_sell:
            verdict = "Bullish"
        elif row["MACD_Hist"] < 0 and row["Price"] < row["SMA"] and row["RSI"] > rsi_buy:
            verdict = "Bearish"
        else:
            verdict = "Neutral"
        return verdict, ", ".join(signals)

    # ====== RUN ======
    if run and tickers:
        with st.spinner("Downloading and scanning…"):
            data = load_prices(tuple(tickers), start, end, interval)

        if not data:
            st.warning("No data returned. Check tickers, dates, or interval.")
            st.stop()

        rows = []
        latest_frames = {}

        for t, df in data.items():
            c = df["Close"]
            ind_rsi = rsi(c, rsi_len)
            macd_line, sig_line, hist = macd(c, macd_fast, macd_slow, macd_signal)
            trend_sma = sma(c, sma_len)
            ind_adl = adl(df)

            df_ind = pd.DataFrame(
                {
                    "Close": c,
                    "RSI": ind_rsi,
                    "MACD": macd_line,
                    "Signal": sig_line,
                    "Hist": hist,
                    "SMA": trend_sma,
                    "ADL": ind_adl,
                    "Volume": df["Volume"],
                }
            ).dropna()

            if df_ind.empty:
                continue

            last = df_ind.iloc[-1]
            verdict, note = classify_row(
                {
                    "MACD_Hist": float(last["Hist"]),
                    "RSI": float(last["RSI"]),
                    "Price": float(last["Close"]),
                    "SMA": float(last["SMA"]),
                },
                rsi_buy=rsi_buy,
                rsi_sell=rsi_sell,
            )

            rows.append(
                {
                    "Ticker": t,
                    "Price": round(last["Close"], 2),
                    "RSI": round(last["RSI"], 1),
                    "MACD": round(last["MACD"], 3),
                    "MACD_Signal": round(last["Signal"], 3),
                    "MACD_Hist": round(last["Hist"], 3),
                    "ADL": int(last["ADL"]),
                    f"SMA{sma_len}": round(last["SMA"], 2),
                    "Verdict": verdict,
                    "Notes": note,
                }
            )
            latest_frames[t] = df_ind

        if not rows:
            st.warning("Indicators didn’t have enough history for the chosen period.")
            st.stop()

        # ====== RESULTS TABLE ======
        df_out = pd.DataFrame(rows).set_index("Ticker").sort_values(["Verdict", "MACD_Hist"], ascending=[True, False])
        verdict_order = {"Bullish": 0, "Neutral": 1, "Bearish": 2}
        df_out["VerdictRank"] = df_out["Verdict"].map(verdict_order)
        df_out = df_out.sort_values(["VerdictRank", "MACD_Hist"], ascending=[True, False]).drop(columns=["VerdictRank"])

        st.subheader("Scan Results")
        st.dataframe(
            df_out.style.format(
                {
                    "Price": "{:.2f}",
                    "RSI": "{:.1f}",
                    "MACD": "{:.3f}",
                    "MACD_Signal": "{:.3f}",
                    "MACD_Hist": "{:.3f}",
                    f"SMA{sma_len}": "{:.2f}",
                    "ADL": "{:,}",
                }
            ),
            use_container_width=True,
            height=400,
        )

        st.markdown("---")
        st.subheader("Charts")

        import matplotlib.pyplot as plt

        for t in df_out.index:
            df_ind = latest_frames[t].copy()

            # Price + SMA
            fig1, ax1 = plt.subplots(figsize=(10, 3))
            ax1.plot(df_ind.index, df_ind["Close"], label="Close")
            ax1.plot(df_ind.index, df_ind["SMA"], label=f"SMA{sma_len}")
            ax1.set_title(f"{t} – Price & SMA")
            ax1.legend(loc="best")
            ax1.grid(True, linewidth=0.3)
            st.pyplot(fig1)
            plt.close(fig1)

            # MACD
            fig2, ax2 = plt.subplots(figsize=(10, 2.6))
            ax2.plot(df_ind.index, df_ind["MACD"], label="MACD")
            ax2.plot(df_ind.index, df_ind["Signal"], label="Signal")
            ax2.bar(df_ind.index, df_ind["Hist"], width=0.8, label="Hist")
            ax2.set_title(f"{t} – MACD")
            ax2.legend(loc="best")
            ax2.grid(True, linewidth=0.3)
            st.pyplot(fig2)
            plt.close(fig2)

            # RSI
            fig3, ax3 = plt.subplots(figsize=(10, 2.4))
            ax3.plot(df_ind.index, df_ind["RSI"], label="RSI")
            ax3.axhline(70, linestyle="--", linewidth=0.8)
            ax3.axhline(30, linestyle="--", linewidth=0.8)
            ax3.set_ylim(0, 100)
            ax3.set_title(f"{t} – RSI ({rsi_len})")
            ax3.grid(True, linewidth=0.3)
            ax3.legend(loc="best")
            st.pyplot(fig3)
            plt.close(fig3)

            # ADL
            fig4, ax4 = plt.subplots(figsize=(10, 2.6))
            ax4.plot(df_ind.index, df_ind["ADL"], label="ADL")
            ax4.set_title(f"{t} – Accumulation/Distribution Line")
            ax4.grid(True, linewidth=0.3)
            ax4.legend(loc="best")
            st.pyplot(fig4)
            plt.close(fig4)

else:
    st.info("Please log in.")
