#!/usr/bin/env python3
"""
Database Recovery Script for QRIS Telegram Bot

This script can restore the SQLite database from a backup SQL file.
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
from typing import Optional

# Database configuration
DATABASE_PATH = 'qris_bot.db'
BACKUP_DIR = 'backups'

def list_backups() -> list:
    """List all available backup files"""
    if not os.path.exists(BACKUP_DIR):
        print(f"❌ Backup directory '{BACKUP_DIR}' not found")
        return []
    
    backup_files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('qris_bot_backup_') and f.endswith('.sql')]
    backup_files.sort(reverse=True)  # Newest first
    
    return backup_files

def show_backups():
    """Display all available backups"""
    backups = list_backups()
    if not backups:
        print("❌ No backup files found")
        return
    
    print("\n📋 Available backups:")
    for i, backup in enumerate(backups, 1):
        print(f"  {i}. {backup}")
    print()

def get_backup_file(backup_name: str) -> Optional[str]:
    """Get the full path of a backup file"""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        print(f"❌ Backup file '{backup_name}' not found")
        return None
    return backup_path

def backup_current_db():
    """Create a backup of the current database before restoration"""
    if not os.path.exists(DATABASE_PATH):
        print("ℹ️  No current database to backup")
        return True
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"qris_bot_pre_restore_{timestamp}.sql"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Export current database
        conn = sqlite3.connect(DATABASE_PATH)
        with open(backup_path, 'w') as f:
            for line in conn.iterdump():
                f.write('%s\n' % line)
        conn.close()
        
        print(f"✅ Current database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to backup current database: {e}")
        return False

def restore_database(backup_path: str) -> bool:
    """Restore database from backup file"""
    try:
        # If database exists, remove it first to avoid conflicts
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)
            print("🗑️  Removed existing database file")
        
        # Connect to database (this will create it)
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Read and execute the backup SQL
        with open(backup_path, 'r') as f:
            sql_script = f.read()
        
        # Execute the SQL script
        conn.executescript(sql_script)
        conn.close()
        
        print(f"✅ Database successfully restored from: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to restore database: {e}")
        return False

def main():
    """Main function"""
    print("🔄 QRIS Telegram Bot Database Recovery Script")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Use backup file specified in command line
        backup_name = sys.argv[1]
        backups = list_backups()
        
        if backup_name not in backups:
            print(f"❌ Backup file '{backup_name}' not found in backups directory")
            show_backups()
            return 1
    else:
        # Interactive mode
        backups = list_backups()
        if not backups:
            return 1
            
        show_backups()
        
        while True:
            try:
                choice = input("Enter the number of the backup to restore (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    print("👋 Exiting...")
                    return 0
                    
                choice_num = int(choice)
                if 1 <= choice_num <= len(backups):
                    backup_name = backups[choice_num - 1]
                    break
                else:
                    print("❌ Invalid choice. Please enter a valid number.")
            except ValueError:
                print("❌ Invalid input. Please enter a number or 'q' to quit.")
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                return 0
    
    backup_path = get_backup_file(backup_name)
    if not backup_path:
        return 1
    
    print(f"\n🔄 Restoring database from: {backup_name}")
    
    # Create backup of current database
    print("\n🔒 Creating backup of current database...")
    if not backup_current_db():
        print("❌ Failed to backup current database. Aborting restoration.")
        return 1
    
    # Restore database
    print("\n🔄 Restoring database...")
    if restore_database(backup_path):
        print("\n✅ Database recovery completed successfully!")
        return 0
    else:
        print("\n❌ Database recovery failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())