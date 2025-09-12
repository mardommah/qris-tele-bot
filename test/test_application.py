import asyncio
import pytest
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN

@pytest.mark.asyncio
async def test_application():
    try:
        print(f"Token: {TELEGRAM_BOT_TOKEN}")
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        print("Application built successfully")
        
        # Try to initialize the bot
        await application.initialize()
        print(f"Application initialized, Bot ID: {application.bot.id}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(test_application())