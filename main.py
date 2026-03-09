import os
import asyncio
from telegram import Bot
from scanner import get_signal_coins
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
                text=message
            )
            return
        except Exception as e:
            print("Telegram error:", e)
            await asyncio.sleep(15)


async def run_bot():
    print("🚀 Signal bot started")

    while True:
        try:
            signals = get_signal_coins()

            for s in signals:
                key = f"{s['coin']}_{s['trade_type']}"
                if key not in posted:
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
                    posted.add(key)
                    await asyncio.sleep(15)

        except Exception as e:
            print("Bot error:", e)

        await asyncio.sleep(30)


asyncio.run(run_bot())
