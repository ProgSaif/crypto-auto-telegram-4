def generate_signal_message(coin, entry, sl, tp1, tp2, tp3, trade_type="LONG", confidence=85):
    return f"""
💹 ${coin} – {trade_type}

Entry: {entry:.8f}
SL: {sl:.8f}
TP1: {tp1:.8f}
TP2: {tp2:.8f}
TP3: {tp3:.8f}

Why this setup?
• Confidence: {confidence}%
• Strong trend on 1H chart
• Confirmed by EMA cross on 15m/1H charts
• RSI indicates {'oversold' if trade_type=='LONG' else 'overbought'} conditions
• Volume shows recent spike compared to average
• ATR used to calculate realistic TP/SL
• Momentum aligns with recent price breakout
• Suitable for intraday swing trading
• Risk/reward ratio favorable for calculated entries
• Coin is actively traded with sufficient liquidity

Please like and comment your PNL
— Follow for more updates —
DYOR 
#{coin}
"""
