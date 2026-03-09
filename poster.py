def generate_signal_message(coin, entry, sl, tp1, tp2, tp3, trade_type, confidence):

    return f"""
💹 ${coin} – {trade_type}

Entry: {entry:.6f}
SL: {sl:.6f}

TP1: {tp1:.6f}
TP2: {tp2:.6f}
TP3: {tp3:.6f}

Why this setup?
• Confidence: {confidence}%
• RSI + EMA trend + Volume spike

DYOR

#{coin}
"""
