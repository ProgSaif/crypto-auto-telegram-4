import requests
import time

BASE_URL = "https://api.binance.us/api/v3"

# Get all USDT pairs
def get_symbols():
    url = f"{BASE_URL}/exchangeInfo"
    r = requests.get(url)

    data = r.json()

    if "symbols" not in data:
        print("Unexpected response from Binance:", data)
        return []

    symbols = [s["symbol"] for s in data["symbols"] if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"]

    return symbols


# Get klines
def get_klines(symbol, interval="5m", limit=50):
    url = f"{BASE_URL}/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    r = requests.get(url, params=params)

    return r.json()


# Simple breakout strategy
def check_signal(symbol):

    klines = get_klines(symbol)

    if not klines or isinstance(klines, dict):
        return

    closes = [float(k[4]) for k in klines]

    last = closes[-1]
    prev = closes[-2]

    change = ((last - prev) / prev) * 100

    if change > 0.1:
        print(f"🚀 {symbol} PUMPING +{change:.2f}%")

    elif change < -0.1:
        print(f"🔻 {symbol} DUMPING {change:.2f}%")


def run_scanner():

    while True:

        symbols = get_symbols()

        if not symbols:
            print("No symbols fetched, skipping scan.")
            time.sleep(10)
            continue

        print(f"Scanning {len(symbols)} USDT pairs...")

        for symbol in symbols:

            try:
                check_signal(symbol)
                time.sleep(0.1)

            except Exception as e:
                print("Error:", e)

        print("Scan complete. Waiting 60s...\n")
        time.sleep(60)


run_scanner()
