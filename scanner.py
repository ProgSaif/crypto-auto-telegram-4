import requests

def get_movers():

    url = "https://api.binance.com/api/v3/ticker/24hr"

    data = requests.get(url).json()

    coins = []

    for item in data:

        symbol = item["symbol"]

        if "USDT" in symbol:

            change = float(item["priceChangePercent"])

            if change > 5:
                coin = symbol.replace("USDT","")
                coins.append(coin)

    return coins
