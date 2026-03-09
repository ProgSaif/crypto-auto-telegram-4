# poster.py
def generate_signal_message(coin, entry, sl, tp1, tp2, tp3, trade_type="LONG", confidence=85):
    return f"""💹 ${coin} – {trade_type}

Entry: {entry:.6f}
SL: {sl:.6f}
TP1: {tp1:.6f}
TP2: {tp2:.6f}
TP3: {tp3:.6f}

Why this setup?
• Confidence: {confidence}%
• High-quality signal based on RSI, EMA, ATR, Volume

— Follow for more real updates —
DYOR
#{coin}
"""

def generate_listing_message(symbols):
    msg = "🆕 New Listings:\n"
    for s in symbols:
        msg += f"${s}\n"
    return msg

def generate_gainers_losers_message(gainers, losers):
    msg = "📈 Top Gainers:\n"
    for g in gainers:
        msg += f"${g['symbol']} +{float(g['priceChangePercent']):.2f}%\n"

    msg += "\n📉 Top Losers:\n"
    for l in losers:
        msg += f"${l['symbol']} {float(l['priceChangePercent']):.2f}%\n"

    return msg
