# database/connection.py

import sqlite3
from utils import log

DATABASE_NAME = 'pagedata.db'

def create_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.execute("PRAGMA foreign_keys = ON;") # Enforce foreign key constraints
        conn.execute("PRAGMA journal_mode = WAL;") # Enable Write-Ahead Logging
        return conn
    except sqlite3.Error as e:
        log.error(f"Database connection error: {e}")
        return None

def _execute_query(query, params=(), commit=False, fetch=None, executemany=False):
    """A central wrapper for all database queries."""
    conn = create_connection()
    if not conn:
        return (False, "Database connection failed.")
    try:
        cursor = conn.cursor()
        if executemany:
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params)
        
        if commit:
            conn.commit()
            result = cursor.lastrowid if not executemany else cursor.rowcount
            return (True, result)
        
        if fetch == 'one':
            return (True, cursor.fetchone())
        elif fetch == 'all':
            return (True, cursor.fetchall())
        
        return (True, True)
    except sqlite3.Error as e:
        log.error(f"Database query failed: {e}\nQuery: {query}\nParams: {params}")
        if conn:
            conn.rollback()
        return (False, str(e))
    finally:
        if conn:
            conn.close()

def create_tables():
    """Creates the necessary tables and indexes if they don't exist."""
    _execute_query('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT, profile_id TEXT NOT NULL UNIQUE,
            account_name TEXT NOT NULL, uid TEXT UNIQUE, account_category TEXT,
            status TEXT, monetization TEXT, proxy TEXT, proxy_location TEXT,
            is_deleted INTEGER DEFAULT 0, note TEXT DEFAULT ''
        )
    ''', commit=True)
    _execute_query('''
        CREATE TABLE IF NOT EXISTS pages (
            page_id INTEGER PRIMARY KEY AUTOINCREMENT, page_name TEXT NOT NULL,
            uid_page_id TEXT, category TEXT, content_folder TEXT, used_folders TEXT,
            video_schedule_date TEXT, video_posts_per_day INTEGER,
            reels_schedule_date TEXT, reels_posts_per_day INTEGER,
            photo_schedule_date TEXT, photo_posts_per_day INTEGER,
            note TEXT, status TEXT, monetization TEXT, is_deleted INTEGER DEFAULT 0,
            linked_account_id INTEGER,
            video_folder TEXT, reels_folder TEXT, photo_folder TEXT,
            followers TEXT, last_interaction TEXT,
            FOREIGN KEY (linked_account_id) REFERENCES accounts (account_id) ON DELETE CASCADE
        )
    ''', commit=True)
    
    _execute_query("CREATE INDEX IF NOT EXISTS idx_accounts_profile_id ON accounts (profile_id);", commit=True)
    _execute_query("CREATE INDEX IF NOT EXISTS idx_pages_linked_account_id ON pages (linked_account_id);", commit=True)

    # Schema migration for existing tables
    conn = create_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        account_columns = [col[1] for col in cursor.execute("PRAGMA table_info(accounts)").fetchall()]
        if 'note' not in account_columns:
            cursor.execute("ALTER TABLE accounts ADD COLUMN note TEXT DEFAULT ''")

        page_columns = [col[1] for col in cursor.execute("PRAGMA table_info(pages)").fetchall()]
        columns_to_add = {
            'video_folder': 'TEXT', 'reels_folder': 'TEXT', 'photo_folder': 'TEXT',
            'followers': 'TEXT', 'last_interaction': 'TEXT'
        }
        for col, col_type in columns_to_add.items():
            if col not in page_columns:
                cursor.execute(f"ALTER TABLE pages ADD COLUMN {col} {col_type}")
        conn.commit()
    finally:
        conn.close()