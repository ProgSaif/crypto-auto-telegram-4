import requests
from signals import calculate_signal, get_klines


def scan_market():

    url = "https://data-api.binance.vision/api/v3/ticker/24hr"

    try:

        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        data = response.json()

        if not isinstance(data, list):
            print("Unexpected Binance response:", data)
            return []

        signals = []

        for coin in data:

            symbol = coin.get("symbol")

            if not symbol.endswith("USDT"):
                continue

            try:

                last_price = float(coin.get("lastPrice", 0))
                change_pct = float(coin.get("priceChangePercent", 0)) / 100
                volume = float(coin.get("quoteVolume", 0))

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

            except Exception as coin_error:
                print(f"Error processing {symbol}: {coin_error}")

        print("Signals detected:", len(signals))

        return signals

    except Exception as e:
        print("Scanner error:", e)
        return []
