def generate_signal_message(coin, entry, sl, tp1, tp2, tp3, trade_type="LONG", confidence=85):
    return f"""
${coin} – {trade_type}

Entry: {entry:.5f}
SL: {sl:.5f}
TP1: {tp1:.5f}
TP2: {tp2:.4f}
TP3: {tp3:.4f}

Why this setup?
• Confidence: {confidence}%
• Price momentum detected, strong trend on 1H chart

— Follow for more real updates —
"""
