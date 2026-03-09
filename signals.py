import requests
import pandas as pd
import numpy as np

# ===== Adjustable Parameters =====
EMA_FAST = 9
EMA_SLOW = 21
RSI_PERIOD = 14

PRICE_CHANGE_THRESHOLD = 0.03     # 3% price move required
RSI_LONG_MAX = 45                 # LONG only if RSI < 45 (oversold)
RSI_SHORT_MIN = 55                # SHORT only if RSI > 55 (overbought)
VOLUME_MULTIPLIER = 4             # Volume spike must be ≥ 4× average
CONFIDENCE_THRESHOLD = 70
TP_SL_ATR_MULTIPLIER = 1.5
MIN_DAILY_VOLUME = 1000000        # Only scan coins with daily volume ≥ $1M

# Optional: Only scan top coins
TOP_COINS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT",
    "XRPUSDT", "DOGEUSDT", "LTCUSDT", "AVAXUSDT", "DOTUSDT"
]

# ===== Helper Functions =====
def get_klines(symbol, interval="5m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        df = pd.DataFrame(data, columns=[
            "open_time","open","high","low","close",
            "volume","close_time","quote_asset_volume",
            "trades","taker_base","taker_quote","ignore"
        ])
        df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)
        return df
    except Exception as e:
        print(f"Failed to fetch klines for {symbol}: {e}")
        return None

def calculate_rsi(df, period=RSI_PERIOD):
    delta = df["close"].diff()
    gain = np.where(delta>0, delta, 0)
    loss = np.where(delta<0, -delta, 0)
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

# ===== Pro Signal Function =====
def calculate_signal(symbol, last_price, change_pct, df, daily_volume, df_higher_tf=None):
    # Only scan top coins
    if symbol not in TOP_COINS:
        return None

    # Ignore low-liquidity coins
    if daily_volume < MIN_DAILY_VOLUME:
        return None

    # Indicators
    rsi = calculate_rsi(df)
    ema_trend = calculate_ema_trend(df)
    atr = calculate_atr(df)
    volume_spike = detect_volume_spike(df)

    # Higher timeframe trend confirmation
    if df_higher_tf is not None:
        ema_trend_htf = calculate_ema_trend(df_higher_tf)
        if ema_trend_htf != ema_trend:
            return None  # skip counter-trend

    # Signal Logic
    trade_type = None
    if change_pct > PRICE_CHANGE_THRESHOLD and ema_trend == "up" and (rsi is None or rsi < RSI_LONG_MAX) and volume_spike:
        trade_type = "LONG"
    elif change_pct < -PRICE_CHANGE_THRESHOLD and ema_trend == "down" and (rsi is None or rsi > RSI_SHORT_MIN) and volume_spike:
        trade_type = "SHORT"

    if not trade_type:
        return None

    # TP/SL based on ATR
    if atr is None:
        atr = last_price * 0.01  # fallback

    if trade_type == "LONG":
        entry = last_price
        sl = entry - atr * TP_SL_ATR_MULTIPLIER
        tp1 = entry + atr * TP_SL_ATR_MULTIPLIER
        tp2 = entry + atr * TP_SL_ATR_MULTIPLIER * 2
        tp3 = entry + atr * TP_SL_ATR_MULTIPLIER * 3
    else:
        entry = last_price
        sl = entry + atr * TP_SL_ATR_MULTIPLIER
        tp1 = entry - atr * TP_SL_ATR_MULTIPLIER
        tp2 = entry - atr * TP_SL_ATR_MULTIPLIER * 2
        tp3 = entry - atr * TP_SL_ATR_MULTIPLIER * 3

    # Confidence scoring
    confidence = int(abs(change_pct)*100) + (20 if volume_spike else 0) + \
                 (20 if ema_trend == ("up" if trade_type=="LONG" else "down") else 0)
    confidence = min(confidence, 100)

    # Only post if confidence high
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
        "confidence": confidence,
        "rsi": rsi,
        "ema_trend": ema_trend,
        "volume_spike": volume_spike,
        "atr": atr
    }
