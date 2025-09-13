# config.py
"""Configuration module for the QRIS Telegram bot."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Admin User ID
ADMIN_USER_ID: int = int(os.getenv('ADMIN_USER_ID', '123456789'))

# Database
DATABASE_PATH: str = 'qris_bot.db'

# QRIS Configuration
DEFAULT_SERVICE_FEE: str = "0"  # Default biaya layanan