#!/usr/bin/env python3
# delete_webhook.py
"""Script to delete any existing webhook on the bot"""

import asyncio
from telegram import Bot
from telegram.request import HTTPXRequest
from config import TELEGRAM_BOT_TOKEN

async def delete_webhook():
    """Delete webhook if it exists"""
    # Use explicit HTTP backend
    request = HTTPXRequest()
    bot = Bot(token=TELEGRAM_BOT_TOKEN, request=request)
    try:
        # Delete webhook
        await bot.delete_webhook(drop_pending_updates=True)
        print("Webhook deleted successfully (if it existed)")
        
        # Check current webhook info
        webhook_info = await bot.get_webhook_info()
        print("Current Webhook Info:")
        print(f"  URL: {webhook_info.url}")
        print(f"  Has Custom Certificate: {webhook_info.has_custom_certificate}")
        print(f"  Pending Update Count: {webhook_info.pending_update_count}")
    except Exception as e:
        print(f"Error managing webhook: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(delete_webhook())
    except Exception as e:
        print(f"Failed to run: {e}")