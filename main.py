import os
import asyncio
import time
from telegram import Bot
from scanner import get_signal_coins
from poster import generate_signal_message

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=BOT_TOKEN)
posted = {}
SIGNAL_COOLDOWN = 3600  # 1 hour

async def send_message_safe(message):
    for i in range(5):
        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=message)
            return
        except Exception as e:
            print("Telegram error:", e)
            if "Retry in" in str(e):
                try:
                    wait = int(str(e).split("Retry in ")[1].split(" ")[0])
                except:
                    wait = 15
                print(f"Flood control triggered. Waiting {wait}s...")
                await asyncio.sleep(wait)
            else:
                await asyncio.sleep(5)

async def run_bot():
    print("🚀 Signal bot started")
    while True:
        try:
            top100_signals, gainers, losers, new_listings = get_signal_coins()
            now = time.time()

            # Top 100 signals (momentum)
            count = 0
            for s in top100_signals:
                key = f"{s['coin']}_{s['trade_type']}"
                if key in posted and now - posted[key] < SIGNAL_COOLDOWN:
                    continue
                message = generate_signal_message(**s)
                await send_message_safe(message)
                posted[key] = now
                count += 1
                if count >= 5:  # post max 5 per cycle
                    break
                await asyncio.sleep(10)

            # Daily gainers
            for symbol, change, price in gainers:
                key = f"{symbol}_GAINER"
                if key in posted and now - posted[key] < SIGNAL_COOLDOWN:
                    continue
                message = f"📈 GAINER ALERT\n${symbol} +{change:.2f}%\nPrice: {price:.6f}"
                await send_message_safe(message)
                posted[key] = now
                await asyncio.sleep(5)

            # Daily losers
            for symbol, change, price in losers:
                key = f"{symbol}_LOSER"
                if key in posted and now - posted[key] < SIGNAL_COOLDOWN:
                    continue
                message = f"📉 LOSER ALERT\n${symbol} {change:.2f}%\nPrice: {price:.6f}"
                await send_message_safe(message)
                posted[key] = now
                await asyncio.sleep(5)

            # New listings
            for symbol, price in new_listings:
                key = f"{symbol}_NEW"
                if key in posted and now - posted[key] < SIGNAL_COOLDOWN:
                    continue
                message = f"🆕 NEW LISTING\n${symbol}\nPrice: {price:.6f}"
                await send_message_safe(message)
                posted[key] = now
                await asyncio.sleep(5)

        except Exception as e:
            print("Bot error:", e)

        await asyncio.sleep(30)  # wait before next scan

asyncio.run(run_bot())
