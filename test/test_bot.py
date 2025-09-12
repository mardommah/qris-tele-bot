import asyncio
import pytest
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

@pytest.mark.asyncio
async def test_bot():
    try:
        print(f"Token: {TELEGRAM_BOT_TOKEN}")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.initialize()
        print(f"Bot ID: {bot.id}")
        print("Bot token is valid!")
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_bot())