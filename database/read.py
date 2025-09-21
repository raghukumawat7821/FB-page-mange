# database/read.py

from .connection import _execute_query, create_connection
import sqlite3

def get_table_data_for_export(table_name):
    """Fetches all non-deleted records and column headers for a given table."""
    conn = create_connection() # --- THIS LINE IS NOW CORRECT ---
    if not conn:
        return (False, "Database connection failed.", None)
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        headers = [row[1] for row in cursor.fetchall()]
        cursor.execute(f"SELECT * FROM {table_name} WHERE is_deleted = 0")
        data = cursor.fetchall()
        return (True, headers, data)
    except sqlite3.Error as e:
        return (False, str(e), None)
    finally:
        if conn:
            conn.close()

def get_all_accounts_data(search_term="", account_category_filter=None, limit=None, offset=0, account_ids_to_include=None):
    """
    Fetches accounts that either match the search term directly OR are in the
    provided list of IDs (e.g., from a page search).
    """
    query = "SELECT * FROM accounts WHERE is_deleted = 0"
    params = []
    
    main_conditions = []
    
    if search_term:
        term = f"%{search_term}%"
        search_cols = ['profile_id', 'account_name', 'uid', 'account_category', 'status', 'monetization', 'proxy', 'proxy_location', 'note']
        search_condition_str = f"({' OR '.join([f'{col} LIKE ?' for col in search_cols])})"
        main_conditions.append(search_condition_str)
        params.extend([term] * len(search_cols))
        
    if account_ids_to_include:
        placeholders = ','.join(['?'] * len(account_ids_to_include))
        main_conditions.append(f"account_id IN ({placeholders})")
        params.extend(account_ids_to_include)

    if main_conditions:
        query += " AND (" + " OR ".join(main_conditions) + ")"

    if account_category_filter and account_category_filter != 'All Categories':
        query += " AND account_category = ?"
        params.append(account_category_filter)

    query += " ORDER BY profile_id"
    if limit:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
    return _execute_query(query, tuple(params), fetch='all')

def get_total_accounts_count(search_term="", account_category_filter=None):
    query = "SELECT COUNT(*) FROM accounts WHERE is_deleted = 0"
    params = []
    conditions = []
    if account_category_filter and account_category_filter != 'All Categories':
        conditions.append("account_category = ?")
        params.append(account_category_filter)
    if search_term:
        term = f"%{search_term}%"
        search_cols = ['profile_id', 'account_name', 'uid', 'account_category', 'status', 'monetization', 'proxy', 'proxy_location', 'note']
        conditions.append(f"({' OR '.join([f'{col} LIKE ?' for col in search_cols])})")
        params.extend([term] * len(search_cols))
    
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    success, result = _execute_query(query, tuple(params), fetch='one')
    if not success:
        return success, result
    return (True, result[0] if result else 0)

def get_all_pages_data(search_term="", page_category_filter=None):
    query = """
        SELECT 
            p.page_id, p.page_name, p.uid_page_id, p.category, p.content_folder, 
            p.used_folders, p.video_schedule_date, p.video_posts_per_day,
            p.reels_schedule_date, p.reels_posts_per_day, p.photo_schedule_date, 
            p.photo_posts_per_day, p.note, p.status, p.monetization, p.is_deleted, 
            p.linked_account_id, p.video_folder, p.reels_folder, p.photo_folder, 
            p.followers, p.last_interaction,
            a.profile_id, a.account_name
        FROM pages p JOIN accounts a ON p.linked_account_id = a.account_id
        WHERE p.is_deleted = 0 AND a.is_deleted = 0
    """
    params = []
    conditions = []
    if page_category_filter and page_category_filter != 'All Categories':
        conditions.append("p.category = ?")
        params.append(page_category_filter)
    if search_term:
        term = f"%{search_term}%"
        search_cols = ['a.profile_id', 'p.page_name', 'p.uid_page_id', 'p.category', 'p.note', 'p.followers', 'p.last_interaction', 'a.account_name']
        conditions.append(f"({' OR '.join([f'{col} LIKE ?' for col in search_cols])})")
        params.extend([term] * len(search_cols))
    if conditions:
        query += " AND " + " AND ".join(conditions)
    query += " ORDER BY a.profile_id, p.page_name"
    return _execute_query(query, tuple(params), fetch='all')

def get_account_details(account_id):
    return _execute_query("SELECT * FROM accounts WHERE account_id = ?", (account_id,), fetch='one')

def get_page_details_for_edit(page_id):
    return _execute_query("SELECT * FROM pages WHERE page_id = ?", (page_id,), fetch='one')

def get_all_accounts():
    query = "SELECT account_id, profile_id, account_name FROM accounts WHERE is_deleted = 0 ORDER BY profile_id"
    return _execute_query(query, fetch='all')

def get_unique_page_categories():
    query = "SELECT DISTINCT category FROM pages WHERE category IS NOT NULL AND category != '' AND is_deleted=0 ORDER BY category"
    success, rows = _execute_query(query, fetch='all')
    if not success: return success, rows
    return (True, [row[0] for row in rows] if rows else [])

def get_unique_account_categories():
    query = "SELECT DISTINCT account_category FROM accounts WHERE account_category IS NOT NULL AND account_category != '' AND is_deleted=0 ORDER BY account_category"
    success, rows = _execute_query(query, fetch='all')
    if not success: return success, rows
    return (True, [row[0] for row in rows] if rows else [])
    
def get_profile_id_map():
    success, rows = _execute_query("SELECT profile_id, account_name FROM accounts WHERE is_deleted = 0", fetch='all')
    if not success: return success, rows
    return (True, {row[0].upper(): (row[0], row[1]) for row in rows} if rows else {})

def get_deleted_items():
    success_acc, accounts = _execute_query("SELECT account_id, profile_id, account_name, 'Account' as type FROM accounts WHERE is_deleted = 1", fetch='all')
    if not success_acc: return success_acc, accounts
    success_pg, pages = _execute_query("SELECT page_id, page_name, '', 'Page' as type FROM pages WHERE is_deleted = 1", fetch='all')
    if not success_pg: return success_pg, pages
    return (True, (accounts or []) + (pages or []))

def get_dependent_pages_count(account_ids):
    if not account_ids:
        return (True, 0)
    query = f"SELECT COUNT(*) FROM pages WHERE linked_account_id IN ({','.join(['?'] * len(account_ids))})"
    success, result = _execute_query(query, tuple(account_ids), fetch='one')
    if not success:
        return success, result
    return (True, result[0] if result else 0)

def check_duplicate(profile_id=None, uid=None):
    if profile_id:
        success, result = _execute_query("SELECT account_id FROM accounts WHERE profile_id = ?", (profile_id,), fetch='one')
        if not success: return success, result
        if result: return (True, "Profile ID")
    if uid and uid.strip() != '':
        success, result = _execute_query("SELECT account_id FROM accounts WHERE uid = ?", (uid,), fetch='one')
        if not success: return success, result
        if result: return (True, "UID")
    return (True, None)

def get_multiple_accounts_details(account_ids):
    if not account_ids: return (True, [])
    query = f"""
        SELECT * FROM accounts 
        WHERE account_id IN ({','.join(['?'] * len(account_ids))})
    """
    return _execute_query(query, tuple(account_ids), fetch='all')

def get_accounts_for_proxy_edit(account_ids):
    if not account_ids: return (True, [])
    query = f"""
        SELECT account_id, profile_id, proxy, proxy_location FROM accounts 
        WHERE account_id IN ({','.join(['?'] * len(account_ids))})
    """
    return _execute_query(query, tuple(account_ids), fetch='all')

def get_multiple_pages_details(page_ids):
    if not page_ids: return (True, [])
    query = f"""
        SELECT p.page_id, p.page_name, p.uid_page_id, p.category, p.monetization, p.linked_account_id, a.profile_id 
        FROM pages p JOIN accounts a ON p.linked_account_id = a.account_id 
        WHERE p.page_id IN ({','.join(['?'] * len(page_ids))})
    """
    return _execute_query(query, tuple(page_ids), fetch='all')