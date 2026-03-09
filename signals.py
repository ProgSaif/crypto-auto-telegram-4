# signals.py
import requests
import pandas as pd
import talib

# --- Fetch candle data from Binance ---
def get_klines(symbol, interval="5m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        resp = requests.get(url, timeout=10).json()
        df = pd.DataFrame(resp, columns=[
            "open_time","open","high","low","close","volume","close_time",
            "quote_asset_volume","number_of_trades","taker_buy_base","taker_buy_quote","ignore"
        ])
        df = df.astype({
            "open":"float","high":"float","low":"float","close":"float","volume":"float"
        })
        return df
    except Exception as e:
        print("Failed to fetch klines:", e)
        return None

# --- Calculate ATR ---
def calculate_atr(df, period=14):
    return talib.ATR(df["high"], df["low"], df["close"], timeperiod=period)

# --- Calculate signals ---
def calculate_signal(symbol):
    df = get_klines(symbol, interval="5m", limit=50)
    if df is None or len(df) < 20:
        return None

    # RSI
    rsi = talib.RSI(df["close"], timeperiod=14).iloc[-1]

    # EMA trend
    ema_fast = talib.EMA(df["close"], timeperiod=12).iloc[-1]
    ema_slow = talib.EMA(df["close"], timeperiod=26).iloc[-1]

    # Volume spike
    avg_volume = df["volume"].rolling(20).mean().iloc[-2]
    volume_spike = df["volume"].iloc[-1] > 1.5 * avg_volume

    # ATR for SL/TP calculation
    atr = calculate_atr(df).iloc[-1]

    last_price = df["close"].iloc[-1]

    # High-quality filter thresholds
    if rsi < 35 and ema_fast > ema_slow and volume_spike:
        trade_type = "LONG"
    elif rsi > 65 and ema_fast < ema_slow and volume_spike:
        trade_type = "SHORT"
    else:
        return None

    # Auto-adjusted TP/SL
    if trade_type == "LONG":
        entry = last_price
        sl = entry - atr
        tp1 = entry + atr * 1
        tp2 = entry + atr * 2
        tp3 = entry + atr * 3
    else:
        entry = last_price
        sl = entry + atr
        tp1 = entry - atr * 1
        tp2 = entry - atr * 2
        tp3 = entry - atr * 3

    confidence = int(abs(rsi-50) + (50 if volume_spike else 0))

    return {
        "coin": symbol.replace("USDT",""),
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "trade_type": trade_type,
        "confidence": confidence
    }

# --- Top USDT coins ---
TOP_COINS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","ADAUSDT",
    "XRPUSDT","DOGEUSDT","LTCUSDT","AVAXUSDT","DOTUSDT"
]

def get_signals():
    signals = []
    for sym in TOP_COINS:
        s = calculate_signal(sym)
        if s:
            signals.append(s)
    return signals

# --- New Listings ---
def get_new_listings():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        data = requests.get(url, timeout=10).json()
        symbols = [s["symbol"] for s in data.get("symbols", []) if s["quoteAsset"]=="USDT" and s["status"]=="TRADING"]
        return symbols[-5:]  # latest 5
    except:
        return []

# --- Gainers / Losers ---
def get_gainers_losers(top_n=5):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    try:
        data = requests.get(url, timeout=10).json()
        usdt_pairs = [x for x in data if x["symbol"].endswith("USDT")]
        gainers = sorted(usdt_pairs, key=lambda x: float(x["priceChangePercent"]), reverse=True)[:top_n]
        losers = sorted(usdt_pairs, key=lambda x: float(x["priceChangePercent"]))[:top_n]
        return gainers, losers
    except:
        return [], []
