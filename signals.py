# signals.py
def calculate_signal(coin, last_price, change_pct, rsi, ema_trend, volume_spike):
    # Test mode: very low thresholds
    if change_pct > 0.001:  # LONG on tiny 0.1% moves
        trade_type = "LONG"
        entry = last_price
        sl = entry - (entry * 0.0005)
        tp1 = entry + (entry * 0.0005)
        tp2 = entry + (entry * 0.001)
        tp3 = entry + (entry * 0.002)
    elif change_pct < -0.001:  # SHORT
        trade_type = "SHORT"
        entry = last_price
        sl = entry + (entry * 0.0005)
        tp1 = entry - (entry * 0.0005)
        tp2 = entry - (entry * 0.001)
        tp3 = entry - (entry * 0.002)
    else:
        return None

    confidence = int(abs(change_pct) * 10000) + (10 if volume_spike else 0)

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
        "volume_spike": volume_spike
    }
