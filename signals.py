import requests
import pandas as pd
import numpy as np


EMA_FAST = 9
EMA_SLOW = 21
RSI_PERIOD = 14

PRICE_MOVE_THRESHOLD = 0.02
VOLUME_SPIKE_MULTIPLIER = 3

RSI_LONG_MAX = 45
RSI_SHORT_MIN = 55

CONFIDENCE_THRESHOLD = 70
MIN_DAILY_VOLUME = 2000000

ATR_MULTIPLIER = 1.5


def get_klines(symbol, interval="5m", limit=100):

    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"

    try:

        resp = requests.get(url, timeout=10)
        data = resp.json()

        df = pd.DataFrame(data, columns=[
            "open_time","open","high","low","close",
            "volume","close_time","qav",
            "trades","tb","tq","ignore"
        ])

        df[["open","high","low","close","volume"]] = df[
            ["open","high","low","close","volume"]
        ].astype(float)

        return df

    except:
        return None


def calculate_rsi(df):

    delta = df["close"].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(RSI_PERIOD).mean()
    avg_loss = pd.Series(loss).rolling(RSI_PERIOD).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


def ema_trend(df):

    ema_fast = df["close"].ewm(span=EMA_FAST).mean()
    ema_slow = df["close"].ewm(span=EMA_SLOW).mean()

    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        return "UP"

    if ema_fast.iloc[-1] < ema_slow.iloc[-1]:
        return "DOWN"

    return "FLAT"


def volume_spike(df):

    avg_vol = df["volume"].rolling(20).mean()

    return df["volume"].iloc[-1] > avg_vol.iloc[-1] * VOLUME_SPIKE_MULTIPLIER


def calculate_atr(df, period=14):

    high_low = df["high"] - df["low"]
    high_close = abs(df["high"] - df["close"].shift())
    low_close = abs(df["low"] - df["close"].shift())

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()

    return atr.iloc[-1]


def calculate_signal(symbol, price, change, df, volume, df_htf=None):

    if volume < MIN_DAILY_VOLUME:
        return None

    rsi = calculate_rsi(df)
    trend = ema_trend(df)
    vol_spike = volume_spike(df)
    atr = calculate_atr(df)

    if atr is None:
        atr = price * 0.01

    trade_type = None

    if change > PRICE_MOVE_THRESHOLD and trend == "UP" and rsi < RSI_LONG_MAX and vol_spike:
        trade_type = "LONG"

    if change < -PRICE_MOVE_THRESHOLD and trend == "DOWN" and rsi > RSI_SHORT_MIN and vol_spike:
        trade_type = "SHORT"

    if trade_type is None:
        return None

    if trade_type == "LONG":

        entry = price
        sl = entry - atr * ATR_MULTIPLIER
        tp1 = entry + atr * ATR_MULTIPLIER
        tp2 = entry + atr * ATR_MULTIPLIER * 2
        tp3 = entry + atr * ATR_MULTIPLIER * 3

    else:

        entry = price
        sl = entry + atr * ATR_MULTIPLIER
        tp1 = entry - atr * ATR_MULTIPLIER
        tp2 = entry - atr * ATR_MULTIPLIER * 2
        tp3 = entry - atr * ATR_MULTIPLIER * 3

    confidence = int(abs(change) * 100)

    if vol_spike:
        confidence += 20

    if trend == ("UP" if trade_type == "LONG" else "DOWN"):
        confidence += 20

    confidence = min(confidence, 100)

    if confidence < CONFIDENCE_THRESHOLD:
        return None

    return {

        "coin": symbol.replace("USDT", ""),
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "trade_type": trade_type,
        "confidence": confidence

    }
