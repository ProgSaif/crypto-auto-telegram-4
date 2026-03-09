def generate_signal_message(signal):

    coin = signal["coin"]
    trade = signal["trade_type"]
    change = signal["change"]
    price = signal["price"]

    emoji = "🚀" if trade == "LONG" else "🔻"

    message = f"""
{emoji} <b>CRYPTO SIGNAL</b>

Coin: <b>{coin}</b>
Direction: <b>{trade}</b>

Price: {price}
Move: {change}%

#crypto #signal
"""

    return message
