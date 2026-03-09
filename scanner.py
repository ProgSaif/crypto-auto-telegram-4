import requests

BASE_URL = "https://api.binance.us/api/v3"


def get_symbols():

    url = f"{BASE_URL}/exchangeInfo"
    r = requests.get(url)
    data = r.json()

    symbols = []

    for s in data["symbols"]:
        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING":
            symbols.append(s["symbol"])

    return symbols


def get_klines(symbol):

    url = f"{BASE_URL}/klines"

    params = {
        "symbol": symbol,
        "interval": "5m",
        "limit": 2
    }

    r = requests.get(url, params=params)

    return r.json()


def detect_signals():

    signals = []

    symbols = get_symbols()

    for symbol in symbols:

        try:

            klines = get_klines(symbol)

            prev_close = float(klines[-2][4])
            last_close = float(klines[-1][4])

            change = ((last_close - prev_close) / prev_close) * 100

            if change > 0.1:

                signals.append({
                    "coin": symbol,
                    "trade_type": "LONG",
                    "change": round(change, 2),
                    "price": last_close
                })

            elif change < -0.1:

                signals.append({
                    "coin": symbol,
                    "trade_type": "SHORT",
                    "change": round(change, 2),
                    "price": last_close
                })

        except:
            continue

    return signals
