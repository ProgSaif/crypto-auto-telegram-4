import requests

def get_signal_coins():

    url = "https://data-api.binance.vision/api/v3/ticker/24hr"

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = response.json()

        signals = []

        if not isinstance(data, list):
            print("Unexpected response:", data)
            return []

        for item in data:
            symbol = item.get("symbol", "")
            if symbol.endswith("USDT"):
                change = float(item.get("priceChangePercent", 0))
                last_price = float(item.get("lastPrice", 0))

                if change > 5:  # bullish signal
                    entry = last_price
                    sl = entry * 0.98  # 2% stop loss
                    tp1 = entry * 1.02
                    tp2 = entry * 1.04
                    tp3 = entry * 1.06
                    trade_type = "LONG"
                    confidence = int(change * 2)  # simple confidence score

                    coin = symbol.replace("USDT", "")
                    signals.append({
                        "coin": coin,
                        "entry": entry,
                        "sl": sl,
                        "tp1": tp1,
                        "tp2": tp2,
                        "tp3": tp3,
                        "trade_type": trade_type,
                        "confidence": confidence
                    })

                elif change < -5:  # bearish signal
                    entry = last_price
                    sl = entry * 1.02
                    tp1 = entry * 0.98
                    tp2 = entry * 0.96
                    tp3 = entry * 0.94
                    trade_type = "SHORT"
                    confidence = int(-change * 2)

                    coin = symbol.replace("USDT", "")
                    signals.append({
                        "coin": coin,
                        "entry": entry,
                        "sl": sl,
                        "tp1": tp1,
                        "tp2": tp2,
                        "tp3": tp3,
                        "trade_type": trade_type,
                        "confidence": confidence
                    })

        print("Detected signals:", [s["coin"] for s in signals])
        return signals

    except Exception as e:
        print("Scanner error:", e)
        return []
