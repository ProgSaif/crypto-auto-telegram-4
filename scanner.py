import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from signals import calculate_signal
import mplfinance as mpf
import os

if not os.path.exists("charts"):
    os.makedirs("charts")

def get_market_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "price_change_percentage": "1h,24h"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if not isinstance(data, list):
            print("Unexpected market data:", data)
            return []
        return data
    except Exception as e:
        print("Market data fetch error:", e)
        return []

def get_ohlcv(coin_id, vs_currency="usd", days=1, interval="minute"):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": vs_currency, "days": days, "interval": interval}
        data = requests.get(url, params=params, timeout=10).json()
        if "prices" not in data or "total_volumes" not in data:
            return pd.DataFrame()
        df = pd.DataFrame(data['prices'], columns=["timestamp","close"])
        df["open"] = df["close"]
        df["high"] = df["close"]
        df["low"] = df["close"]
        df["volume"] = pd.DataFrame(data['total_volumes'])[1]
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"OHLCV fetch error for {coin_id}:", e)
        return pd.DataFrame()

def detect_signals():
    market_data = get_market_data()
    signals = []

    for coin in market_data:
        if not isinstance(coin, dict):
            continue
        coin_id = coin.get('id')
        symbol = coin.get('symbol', '').upper()
        last_price = coin.get('current_price', 0)
        change_pct = coin.get('price_change_percentage_24h', 0) or 0

        if not coin_id or not symbol:
            continue

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

        # Calculate signal
        signal = calculate_signal(symbol, last_price, change_pct, rsi, ema_trend, vol_spike)
        if signal:
            chart_file = f"charts/{symbol}.png"
            try:
                mpf.plot(df, type='candle', style='yahoo', volume=True,
                         savefig=dict(fname=chart_file, dpi=100, bbox_inches="tight"))
            except Exception as e:
                print(f"Chart generation error for {symbol}:", e)
                chart_file = None
            signal['chart_file'] = chart_file
            signals.append(signal)

        # Debug log
        print(f"Scanned {symbol}: price={last_price}, change={change_pct:.2f}%, RSI={rsi:.2f}, EMA={ema_trend}, VolSpike={vol_spike}")

    return signals
