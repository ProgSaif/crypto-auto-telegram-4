import requests
from signals import calculate_signal, get_klines
import time

def scan_market():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    signals = []

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if not isinstance(data, list):
            print("Unexpected Binance response:", data)
            return signals
    except Exception as e:
        print("Failed to fetch market data:", e)
        return signals

    for item in data:
        symbol = item.get("symbol", "")
        if not symbol.endswith("USDT"):
            continue

        try:
            last_price = float(item.get("lastPrice", 0))
            change_pct = float(item.get("priceChangePercent", 0)) / 100
            daily_volume = float(item.get("quoteVolume", 0))

            df_5m = get_klines(symbol, interval="5m", limit=200)
            df_1h = get_klines(symbol, interval="1h", limit=200)

            signal = calculate_signal(symbol, last_price, change_pct, df_5m, daily_volume, df_higher_tf=df_1h)
            if signal:
                signals.append(signal)

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    print(f"Signals detected: {len(signals)}")
    return signals
