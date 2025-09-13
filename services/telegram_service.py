# services/telegram_service.py
"""Telegram service for handling bot operations."""

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from typing import List, Optional, Dict, Any
from services.logging_service import get_logger

logger = get_logger(__name__)


class TelegramService:
    """Service class for Telegram bot operations."""
    
    def create_reply_keyboard(self, keyboard_layout: List[List[str]], 
                             resize_keyboard: bool = True, 
                             one_time_keyboard: bool = False) -> ReplyKeyboardMarkup:
        """Create a reply keyboard markup."""
        logger.debug("Creating reply keyboard")
        return ReplyKeyboardMarkup(
            keyboard_layout, 
            resize_keyboard=resize_keyboard, 
            one_time_keyboard=one_time_keyboard
        )
    
    def remove_reply_keyboard(self) -> ReplyKeyboardRemove:
        """Remove reply keyboard."""
        logger.debug("Removing reply keyboard")
        return ReplyKeyboardRemove()


# Create a global instance
telegram_service = TelegramService()