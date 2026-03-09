def calculate_signal(coin, last_price, change_pct, rsi, ema_trend, volume_spike):

    if change_pct > 2:
        trade_type = "LONG"
        entry = last_price
        sl = entry - (entry * 0.01) if not volume_spike else entry - (entry * 0.02)
        tp1 = entry + (entry * 0.01)
        tp2 = entry + (entry * 0.02)
        tp3 = entry + (entry * 0.03)
    elif change_pct < -2:
        trade_type = "SHORT"
        entry = last_price
        sl = entry + (entry * 0.01) if not volume_spike else entry + (entry * 0.02)
        tp1 = entry - (entry * 0.01)
        tp2 = entry - (entry * 0.02)
        tp3 = entry - (entry * 0.03)
    else:
        return None

    confidence = int(abs(change_pct) * 2) + (10 if volume_spike else 0)

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
