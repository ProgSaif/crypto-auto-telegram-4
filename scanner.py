import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from signals import calculate_signal
import mplfinance as mpf
import os

os.makedirs("charts", exist_ok=True)

def get_market_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "price_change_percentage": "24h"
    }
    response = requests.get(url, params=params, timeout=10)
    return response.json()

def get_ohlcv(coin_id, vs_currency="usd", days=1, interval="minute"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days, "interval": interval}
    data = requests.get(url, params=params, timeout=10).json()
    df = pd.DataFrame(data['prices'], columns=["timestamp","close"])
    df["open"] = df["close"]
    df["high"] = df["close"]
    df["low"] = df["close"]
    df["volume"] = pd.DataFrame(data['total_volumes'])[1]
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def detect_signals():
    data = get_market_data()
    signals = []

    for coin in data:
        coin_id = coin['id']
        symbol = coin['symbol'].upper()
        last_price = coin['current_price']
        change_pct = coin['price_change_percentage_24h'] or 0
        df = get_ohlcv(coin_id, days=1, interval="minute")

        if df.empty or len(df) < 20:
            continue

        # RSI
        rsi = RSIIndicator(df['close'], window=14).rsi().iloc[-1]

        # EMA trend
        ema20 = EMAIndicator(df['close'], window=20).ema_indicator().iloc[-1]
        ema50 = EMAIndicator(df['close'], window=50).ema_indicator().iloc[-1]
        ema_trend = "Bullish" if ema20 > ema50 else "Bearish"

        # Volume spike
        avg_vol = df['volume'].rolling(20).mean().iloc[-1]
        vol_spike = df['volume'].iloc[-1] > avg_vol * 1.5

        signal = calculate_signal(symbol, last_price, change_pct, rsi, ema_trend, vol_spike)
        if signal:
            chart_file = f"charts/{symbol}.png"
            mpf.plot(df, type='candle', style='yahoo', volume=True,
                     savefig=dict(fname=chart_file, dpi=100, bbox_inches="tight"))
            signal['chart_file'] = chart_file
            signals.append(signal)

    return signals
