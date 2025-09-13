#!/usr/bin/env python3
# test_bot.py
"""Simple script to test if the bot token is working"""

import asyncio
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

async def test_bot():
    """Test bot connectivity"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        me = await bot.get_me()
        print(f"Bot is running: {me.first_name} (@{me.username})")
        print("Bot token is valid and working!")
        return True
    except Exception as e:
        print(f"Error testing bot: {e}")
        return False
    finally:
        await bot.close()

if __name__ == "__main__":
    try:
        # For Python 3.13 compatibility
        asyncio.run(test_bot())
    except Exception as e:
        print(f"Failed to run test: {e}")