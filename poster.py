def generate_signal_message(coin, entry, sl, tp1, tp2, tp3, trade_type="LONG", confidence=85):
    return f""" ${coin} – {trade_type}

Entry: {entry:.8f}
SL: {sl:.8f}
TP1: {tp1:.8f}
TP2: {tp2:.8f}
TP3: {tp3:.8f}

Please like and comment
— Follow for more signal —

Why this setup?
• Confidence: {confidence}%
• Strong trend on 1H chart
• RSI indicates {'oversold' if trade_type=='LONG' else 'overbought'} conditions
• Momentum aligns with recent price breakout
• ${coin} is actively traded with sufficient liquidity


DYOR 
#{coin}
"""
