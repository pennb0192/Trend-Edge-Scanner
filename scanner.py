#!/usr/bin/env python3
"""
1:1 Trading Rule - Trend Edge Scanner
Scans tickers for:
- Bearish setup: SMA5 > SMA10 > SMA20 AND close >= Upper Bollinger(20, 2)
- Bullish setup: SMA5 < SMA10 < SMA20 AND close <= Lower Bollinger(20, 2)
"""

import argparse
from dataclasses import dataclass
from typing import List, Optional
import sys
import numpy as np
import pandas as pd

try:
    import yfinance as yf
except Exception as e:
    print("yfinance is required. Install with: pip install yfinance", file=sys.stderr)
    raise

# -------------------- Helpers --------------------
def _normalize_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten MultiIndex columns and ensure Close is a Series."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if "Close" in df and isinstance(df["Close"], (pd.DataFrame,)):
        df["Close"] = df["Close"].iloc[:, 0]
    return df

@dataclass
class ScanResult:
    symbol: str
    side: str  # 'BULLISH' or 'BEARISH'
    close: float
    sma5: float
    sma10: float
    sma20: float
    bb_upper: float
    bb_lower: float
    distance_to_target: float
    distance_to_target_pct: float
    condition_met_on: str

# -------------------- Indicators --------------------
def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if "Close" not in df:
        raise ValueError("Downloaded data missing 'Close' column.")
    if isinstance(df["Close"], (pd.DataFrame,)):
        df["Close"] = df["Close"].iloc[:, 0]

    df["SMA5"] = df["Close"].rolling(5).mean()
    df["SMA10"] = df["Close"].rolling(10).mean()
    df["SMA20"] = df["Close"].rolling(20).mean()

    stdev = df["Close"].rolling(20).std(ddof=0)
    df["BB_UPPER"] = df["SMA20"] + 2 * stdev
    df["BB_LOWER"] = df["SMA20"] - 2 * stdev
    return df

# -------------------- Setup Check --------------------
def check_setups(df: pd.DataFrame, symbol: str, tolerance: float = 0.0) -> Optional[ScanResult]:
    if df.empty:
        return None
    last = df.dropna().iloc[-1]
    if last.isnull().any():
        return None

    c = float(last["Close"])
    s5 = float(last["SMA5"])
    s10 = float(last["SMA10"])
    s20 = float(last["SMA20"])
    up = float(last["BB_UPPER"])
    lo = float(last["BB_LOWER"])
    ts = str(last.name)

    # Bearish setup
    if (s5 > s10 > s20) and (c >= up - tolerance):
        dist = abs(c - s5)
        pct = (dist / c) * 100 if c != 0 else 0.0
        return ScanResult(symbol, "BEARISH", c, s5, s10, s20, up, lo, dist, pct, ts)

    # Bullish setup
    if (s5 < s10 < s20) and (c <= lo + tolerance):
        dist = abs(c - s5)
        pct = (dist / c) * 100 if c != 0 else 0.0
        return ScanResult(symbol, "BULLISH", c, s5, s10, s20, up, lo, dist, pct, ts)

    return None

# -------------------- Scanner --------------------
def scan_symbols(symbols: List[str], period: str = "6mo", interval: str = "1d", tolerance: float = 0.0) -> pd.DataFrame:
    rows = []
    for sym in symbols:
        try:
            df = yf.download(sym, period=period, interval=interval, progress=False, auto_adjust=True)
            if df is None or df.empty:
                continue
            df = _normalize_prices(df)
            df = compute_indicators(df)
            res = check_setups(df, sym, tolerance=tolerance)
            if res:
                rows.append({
                    "symbol": res.symbol,
                    "signal": res.side,
                    "time": res.condition_met_on,
                    "close": round(res.close, 4),
                    "sma5": round(res.sma5, 4),
                    "sma10": round(res.sma10, 4),
                    "sma20": round(res.sma20, 4),
                    "bb_upper": round(res.bb_upper, 4),
                    "bb_lower": round(res.bb_lower, 4),
                    "target_sma5": round(res.sma5, 4),
                    "distance_to_target": round(res.distance_to_target, 4),
                    "distance_to_target_pct": round(res.distance_to_target_pct, 3),
                })
        except Exception as e:
            print(f"[WARN] {sym}: {e}", file=sys.stderr)
            continue

    if not rows:
        return pd.DataFrame(columns=[
            "symbol","signal","time","close","sma5","sma10","sma20","bb_upper","bb_lower",
            "target_sma5","distance_to_target","distance_to_target_pct"
        ])
    return pd.DataFrame(rows).sort_values(["signal","symbol"]).reset_index(drop=True)

# -------------------- CLI --------------------
def parse_args():
    p = argparse.ArgumentParser(description="Scan tickers for 1:1 Rule trend-edge setups (SMA5/10/20 + Bollinger).")
    p.add_argument("-s", "--symbols", type=str, required=True,
                   help='Comma-separated tickers (e.g. "SPY,AAPL,MSFT").')
    p.add_argument("--period", type=str, default="6mo",
                   help="History period (e.g. 3mo, 6mo, 1y). Default=6mo")
    p.add_argument("--interval", type=str, default="1d",
                   help="Bar interval (e.g. 1d, 1h, 15m). Default=1d")
    p.add_argument("--tolerance", type=float, default=0.0,
                   help="Price tolerance around the Bollinger boundary. Default=0.0")
    p.add_argument("--csv", type=str, default="",
                   help="If set, saves results to CSV path.")
    return p.parse_args()

def main():
    args = parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    if not symbols:
        print("No symbols provided.", file=sys.stderr)
        sys.exit(1)
    df = scan_symbols(symbols, period=args.period, interval=args.interval, tolerance=args.tolerance)
    if df.empty:
        print("No setups found for the given symbols/timeframe.")
    else:
        with pd.option_context("display.max_columns", None, "display.width", 140):
            print(df.to_string(index=False))
        if args.csv:
            df.to_csv(args.csv, index=False)
            print(f"\nSaved results to {args.csv}")

if __name__ == "__main__":
    main()
