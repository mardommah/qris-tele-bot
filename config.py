# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Admin User ID
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '123456789'))

# Database
DATABASE_PATH = 'qris_bot.db'

# QRIS Configuration
DEFAULT_SERVICE_FEE = "0"  # Default biaya layanan