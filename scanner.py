import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from signals import calculate_signal
import time

def get_all_usdt_symbols():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    try:
        data = requests.get(url, timeout=10).json()
        symbols = [item['symbol'] for item in data if item['symbol'].endswith("USDT")]
        return symbols
    except Exception as e:
        print("Failed to fetch all symbols:", e)
        return []

def get_klines(symbol, interval="1m", limit=50):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        data = requests.get(url, params=params, timeout=10).json()
        df = pd.DataFrame(data, columns=[
            "OpenTime","Open","High","Low","Close","Volume",
            "CloseTime","QuoteAssetVolume","NumberOfTrades",
            "TakerBuyBase","TakerBuyQuote","Ignore"
        ])
        df["Close"] = df["Close"].astype(float)
        df["Volume"] = df["Volume"].astype(float)
        df.index = pd.to_datetime(df["OpenTime"], unit='ms')
        return df
    except Exception as e:
        print(f"Klines fetch error {symbol}: {e}")
        return pd.DataFrame()

def detect_signals():
    signals = []
    symbols = get_all_usdt_symbols()
    print(f"Scanning {len(symbols)} USDT pairs...")

    for symbol in symbols:
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
        change_pct = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]
        last_price = df['Close'].iloc[-1]

        # Signal
        signal = calculate_signal(symbol, last_price, change_pct, rsi, ema_trend, vol_spike)
        if signal:
            signals.append(signal)

        # Debug
        print(f"{symbol}: price={last_price:.4f}, change={change_pct:.5f}, RSI={rsi:.2f}, EMA={ema_trend}, VolSpike={vol_spike}")

        time.sleep(0.2)  # avoid hitting Binance too fast

    return signals
