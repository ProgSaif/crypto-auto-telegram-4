import os
import asyncio
from telegram import Bot
from scanner import detect_signals
from poster import generate_signal_message

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=BOT_TOKEN)
posted = set()

async def send_message_safe(message, chart=None):
    for i in range(3):
        try:
            if chart:
                with open(chart, "rb") as img:
                    await bot.send_photo(chat_id=CHANNEL_ID, photo=img, caption=message)
            else:
                await bot.send_message(chat_id=CHANNEL_ID, text=message)
            return
        except Exception as e:
            print("Telegram error:", e)
            await asyncio.sleep(5)

async def run_bot():
    while True:
        signals = detect_signals()

        for s in signals:
            key = f"{s['coin']}_{s['trade_type']}"
            if key not in posted:
                message = generate_signal_message(s)
                chart = s.get("chart_file")
                print("Posting:", s['coin'], s['trade_type'])
                await send_message_safe(message, chart)
                posted.add(key)
                await asyncio.sleep(5)
        await asyncio.sleep(300)  # repeat every 5 min

asyncio.run(run_bot())
