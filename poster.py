def generate_signal_message(coin, entry, sl, tp1, tp2, tp3, trade_type="LONG", confidence=85):
    entry_low = entry * 0.995
    entry_high = entry * 1.005

    message = f"""
Traders are watching the majors… but ${coin} just flashed momentum.
${coin} — {trade_type}

Entry: {entry_low:.4f} – {entry_high:.4f}
SL: {sl:.4f}
TP1: {tp1:.4f}
TP2: {tp2:.4f}
TP3: {tp3:.4f}

Why this setup?
{coin} just broke out of its consolidation range with a strong {'bullish' if trade_type=='LONG' else 'bearish'} candle.
Price reclaimed the {entry:.4f} level, showing {'buyers' if trade_type=='LONG' else 'sellers'} stepping back in after weeks of sideways action.
If {'bulls' if trade_type=='LONG' else 'bears'} hold above {entry_low:.4f}, the next liquidity sits around {tp1:.4f}+.
The real question:
Is this the start of a bigger breakout… or just the first liquidity grab? 👀

Trade ${coin} here 👇
"""
    return message
