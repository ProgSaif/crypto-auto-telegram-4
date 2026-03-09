import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from signals import calculate_signal
import mplfinance as mpf

def get_klines(symbol, interval="1m", limit=100):
    url = f"https://api.binance.vision/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=["open_time","open","high","low","close","volume",
                                     "close_time","quote_asset_volume","trades","taker_base",
                                     "taker_quote","ignore"])
    df = df.astype({
        "open":"float","high":"float","low":"float","close":"float","volume":"float"
    })
    return df

def detect_signals():
    url = "https://data-api.binance.vision/api/v3/ticker/24hr"
    response = requests.get(url).json()

    signals = []

    for item in response:
        symbol = item.get("symbol", "")
        if not symbol.endswith("USDT"):
            continue

        coin = symbol.replace("USDT", "")
        change_pct = float(item.get("priceChangePercent", 0))
        last_price = float(item.get("lastPrice", 0))
        volume = float(item.get("volume", 0))

        # fetch candles
        df = get_klines(symbol, interval="5m", limit=50)

        # RSI
        rsi = RSIIndicator(df['close'], window=14).rsi().iloc[-1]

        # EMA trend
        ema20 = EMAIndicator(df['close'], window=20).ema_indicator().iloc[-1]
        ema50 = EMAIndicator(df['close'], window=50).ema_indicator().iloc[-1]
        ema_trend = "Bullish" if ema20 > ema50 else "Bearish"

        # Detect volume spike
        avg_volume = df['volume'].rolling(20).mean().iloc[-1]
        volume_spike = True if volume > avg_volume * 1.5 else False

        # calculate professional signal
        signal = calculate_signal(coin, last_price, change_pct, rsi, ema_trend, volume_spike)
        if signal:
            # save chart
            chart_file = f"charts/{coin}.png"
            mpf.plot(df.set_index(pd.to_datetime(df['open_time'], unit='ms')),
                     type='candle', style='yahoo', volume=True,
                     savefig=dict(fname=chart_file, dpi=100, bbox_inches="tight"))
            signal['chart_file'] = chart_file
            signals.append(signal)

    return signals
