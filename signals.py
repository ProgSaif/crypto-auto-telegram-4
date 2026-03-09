def calculate_signal(coin, last_price, change_pct, rsi, ema_trend, volume_spike):
    # Fast-testing thresholds
    if change_pct > 0.05:  # LONG
        trade_type = "LONG"
        entry = last_price
        sl = entry - (entry * 0.001)
        tp1 = entry + (entry * 0.001)
        tp2 = entry + (entry * 0.002)
        tp3 = entry + (entry * 0.003)
    elif change_pct < -0.05:  # SHORT
        trade_type = "SHORT"
        entry = last_price
        sl = entry + (entry * 0.001)
        tp1 = entry - (entry * 0.001)
        tp2 = entry - (entry * 0.002)
        tp3 = entry - (entry * 0.003)
    else:
        return None

    confidence = int(abs(change_pct) * 1000) + (10 if volume_spike else 0)

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
