import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from signals import calculate_signal
import mplfinance as mpf
import os
import time

# Ensure charts folder exists
if not os.path.exists("charts"):
    os.makedirs("charts")

TOP_SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","XRPUSDT","SOLUSDT",
               "ADAUSDT","MATICUSDT","DOGEUSDT","LTCUSDT","DOTUSDT","OPNUSDT","ROBOUSDT"]

def get_klines(symbol, interval="1m", limit=50):
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        data = requests.get(url, params=params, timeout=10).json()
        df = pd.DataFrame(data, columns=[
            "OpenTime","Open","High","Low","Close","Volume",
            "CloseTime","QuoteAssetVolume","NumberOfTrades",
            "TakerBuyBase","TakerBuyQuote","Ignore"
        ])
        df["Open"] = df["Open"].astype(float)
        df["High"] = df["High"].astype(float)
        df["Low"] = df["Low"].astype(float)
        df["Close"] = df["Close"].astype(float)
        df["Volume"] = df["Volume"].astype(float)
        df.index = pd.to_datetime(df["OpenTime"], unit='ms')
        return df
    except Exception as e:
        print(f"Klines fetch error {symbol}: {e}")
        return pd.DataFrame()

def detect_signals():
    signals = []

    for symbol in TOP_SYMBOLS:
        df = get_klines(symbol)
        if df.empty or len(df) < 20:
            continue

        # RSI
        rsi = RSIIndicator(df['Close'], window=14).rsi().iloc[-1]

        # EMA trend
        ema20 = EMAIndicator(df['Close'], window=20).ema_indicator().iloc[-1]
        ema50 = EMAIndicator(df['Close'], window=50).ema_indicator().iloc[-1]
        ema_trend = "Bullish" if ema20 > ema50 else "Bearish"

        # Volume spike
        avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
        vol_spike = df['Volume'].iloc[-1] > avg_vol * 1.5

        # Price change
        change_pct = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
        last_price = df['Close'].iloc[-1]

        # Signal
        signal = calculate_signal(symbol, last_price, change_pct, rsi, ema_trend, vol_spike)
        if signal:
            chart_file = f"charts/{symbol}.png"
            try:
                mpf.plot(df, type='candle', style='yahoo', volume=True,
                         savefig=dict(fname=chart_file, dpi=100, bbox_inches="tight"))
            except Exception as e:
                print(f"Chart generation error for {symbol}: {e}")
                chart_file = None
            signal['chart_file'] = chart_file
            signals.append(signal)

        print(f"Scanned {symbol}: price={last_price:.4f}, change={change_pct:.4f}%, RSI={rsi:.2f}, EMA={ema_trend}, VolSpike={vol_spike}")

        time.sleep(0.2)  # avoid hitting Binance too fast

    return signals
