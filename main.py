import os
import asyncio
from telegram import Bot
from signals import calculate_signal, get_klines  # make sure your signals.py has these functions
from poster import generate_signal_message

# ====== Environment Variables ======
BOT_TOKEN = os.getenv("BOT_TOKEN")       # Your Telegram Bot Token
CHANNEL_ID = os.getenv("CHANNEL_ID")     # Your Telegram Channel ID

bot = Bot(token=BOT_TOKEN)
posted_keys = set()  # track posted messages per candle

# ====== Safe Telegram Sender ======
async def send_message_safe(message):
    for attempt in range(3):
        try:
            msg = await bot.send_message(chat_id=CHANNEL_ID, text=message)
            return msg
        except Exception as e:
            # Handle Telegram Flood Control
            if hasattr(e, "retry_after"):
                wait = e.retry_after + 1
                print(f"Flood control exceeded. Waiting {wait} seconds...")
                await asyncio.sleep(wait)
            else:
                print("Telegram error:", e)
                await asyncio.sleep(5)
    return None

# ====== Main Bot Loop ======
async def run_bot():
    print("Starting High-Quality Signal Bot...")

    while True:
        try:
            # Example: top coins list from signals.py or hardcoded
            TOP_COINS = [
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT",
                "XRPUSDT", "DOGEUSDT", "LTCUSDT", "AVAXUSDT", "DOTUSDT"
            ]

            for symbol in TOP_COINS:
                # Fetch latest 5m candle data
                df = get_klines(symbol, interval="5m", limit=100)
                df_htf = get_klines(symbol, interval="1h", limit=50)  # higher timeframe trend

                if df is None or df_htf is None:
                    continue

                # Current price & change %
                last_price = df["close"].iloc[-1]
                change_pct = (last_price - df["close"].iloc[-2]) / df["close"].iloc[-2]

                # Optional: daily volume filter
                daily_volume = df["volume"].sum() * last_price

                signal = calculate_signal(
                    symbol=symbol,
                    last_price=last_price,
                    change_pct=change_pct,
                    df=df,
                    daily_volume=daily_volume,
                    df_higher_tf=df_htf
                )

                if signal:
                    # Key to avoid posting multiple times in same candle
                    candle_time = df["open_time"].iloc[-1]
                    key = f"{symbol}_{candle_time}"
                    if key in posted_keys:
                        continue
                    posted_keys.add(key)

                    # Generate professional Telegram message
                    message = generate_signal_message(
                        coin=signal["coin"],
                        entry=signal["entry"],
                        sl=signal["sl"],
                        tp1=signal["tp1"],
                        tp2=signal["tp2"],
                        tp3=signal["tp3"],
                        trade_type=signal["trade_type"],
                        confidence=signal["confidence"]
                    )

                    # Send to Telegram safely
                    msg_obj = await send_message_safe(message)
                    if msg_obj:
                        # Auto-delete after 5 minutes
                        asyncio.create_task(delete_after_delay(msg_obj.message_id, delay=300))

                    # Delay between messages to avoid flood
                    await asyncio.sleep(15)

            # Wait before next scan
            await asyncio.sleep(60)

        except Exception as e:
            print("Bot loop error:", e)
            await asyncio.sleep(10)

# ====== Auto-delete message ======
async def delete_after_delay(message_id, delay=300):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=CHANNEL_ID, message_id=message_id)
    except Exception as e:
        print("Failed to delete message:", e)

# ====== Run Bot ======
if __name__ == "__main__":
    asyncio.run(run_bot())
