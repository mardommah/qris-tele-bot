# services/database_service.py
"""Database service for handling all database operations."""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional, Union
from config import DATABASE_PATH
from services.logging_service import get_logger

logger = get_logger(__name__)


class DatabaseService:
    """Service class for database operations."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database service."""
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_db(self) -> None:
        """Initialize database tables."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Tabel merchants
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS merchants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    qris_static TEXT NOT NULL,
                    qris_image_path TEXT,
                    owner_telegram_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabel transactions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    merchant_id INTEGER,
                    amount TEXT NOT NULL,
                    service_fee TEXT DEFAULT '0',
                    qris_dynamic TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (merchant_id) REFERENCES merchants (id)
                )
            ''')
            
            # Tabel admins (untuk multiple admin)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    # Merchant operations
    def add_merchant(self, name: str, qris_static: str, owner_telegram_id: int, qris_image_path: str = None) -> int:
        """Add a new merchant."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO merchants (name, qris_static, qris_image_path, owner_telegram_id) VALUES (?, ?, ?, ?)
            ''', (name, qris_static, qris_image_path, owner_telegram_id))
            merchant_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Merchant added with ID: {merchant_id}")
            return merchant_id
        except Exception as e:
            logger.error(f"Error adding merchant: {e}")
            raise

    def get_merchants(self) -> List[Tuple]:
        """Get all merchants."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM merchants')
            merchants = cursor.fetchall()
            conn.close()
            logger.info(f"Retrieved {len(merchants)} merchants")
            return merchants
        except Exception as e:
            logger.error(f"Error retrieving merchants: {e}")
            raise

    def get_merchant_by_id(self, merchant_id: int) -> Optional[Tuple]:
        """Get merchant by ID."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM merchants WHERE id = ?', (merchant_id,))
            merchant = cursor.fetchone()
            conn.close()
            if merchant:
                logger.info(f"Merchant found with ID: {merchant_id}")
            else:
                logger.info(f"No merchant found with ID: {merchant_id}")
            return merchant
        except Exception as e:
            logger.error(f"Error retrieving merchant by ID {merchant_id}: {e}")
            raise

    def get_merchant_by_owner(self, owner_telegram_id: int) -> Optional[Tuple]:
        """Get merchant by owner Telegram ID."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM merchants WHERE owner_telegram_id = ?', (owner_telegram_id,))
            merchant = cursor.fetchone()
            conn.close()
            if merchant:
                logger.info(f"Merchant found for owner ID: {owner_telegram_id}")
            else:
                logger.info(f"No merchant found for owner ID: {owner_telegram_id}")
            return merchant
        except Exception as e:
            logger.error(f"Error retrieving merchant by owner ID {owner_telegram_id}: {e}")
            raise

    def get_user_merchants(self, user_telegram_id: int) -> Optional[Tuple]:
        """Get merchant by owner Telegram ID."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM merchants WHERE owner_telegram_id = ?', (user_telegram_id,))
            merchant = cursor.fetchone()
            conn.close()
            if merchant:
                logger.info(f"User merchant found for user ID: {user_telegram_id}")
            else:
                logger.info(f"No user merchant found for user ID: {user_telegram_id}")
            return merchant
        except Exception as e:
            logger.error(f"Error retrieving user merchant for user ID {user_telegram_id}: {e}")
            raise

    def update_merchant_qris(self, merchant_id: int, qris_static: str, qris_image_path: str = None) -> None:
        """Update merchant QRIS."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if qris_image_path:
                cursor.execute('''
                    UPDATE merchants SET qris_static = ?, qris_image_path = ? WHERE id = ?
                ''', (qris_static, qris_image_path, merchant_id))
            else:
                cursor.execute('''
                    UPDATE merchants SET qris_static = ? WHERE id = ?
                ''', (qris_static, merchant_id))
            conn.commit()
            conn.close()
            logger.info(f"Merchant QRIS updated for merchant ID: {merchant_id}")
        except Exception as e:
            logger.error(f"Error updating merchant QRIS for merchant ID {merchant_id}: {e}")
            raise

    def get_default_merchant(self) -> Optional[Tuple]:
        """Get the first merchant as default."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM merchants LIMIT 1')
            merchant = cursor.fetchone()
            conn.close()
            if merchant:
                logger.info("Default merchant retrieved")
            else:
                logger.info("No default merchant found")
            return merchant
        except Exception as e:
            logger.error(f"Error retrieving default merchant: {e}")
            raise

    # Transaction operations
    def add_transaction(self, user_id: int, chat_id: int, merchant_id: int, amount: str, 
                       service_fee: str = "0", qris_dynamic: str = None) -> int:
        """Add a new transaction."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (user_id, chat_id, merchant_id, amount, service_fee, qris_dynamic)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, chat_id, merchant_id, amount, service_fee, qris_dynamic))
            transaction_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Transaction added with ID: {transaction_id}")
            return transaction_id
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            raise

    def get_user_transactions(self, user_id: int) -> List[Tuple]:
        """Get user transaction history."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, m.name as merchant_name 
                FROM transactions t 
                LEFT JOIN merchants m ON t.merchant_id = m.id 
                WHERE t.user_id = ? 
                ORDER BY t.created_at DESC
            ''', (user_id,))
            transactions = cursor.fetchall()
            conn.close()
            logger.info(f"Retrieved {len(transactions)} transactions for user ID: {user_id}")
            return transactions
        except Exception as e:
            logger.error(f"Error retrieving transactions for user ID {user_id}: {e}")
            raise

    def get_user_transactions_by_date(self, user_id: int, date: str) -> List[Tuple]:
        """Get user transaction history for a specific date."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, m.name as merchant_name 
                FROM transactions t 
                LEFT JOIN merchants m ON t.merchant_id = m.id 
                WHERE t.user_id = ? AND DATE(t.created_at) = ?
                ORDER BY t.created_at DESC
            ''', (user_id, date))
            transactions = cursor.fetchall()
            conn.close()
            logger.info(f"Retrieved {len(transactions)} transactions for user ID: {user_id} on date: {date}")
            return transactions
        except Exception as e:
            logger.error(f"Error retrieving transactions for user ID {user_id} on date {date}: {e}")
            raise

    def get_user_transactions_today(self, user_id: int) -> List[Tuple]:
        """Get user transaction history for today."""
        try:
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            return self.get_user_transactions_by_date(user_id, today)
        except Exception as e:
            logger.error(f"Error retrieving today's transactions for user ID {user_id}: {e}")
            raise

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Tuple]:
        """Get transaction by ID."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM transactions WHERE id = ?
            ''', (transaction_id,))
            transaction = cursor.fetchone()
            conn.close()
            if transaction:
                logger.info(f"Transaction found with ID: {transaction_id}")
            else:
                logger.info(f"No transaction found with ID: {transaction_id}")
            return transaction
        except Exception as e:
            logger.error(f"Error retrieving transaction by ID {transaction_id}: {e}")
            raise

    def get_transaction_with_merchant(self, transaction_id: int) -> Optional[Tuple]:
        """Get transaction with merchant details."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, m.name as merchant_name 
                FROM transactions t 
                LEFT JOIN merchants m ON t.merchant_id = m.id 
                WHERE t.id = ?
            ''', (transaction_id,))
            transaction = cursor.fetchone()
            conn.close()
            if transaction:
                logger.info(f"Transaction with merchant found for ID: {transaction_id}")
            else:
                logger.info(f"No transaction with merchant found for ID: {transaction_id}")
            return transaction
        except Exception as e:
            logger.error(f"Error retrieving transaction with merchant for ID {transaction_id}: {e}")
            raise

    def update_transaction_status(self, transaction_id: int, status: str) -> None:
        """Update transaction status."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE transactions SET status = ? WHERE id = ?
            ''', (status, transaction_id))
            conn.commit()
            conn.close()
            logger.info(f"Transaction status updated to {status} for ID: {transaction_id}")
        except Exception as e:
            logger.error(f"Error updating transaction status for ID {transaction_id}: {e}")
            raise

    # Admin operations
    def add_admin(self, user_id: int, username: str = None) -> bool:
        """Add admin."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO admins (user_id, username) VALUES (?, ?)
            ''', (user_id, username))
            conn.commit()
            conn.close()
            logger.info(f"Admin added with user ID: {user_id}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"User ID {user_id} is already an admin")
            return False
        except Exception as e:
            logger.error(f"Error adding admin with user ID {user_id}: {e}")
            raise

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM admins WHERE user_id = ?', (user_id,))
            result = cursor.fetchone() is not None
            conn.close()
            if result:
                logger.info(f"User ID {user_id} is an admin")
            else:
                logger.info(f"User ID {user_id} is not an admin")
            return result
        except Exception as e:
            logger.error(f"Error checking admin status for user ID {user_id}: {e}")
            raise


# Create a global instance
db_service = DatabaseService()