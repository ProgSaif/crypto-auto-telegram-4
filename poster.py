def generate_signal_message(signal):
    return f"""
${signal['coin']} – {signal['trade_type']}

Entry: {signal['entry']:.2f}
SL: {signal['sl']:.2f}
TP1: {signal['tp1']:.2f}
TP2: {signal['tp2']:.2f}
TP3: {signal['tp3']:.2f}

Why this setup?
• Confidence: {signal['confidence']}%
• RSI: {signal['rsi']:.2f}  EMA Trend: {signal['ema_trend']}
• Volume spike: {'Yes' if signal['volume_spike'] else 'No'}

— Follow for more real updates —
"""
