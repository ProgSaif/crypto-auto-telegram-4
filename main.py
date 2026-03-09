import os
import asyncio
from telegram import Bot
from scanner import get_movers
from poster import generate_post

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
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30
            )

            return

        except Exception as e:

            print("Telegram error:", e)

            await asyncio.sleep(5)


async def run_bot():

    while True:

        coins = get_movers()

        for coin in coins:

            if coin not in posted:

                message = generate_post(coin)

                print("Posting:", coin)

                await send_message_safe(message)

                posted.add(coin)

                await asyncio.sleep(3)

        await asyncio.sleep(300)


asyncio.run(run_bot())
