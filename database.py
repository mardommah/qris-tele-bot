# database.py
import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH

def init_db():
    """Inisialisasi database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Tabel merchants
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            qris_static TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabel transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
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

def add_merchant(name: str, qris_static: str):
    """Tambah merchant baru"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO merchants (name, qris_static) VALUES (?, ?)
    ''', (name, qris_static))
    merchant_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return merchant_id

def get_merchants():
    """Dapatkan semua merchant"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM merchants')
    merchants = cursor.fetchall()
    conn.close()
    return merchants

def add_transaction(user_id: int, merchant_id: int, amount: str, service_fee: str = "0", qris_dynamic: str = None):
    """Tambah transaksi baru"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (user_id, merchant_id, amount, service_fee, qris_dynamic)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, merchant_id, amount, service_fee, qris_dynamic))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def get_user_transactions(user_id: int):
    """Dapatkan riwayat transaksi user"""
    conn = sqlite3.connect(DATABASE_PATH)
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
    return transactions

def get_transaction_by_id(transaction_id: int):
    """Dapatkan transaksi berdasarkan ID"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM transactions WHERE id = ?
    ''', (transaction_id,))
    transaction = cursor.fetchone()
    conn.close()
    return transaction

def update_transaction_status(transaction_id: int, status: str):
    """Update status transaksi"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE transactions SET status = ? WHERE id = ?
    ''', (status, transaction_id))
    conn.commit()
    conn.close()

def add_admin(user_id: int, username: str = None):
    """Tambah admin"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO admins (user_id, username) VALUES (?, ?)
        ''', (user_id, username))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result

def is_admin(user_id: int):
    """Cek apakah user adalah admin"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM admins WHERE user_id = ?', (user_id,))
    result = cursor.fetchone() is not None
    conn.close()
    return result

def get_default_merchant():
    """Dapatkan merchant pertama sebagai default"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM merchants LIMIT 1')
    merchant = cursor.fetchone()
    conn.close()
    return merchant