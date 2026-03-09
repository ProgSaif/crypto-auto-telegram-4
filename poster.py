def generate_signal_message(coin, entry, sl, tp1, tp2, tp3, trade_type="LONG", confidence=85):
    return f"""
${coin} – {trade_type}

Entry: {entry:.2f}
SL: {sl:.2f}
TP1: {tp1:.2f}
TP2: {tp2:.2f}
TP3: {tp3:.2f}

Why this setup?
• Confidence: {confidence}%
• Price momentum detected, strong trend on 1H chart

— Follow for more real updates —
"""
