# database.py
"""Database module - legacy interface for backward compatibility."""

from services.database_service import db_service

# Legacy functions for backward compatibility
def init_db() -> None:
    """Initialize database"""
    db_service.init_db()

def add_merchant(name: str, qris_static: str, owner_telegram_id: int, qris_image_path: str = None) -> int:
    """Add a new merchant"""
    return db_service.add_merchant(name, qris_static, owner_telegram_id, qris_image_path)

def get_merchants():
    """Get all merchants"""
    return db_service.get_merchants()

def get_merchant_by_id(merchant_id: int):
    """Get merchant by ID"""
    return db_service.get_merchant_by_id(merchant_id)

def get_merchant_by_owner(owner_telegram_id: int):
    """Get merchant by owner Telegram ID"""
    return db_service.get_merchant_by_owner(owner_telegram_id)

def get_user_merchants(user_telegram_id: int):
    """Get merchant by owner Telegram ID"""
    return db_service.get_user_merchants(user_telegram_id)

def update_merchant_qris(merchant_id: int, qris_static: str, qris_image_path: str = None) -> None:
    """Update merchant QRIS"""
    db_service.update_merchant_qris(merchant_id, qris_static, qris_image_path)

def add_transaction(user_id: int, chat_id: int, merchant_id: int, amount: str, service_fee: str = "0", qris_dynamic: str = None) -> int:
    """Add a new transaction"""
    return db_service.add_transaction(user_id, chat_id, merchant_id, amount, service_fee, qris_dynamic)

def get_user_transactions(user_id: int):
    """Get user transaction history"""
    return db_service.get_user_transactions(user_id)

def get_transaction_by_id(transaction_id: int):
    """Get transaction by ID"""
    return db_service.get_transaction_by_id(transaction_id)

def get_transaction_with_merchant(transaction_id: int):
    """Get transaction with merchant details"""
    return db_service.get_transaction_with_merchant(transaction_id)

def update_transaction_status(transaction_id: int, status: str) -> None:
    """Update transaction status"""
    db_service.update_transaction_status(transaction_id, status)

def add_admin(user_id: int, username: str = None) -> bool:
    """Add admin"""
    return db_service.add_admin(user_id, username)

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return db_service.is_admin(user_id)

def get_default_merchant():
    """Get the first merchant as default"""
    return db_service.get_default_merchant()