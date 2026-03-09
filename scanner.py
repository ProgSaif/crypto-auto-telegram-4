import requests
from signals import calculate_signal, get_klines

def scan_market():
    """
    Scan Binance market and return a list of eligible signals.
    Works for all USDT pairs.
    """

    url = "https://data-api.binance.vision/api/v3/ticker/24hr"

    try:
        # Request market data
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        data = response.json()

        # Check if response is valid
        if not isinstance(data, list):
            print("Unexpected Binance response:", data)
            return []

        signals = []

        for coin in data:
            symbol = coin.get("symbol")

            # Only USDT pairs
            if not symbol or not symbol.endswith("USDT"):
                continue

            try:
                # Extract price and change
                last_price = float(coin.get("lastPrice", 0))
                change_pct = float(coin.get("priceChangePercent", 0)) / 100
                daily_volume = float(coin.get("quoteVolume", 0))

                # Fetch klines for indicators
                df_5m = get_klines(symbol, interval="5m", limit=100)
                df_1h = get_klines(symbol, interval="1h", limit=100)

                if df_5m is None:
                    continue

                # Calculate signal
                signal = calculate_signal(
                    symbol,
                    last_price,
                    change_pct,
                    df_5m,
                    daily_volume,
                    df_1h  # higher timeframe trend confirmation
                )

                # 🔹 Debug print for RSI, EMA, and Volume spike
                if signal:
                    print(symbol,
                          "RSI:", signal.get("rsi"),
                          "Trend:", signal.get("ema_trend"),
                          "VolumeSpike:", signal.get("volume_spike"))

                    signals.append(signal)
                else:
                    # Optional: print coins that fail conditions
                    print(symbol,
                          "RSI:", signal.get("rsi") if signal else "N/A",
                          "Trend:", signal.get("ema_trend") if signal else "N/A",
                          "VolumeSpike:", signal.get("volume_spike") if signal else "N/A")

            except Exception as coin_error:
                print(f"Error processing {symbol}: {coin_error}")

        print("Signals detected:", len(signals))
        return signals

    except Exception as e:
        print("Scanner error:", e)
        return []
