import requests

def get_movers():

    url = "https://api.binance.com/api/v3/ticker/24hr"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        coins = []

        # make sure data is a list
        if not isinstance(data, list):
            print("Unexpected Binance response:", data)
            return []

        for item in data:

            symbol = item.get("symbol", "")

            if symbol.endswith("USDT"):

                change = float(item.get("priceChangePercent", 0))

                if change > 5:

                    coin = symbol.replace("USDT", "")
                    coins.append(coin)

        return coins

    except Exception as e:

        print("Scanner error:", e)
        return []
