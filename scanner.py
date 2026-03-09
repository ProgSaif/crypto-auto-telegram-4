import requests

def get_movers():

    url = "https://data-api.binance.vision/api/v3/ticker/24hr"

    try:

        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        data = response.json()

        coins = []

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

        print("Detected movers:", coins)

        return coins

    except Exception as e:

        print("Scanner error:", e)

        return []
