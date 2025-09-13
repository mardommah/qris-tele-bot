#!/usr/bin/env python3
# check_webhook.py
"""Script to check the current webhook status of the bot"""

import asyncio
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

async def check_webhook():
    """Check webhook status"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        webhook_info = await bot.get_webhook_info()
        print("Webhook Info:")
        print(f"  URL: {webhook_info.url}")
        print(f"  Has Custom Certificate: {webhook_info.has_custom_certificate}")
        print(f"  Pending Update Count: {webhook_info.pending_update_count}")
        print(f"  Last Error Date: {webhook_info.last_error_date}")
        print(f"  Last Error Message: {webhook_info.last_error_message}")
        print(f"  Max Connections: {webhook_info.max_connections}")
        print(f"  Allowed Updates: {webhook_info.allowed_updates}")
    except Exception as e:
        print(f"Error checking webhook: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(check_webhook())