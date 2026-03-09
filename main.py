import os
import asyncio
from telegram import Bot
from scanner import detect_signals
from poster import generate_signal_message

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=BOT_TOKEN)

posted = set()


async def send_message_safe(message):
    for i in range(3):
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode="HTML"
            )
            return
        except Exception as e:
            print("Telegram error:", e)
            await asyncio.sleep(5)


async def run_bot():

    print("🚀 Crypto Signal Bot Started")

    while True:

        try:

            signals = detect_signals()

            for s in signals:

                key = f"{s['coin']}_{s['trade_type']}"

                if key not in posted:

                    message = generate_signal_message(s)

                    print("Posting:", s['coin'], s['trade_type'])

                    await send_message_safe(message)

                    posted.add(key)

                    await asyncio.sleep(2)

        except Exception as e:
            print("Scanner error:", e)

        await asyncio.sleep(10)


asyncio.run(run_bot())
