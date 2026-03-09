def calculate_rsi(df, period=RSI_PERIOD):
    if df is None or df.empty:
        return None
    delta = df["close"].diff()
    gain = np.where(delta>0, delta, 0)
    loss = np.where(delta<0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else None

def calculate_ema_trend(df, fast=EMA_FAST, slow=EMA_SLOW):
    if df is None or df.empty:
        return None
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        return "up"
    elif ema_fast.iloc[-1] < ema_slow.iloc[-1]:
        return "down"
    else:
        return "flat"

def calculate_atr(df, period=14):
    if df is None or df.empty:
        return None
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    tr = pd.DataFrame({"hl": high_low, "hc": high_close, "lc": low_close}).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr.iloc[-1] if not atr.empty else None

def detect_volume_spike(df, multiplier=VOLUME_MULTIPLIER):
    if df is None or df.empty:
        return False
    avg_volume = df["volume"].rolling(20).mean()
    current_volume = df["volume"].iloc[-1]
    if pd.isna(avg_volume.iloc[-1]):
        return False
    return current_volume > (avg_volume.iloc[-1] * multiplier)
