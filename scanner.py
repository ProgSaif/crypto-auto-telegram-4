import requests
from signals import calculate_signal, get_klines


def scan_market():

    url = "https://api.binance.com/api/v3/ticker/24hr"

    try:

        response = requests.get(url, timeout=10)
        data = response.json()

        signals = []

        for coin in data:

            symbol = coin["symbol"]

            if not symbol.endswith("USDT"):
                continue

            last_price = float(coin["lastPrice"])
            change_pct = float(coin["priceChangePercent"]) / 100
            volume = float(coin["quoteVolume"])

            df = get_klines(symbol, "5m", 100)
            df_htf = get_klines(symbol, "1h", 100)

            if df is None:
                continue

            signal = calculate_signal(
                symbol,
                last_price,
                change_pct,
                df,
                volume,
                df_htf
            )

            if signal:
                signals.append(signal)

        print("Signals detected:", len(signals))

        return signals

    except Exception as e:
        print("Scanner error:", e)
        return []
