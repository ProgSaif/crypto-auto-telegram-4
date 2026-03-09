def generate_signal_message(signal):
    return f"""
${signal['coin']} – {signal['trade_type']}

Entry: {signal['entry']:.4f}
SL: {signal['sl']:.4f}
TP1: {signal['tp1']:.4f}
TP2: {signal['tp2']:.4f}
TP3: {signal['tp3']:.4f}

Why this setup?
• Confidence: {signal['confidence']}%
• RSI: {signal['rsi']:.2f}  EMA Trend: {signal['ema_trend']}
• Volume spike: {'Yes' if signal['volume_spike'] else 'No'}

— Follow for more real updates —
"""
