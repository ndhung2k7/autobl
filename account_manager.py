"""
Account management module
"""
import json
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
from utils import logger, DataValidator

class AccountManager:
    """Manage social media accounts"""
    
    def __init__(self, db_path: str = 'auto_comment.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT,
                cookie TEXT,
                token TEXT,
                proxy TEXT,
                platform TEXT,
                status TEXT DEFAULT 'inactive',
                last_active TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                action TEXT,
                status TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_account(self, username: str, password: str = None, 
                   cookie: str = None, token: str = None,
                   proxy: str = None, platform: str = 'facebook') -> bool:
        """Add new account"""
        if not DataValidator.validate_username(username):
            logger.error("Invalid username")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if account exists
            cursor.execute('SELECT id FROM accounts WHERE username = ?', (username,))
            if cursor.fetchone():
                logger.error(f"Account {username} already exists")
                return False
            
            # Hash password if provided
            if password:
                password = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO accounts (username, password, cookie, token, proxy, platform, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, cookie, token, proxy, platform, 'active'))
            
            account_id = cursor.lastrowid
            conn.commit()
            
            # Log activity
            self._log_account_activity(account_id, 'add', 'success', 'Account added')
            
            logger.info(f"Account {username} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding account: {e}")
            return False
        finally:
            conn.close()
    
    def update_account(self, account_id: int, **kwargs) -> bool:
        """Update account information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            update_fields = []
            values = []
            
            for key, value in kwargs.items():
                if value is not None and key in ['username', 'password', 'cookie', 'token', 'proxy', 'platform', 'status']:
                    if key == 'password':
                        value = hashlib.sha256(value.encode()).hexdigest()
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if update_fields:
                values.append(account_id)
                query = f"UPDATE accounts SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                
                self._log_account_activity(account_id, 'update', 'success', f'Updated fields: {", ".join(update_fields)}')
                logger.info(f"Account {account_id} updated")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating account: {e}")
            return False
        finally:
            conn.close()
    
    def delete_account(self, account_id: int) -> bool:
        """Delete account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
            conn.commit()
            
            logger.info(f"Account {account_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting account: {e}")
            return False
        finally:
            conn.close()
    
    def get_accounts(self, status: str = None) -> List[Dict]:
        """Get all accounts"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute('SELECT * FROM accounts WHERE status = ?', (status,))
            else:
                cursor.execute('SELECT * FROM accounts')
            
            accounts = [dict(row) for row in cursor.fetchall()]
            return accounts
            
        except Exception as e:
            logger.error(f"Error fetching accounts: {e}")
            return []
        finally:
            conn.close()
    
    def update_status(self, account_id: int, status: str, details: str = '') -> bool:
        """Update account status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE accounts 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (status, account_id))
            conn.commit()
            
            self._log_account_activity(account_id, 'status_change', status, details)
            logger.info(f"Account {account_id} status changed to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return False
        finally:
            conn.close()
    
    def _log_account_activity(self, account_id: int, action: str, status: str, details: str):
        """Log account activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO account_logs (account_id, action, status, details)
                VALUES (?, ?, ?, ?)
            ''', (account_id, action, status, details))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
        finally:
            conn.close()
