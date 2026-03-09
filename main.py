import os
import asyncio
from telegram import Bot
from signals import get_signals, get_new_listings, get_gainers_losers
from poster import generate_signal_message, generate_listing_message, generate_gainers_losers_message

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
bot = Bot(token=BOT_TOKEN)
posted_keys = set()

async def send_message_safe(message, delete_after=300):
    for i in range(3):
        try:
            msg = await bot.send_message(chat_id=CHANNEL_ID, text=message)
            asyncio.create_task(delete_after_delay(msg.message_id, delete_after))
            return
        except Exception as e:
            if hasattr(e, "retry_after"):
                wait = e.retry_after + 1
                print(f"Flood control exceeded. Waiting {wait}s")
                await asyncio.sleep(wait)
            else:
                print("Telegram error:", e)
                await asyncio.sleep(15)

async def delete_after_delay(message_id, delay):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=CHANNEL_ID, message_id=message_id)
    except Exception as e:
        print("Failed to delete message:", e)

async def run_bot():
    print("🚀 High-Quality Signal Bot Started")
    while True:
        try:
            # Signals
            signals = get_signals()
            for s in signals:
                key = f"{s['coin']}_{s['trade_type']}"
                if key not in posted_keys:
                    msg = generate_signal_message(
                        s["coin"], s["entry"], s["sl"], s["tp1"], s["tp2"], s["tp3"],
                        s["trade_type"], s["confidence"]
                    )
                    print("Posting signal:", s["coin"])
                    await send_message_safe(msg)
                    posted_keys.add(key)
                    await asyncio.sleep(15)

            # New listings
            listings = get_new_listings()
            if listings:
                msg = generate_listing_message(listings)
                await send_message_safe(msg)
                await asyncio.sleep(15)

            # Gainers & Losers
            gainers, losers = get_gainers_losers()
            if gainers or losers:
                msg = generate_gainers_losers_message(gainers, losers)
                await send_message_safe(msg)
                await asyncio.sleep(15)

        except Exception as e:
            print("Bot loop error:", e)
            await asyncio.sleep(10)

        await asyncio.sleep(60)  # wait 1 minute before next scan

if __name__ == "__main__":
    asyncio.run(run_bot())
