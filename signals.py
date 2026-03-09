import requests
import pandas as pd
import numpy as np

# Adjustable parameters
EMA_FAST = 9
EMA_SLOW = 21
RSI_PERIOD = 14
VOLUME_MULTIPLIER = 2  # volume spike detection multiplier
CONFIDENCE_THRESHOLD = 50  # minimum confidence to post
TP_SL_ATR_MULTIPLIER = 1.5  # how much ATR to use for TP/SL


def get_klines(symbol, interval="5m", limit=100):
    """
    Fetch Binance Klines (OHLCV) for the symbol.
    """
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval={interval}&limit={limit}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close",
            "volume", "close_time", "quote_asset_volume",
            "trades", "taker_base", "taker_quote", "ignore"
        ])
        df[["open", "high", "low", "close", "volume"]] = df[["open","high","low","close","volume"]].astype(float)
        return df
    except Exception as e:
        print(f"Failed to fetch klines for {symbol}: {e}")
        return None


def calculate_rsi(df, period=RSI_PERIOD):
    delta = df["close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else None


def calculate_ema_trend(df, fast=EMA_FAST, slow=EMA_SLOW):
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        return "up"
    elif ema_fast.iloc[-1] < ema_slow.iloc[-1]:
        return "down"
    else:
        return "flat"


def calculate_atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    tr = pd.DataFrame({"hl": high_low, "hc": high_close, "lc": low_close}).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr.iloc[-1] if not atr.empty else None


def detect_volume_spike(df, multiplier=VOLUME_MULTIPLIER):
    avg_volume = df["volume"].rolling(20).mean()
    current_volume = df["volume"].iloc[-1]
    return current_volume > (avg_volume.iloc[-1] * multiplier)


def calculate_signal(coin, last_price, change_pct, df):
    """
    Generate signal with RSI, EMA, volume spike, and TP/SL based on ATR
    """
    # Calculate indicators
    rsi = calculate_rsi(df)
    ema_trend = calculate_ema_trend(df)
    atr = calculate_atr(df)
    volume_spike = detect_volume_spike(df)

    # Base threshold for % change
    THRESHOLD = 0.01  # 1% change
    trade_type = None

    # LONG condition: price move + EMA trend up + RSI oversold + volume spike
    if change_pct > THRESHOLD and ema_trend == "up" and (rsi is None or rsi < 60) and volume_spike:
        trade_type = "LONG"
    # SHORT condition: price drop + EMA trend down + RSI overbought + volume spike
    elif change_pct < -THRESHOLD and ema_trend == "down" and (rsi is None or rsi > 40) and volume_spike:
        trade_type = "SHORT"

    if not trade_type:
        return None  # do not signal if conditions not met

    # TP / SL based on ATR
    if atr is None:
        atr = last_price * 0.01  # fallback 1% ATR

    if trade_type == "LONG":
        entry = last_price
        sl = entry - atr * TP_SL_ATR_MULTIPLIER
        tp1 = entry + atr * TP_SL_ATR_MULTIPLIER
        tp2 = entry + atr * TP_SL_ATR_MULTIPLIER * 2
        tp3 = entry + atr * TP_SL_ATR_MULTIPLIER * 3
    else:  # SHORT
        entry = last_price
        sl = entry + atr * TP_SL_ATR_MULTIPLIER
        tp1 = entry - atr * TP_SL_ATR_MULTIPLIER
        tp2 = entry - atr * TP_SL_ATR_MULTIPLIER * 2
        tp3 = entry - atr * TP_SL_ATR_MULTIPLIER * 3

    # Confidence scoring
    confidence = int(abs(change_pct)*100) + (20 if volume_spike else 0) + (20 if ema_trend == ("up" if trade_type=="LONG" else "down") else 0)
    confidence = min(confidence, 100)

    return {
        "coin": coin,
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "trade_type": trade_type,
        "confidence": confidence,
        "rsi": rsi,
        "ema_trend": ema_trend,
        "volume_spike": volume_spike,
        "atr": atr
    }
