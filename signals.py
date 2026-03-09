import pandas as pd
import numpy as np
import requests
import time

# ===== PARAMETERS =====
EMA_FAST = 9
EMA_SLOW = 21
RSI_PERIOD = 14

PRICE_MOVE_THRESHOLD = 0.005
VOLUME_MULTIPLIER = 1.5
RSI_LONG_MAX = 90
RSI_SHORT_MIN = 10

CONFIDENCE_THRESHOLD = 10
MIN_DAILY_VOLUME = 100000

ATR_MULTIPLIER = 3
MIN_MOVE_PERCENT = 0.006   # 0.6% minimum move

# ===== GET KLINES =====
def get_klines(symbol, interval="5m", limit=200, retries=3):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"

    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()

            if not isinstance(data, list) or len(data) == 0:
                raise ValueError("Empty response")

            df = pd.DataFrame(data, columns=[
                "open_time","open","high","low","close",
                "volume","close_time","quote_asset_volume",
                "trades","taker_base","taker_quote","ignore"
            ])

            df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)

            return df

        except Exception as e:
            print(f"Attempt {attempt+1} failed for {symbol}: {e}")
            time.sleep(2)

    return None


# ===== RSI =====
def calculate_rsi(df, period=RSI_PERIOD):

    if df is None or len(df) < period:
        return None

    delta = df["close"].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


# ===== EMA TREND =====
def calculate_ema_trend(df):

    ema_fast = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    ema_slow = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()

    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        return "up"

    elif ema_fast.iloc[-1] < ema_slow.iloc[-1]:
        return "down"

    return "flat"


# ===== ATR =====
def calculate_atr(df, period=14):

    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()

    return atr.iloc[-1]


# ===== VOLUME SPIKE =====
def detect_volume_spike(df):

    avg_volume = df["volume"].rolling(20).mean()

    current_volume = df["volume"].iloc[-1]

    return current_volume > avg_volume.iloc[-1] * VOLUME_MULTIPLIER


# ===== SIGNAL ENGINE =====
def calculate_signal(symbol, last_price, change_pct, df, daily_volume):

    if df is None or daily_volume < MIN_DAILY_VOLUME:
        return None

    rsi = calculate_rsi(df)
    trend = calculate_ema_trend(df)
    volume_spike = detect_volume_spike(df)

    # ATR from higher timeframe
    df_1h = get_klines(symbol, "1h", 200)

    atr = calculate_atr(df_1h)

    if atr is None:
        atr = last_price * 0.01

    # Prevent tiny TP/SL
    atr = max(atr, last_price * MIN_MOVE_PERCENT)

    print(f"{symbol} -> RSI:{rsi} Trend:{trend} VolSpike:{volume_spike} Change:{change_pct}")

    trade_type = None

    if change_pct > PRICE_MOVE_THRESHOLD and trend == "up" and volume_spike:
        trade_type = "LONG"

    elif change_pct < -PRICE_MOVE_THRESHOLD and trend == "down" and volume_spike:
        trade_type = "SHORT"

    if not trade_type:
        return None


    entry = last_price

    if trade_type == "LONG":

        sl = entry - atr * ATR_MULTIPLIER

        tp1 = entry + atr * ATR_MULTIPLIER
        tp2 = entry + atr * ATR_MULTIPLIER * 2
        tp3 = entry + atr * ATR_MULTIPLIER * 3

    else:

        sl = entry + atr * ATR_MULTIPLIER

        tp1 = entry - atr * ATR_MULTIPLIER
        tp2 = entry - atr * ATR_MULTIPLIER * 2
        tp3 = entry - atr * ATR_MULTIPLIER * 3


    confidence = int(abs(change_pct) * 100)

    if volume_spike:
        confidence += 20

    confidence = min(confidence, 100)

    if confidence < CONFIDENCE_THRESHOLD:
        return None


    return {
        "coin": symbol.replace("USDT",""),
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "trade_type": trade_type,
        "confidence": confidence,
        "rsi": rsi,
        "ema_trend": trend,
        "volume_spike": volume_spike,
        "atr": atr
    }
