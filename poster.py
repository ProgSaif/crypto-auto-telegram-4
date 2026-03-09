def generate_signal_message(coin, entry, sl, tp1, tp2, tp3, trade_type="LONG", confidence=85):

    return f"""
${coin} – {trade_type}

Entry: {entry:.6f}
SL: {sl:.6f}
TP1: {tp1:.6f}
TP2: {tp2:.5f}
TP3: {tp3:.5f}

Why this setup?
• Confidence: {confidence}%
• Price momentum detected, strong trend on 1H chart

— Follow for more real updates —
DYOR 
#{coin}
"""
