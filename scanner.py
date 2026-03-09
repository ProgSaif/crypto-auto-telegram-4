import requests

# Top 100 coins (example list, you can update)
TOP_100_COINS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
    "ADAUSDT","DOGEUSDT","AVAXUSDT","DOTUSDT","LINKUSDT",
    "LTCUSDT","MATICUSDT","ATOMUSDT","UNIUSDT","APTUSDT"
    # add remaining coins up to 100...
]

def get_signal_coins():
    url = "https://data-api.binance.vision/api/v3/ticker/24hr"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = response.json()
        if not isinstance(data, list):
            print("Unexpected response:", data)
            return [], [], [], []

        top100_signals = []
        new_listings = []
        gainers = []
        losers = []

        for item in data:
            symbol = item.get("symbol", "")
            change = float(item.get("priceChangePercent",0))
            last_price = float(item.get("lastPrice",0))

            # Top 100 coins signals
            if symbol in TOP_100_COINS and abs(change) > 1:
                trade_type = "LONG" if change > 0 else "SHORT"
                entry = last_price
                sl = entry*0.98 if trade_type=="LONG" else entry*1.02
                tp1 = entry*1.02 if trade_type=="LONG" else entry*0.98
                tp2 = entry*1.04 if trade_type=="LONG" else entry*0.96
                tp3 = entry*1.06 if trade_type=="LONG" else entry*0.94
                confidence = min(int(abs(change)*10),95)
                coin = symbol.replace("USDT","")
                top100_signals.append({
                    "coin": coin,
                    "entry": entry,
                    "sl": sl,
                    "tp1": tp1,
                    "tp2": tp2,
                    "tp3": tp3,
                    "trade_type": trade_type,
                    "confidence": confidence
                })

            # Daily gainers/losers
            if change > 0:
                gainers.append((symbol, change, last_price))
            elif change < 0:
                losers.append((symbol, change, last_price))

            # Placeholder for new listings
            if symbol not in TOP_100_COINS and len(new_listings) < 5:
                new_listings.append((symbol, last_price))

        # Top 5 gainers/losers
        gainers = sorted(gainers, key=lambda x: x[1], reverse=True)[:5]
        losers = sorted(losers, key=lambda x: x[1])[:5]

        print("Top100 signals:", [s["coin"] for s in top100_signals])
        print("Gainers:", [s[0] for s in gainers])
        print("Losers:", [s[0] for s in losers])
        print("New listings:", [s[0] for s in new_listings])

        return top100_signals, gainers, losers, new_listings

    except Exception as e:
        print("Scanner error:", e)
        return [], [], [], []
