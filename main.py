import os
import asyncio
import time
from telegram import Bot
from scanner import get_signal_coins
from poster import generate_signal_message

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=BOT_TOKEN)

# store posted signals with timestamp
posted = {}

# how long before a signal can repeat (seconds)
SIGNAL_COOLDOWN = 3600  # 1 hour


async def send_message_safe(message):
    for i in range(5):
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=message
            )
            return

        except Exception as e:
            print("Telegram error:", e)

            if "Retry in" in str(e):
                try:
                    wait = int(str(e).split("Retry in ")[1].split(" ")[0])
                except:
                    wait = 15

                print(f"Flood control triggered. Waiting {wait} seconds...")
                await asyncio.sleep(wait)

            else:
                await asyncio.sleep(5)


async def run_bot():

    print("🚀 Signal bot started")

    while True:
        try:

            signals = get_signal_coins()[:5]

            now = time.time()

            for s in signals:

                key = f"{s['coin']}_{s['trade_type']}"

                # skip if posted recently
                if key in posted and now - posted[key] < SIGNAL_COOLDOWN:
                    continue

                message = generate_signal_message(
                    s["coin"],
                    s["entry"],
                    s["sl"],
                    s["tp1"],
                    s["tp2"],
                    s["tp3"],
                    s["trade_type"],
                    s["confidence"]
                )

                print("Posting:", s["coin"], s["trade_type"])

                await send_message_safe(message)

                posted[key] = now

                await asyncio.sleep(10)

        except Exception as e:
            print("Bot error:", e)

        await asyncio.sleep(30)


asyncio.run(run_bot())
