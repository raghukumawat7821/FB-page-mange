# database/write.py

import json
from utils import log
from .connection import _execute_query, create_connection
from .read import get_all_accounts

def wipe_and_restore_database(accounts_data, pages_data):
    """Wipes all data and restores it from provided lists of dictionaries."""
    conn = create_connection()
    if not conn: return (False, "Database connection failed.")
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION;")
        cursor.execute("DELETE FROM pages;")
        cursor.execute("DELETE FROM accounts;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('accounts', 'pages');")

        if accounts_data:
            acc_headers = accounts_data[0].keys()
            acc_query = f"INSERT INTO accounts ({', '.join(acc_headers)}) VALUES ({', '.join(['?'] * len(acc_headers))})"
            acc_rows = [tuple(row.values()) for row in accounts_data]
            cursor.executemany(acc_query, acc_rows)

        if pages_data:
            pg_headers = pages_data[0].keys()
            pg_query = f"INSERT INTO pages ({', '.join(pg_headers)}) VALUES ({', '.join(['?'] * len(pg_headers))})"
            pg_rows = [tuple(row.values()) for row in pages_data]
            cursor.executemany(pg_query, pg_rows)

        conn.commit()
        return (True, "Restore successful.")
    except Exception as e:
        log.error(f"Database restore failed: {e}")
        conn.rollback()
        return (False, str(e))
    finally:
        if conn: conn.close()
            
def add_account(data):
    name = data['account_name'].strip().title()
    category = data.get('category', '').strip().title()
    query = "INSERT INTO accounts (profile_id, account_name, uid, account_category, status) VALUES (?, ?, ?, ?, 'Created')"
    params = (data['profile_id'], name, data['uid'], category)
    return _execute_query(query, params, commit=True)

def add_page(details):
    name = details['page_name'].strip().title()
    category = details.get('category', '').strip().title()
    query = "INSERT INTO pages (page_name, uid_page_id, category, monetization, linked_account_id, status) VALUES (?, ?, ?, ?, ?, 'Created')"
    params = (name, details['uid_page_id'], category, details.get('monetization', ''), details['linked_account_id'])
    return _execute_query(query, params, commit=True)

def bulk_add_pages(pages_data):
    success, all_accounts = get_all_accounts()
    if not success: return success, all_accounts
    
    profile_id_map = {acc[1].upper(): acc[0] for acc in all_accounts}
    pages_to_add = []
    for page in pages_data:
        profile_id = page['profile_id'].upper()
        if profile_id in profile_id_map:
            account_id = profile_id_map[profile_id]
            name = page['page_name'].strip().title()
            category = page.get('category', '').strip().title()
            pages_to_add.append((name, page.get('uid_page_id', ''), category, account_id, 'Created'))

    if not pages_to_add: return (False, "No valid accounts found for the given Profile IDs.")
    query = "INSERT INTO pages (page_name, uid_page_id, category, linked_account_id, status) VALUES (?, ?, ?, ?, ?)"
    return _execute_query(query, pages_to_add, commit=True, executemany=True)

def bulk_import_accounts(records):
    keys = ['profile_id', 'account_name', 'uid', 'account_category', 'proxy', 'proxy_location', 'monetization', 'note']
    processed = []
    for rec in records:
        if not rec.get('profile_id') or not rec.get('account_name'): continue
        clean = {key: rec.get(key, '').strip() for key in keys}
        clean['account_name'] = clean['account_name'].title()
        clean['account_category'] = clean['account_category'].title()
        processed.append(clean)

    if not processed: return (False, "No valid records to import.")
    query = """
        INSERT OR IGNORE INTO accounts (profile_id, account_name, uid, account_category, proxy, proxy_location, monetization, status, note) 
        VALUES (:profile_id, :account_name, :uid, :account_category, :proxy, :proxy_location, :monetization, 'Imported', :note)
    """
    return _execute_query(query, processed, commit=True, executemany=True)

def update_account_details(account_id, details):
    details['account_name'] = details['account_name'].strip().title()
    details['account_category'] = details['account_category'].strip().title()
    query = "UPDATE accounts SET account_name = ?, account_category = ?, monetization = ?, proxy = ?, proxy_location = ?, note = ?, status = 'Details Updated' WHERE account_id = ?"
    params = (details['account_name'], details['account_category'], details.get('monetization', ''), details.get('proxy', ''), details.get('proxy_location', ''), details.get('note', ''), account_id)
    return _execute_query(query, params, commit=True)

def bulk_update_accounts_partial(updates):
    # This function requires a direct connection for transaction management
    conn = create_connection()
    if not conn: return (False, "Database connection failed.")
    try:
        cursor = conn.cursor()
        for item_update in updates:
            if len(item_update) <= 1: continue
            account_id = item_update.pop('account_id')
            if 'account_category' in item_update:
                item_update['account_category'] = item_update.get('account_category', '').strip().title()

            fields = [f"{key} = ?" for key in item_update.keys()]
            params = list(item_update.values()) + [account_id]
            query = f"UPDATE accounts SET {', '.join(fields)}, status = 'Bulk Updated' WHERE account_id = ?"
            cursor.execute(query, tuple(params))
        conn.commit()
        return (True, f"{len(updates)} accounts processed.")
    except Exception as e:
        conn.rollback()
        return (False, str(e))
    finally:
        if conn: conn.close()

def update_page_details(page_id, details):
    details['status'] = 'Details Updated'
    if 'page_name' in details: details['page_name'] = details['page_name'].strip().title()
    if 'category' in details: details['category'] = details['category'].strip().title()
    if 'used_folders' in details and isinstance(details['used_folders'], list):
        details['used_folders'] = json.dumps(details['used_folders'])
    
    set_clause = ", ".join([f"{key} = ?" for key in details.keys()])
    params = list(details.values()) + [page_id]
    query = f"UPDATE pages SET {set_clause} WHERE page_id = ?"
    return _execute_query(query, tuple(params), commit=True)

def update_page_note(page_id, note):
    query = "UPDATE pages SET note = ?, status = 'Note Saved' WHERE page_id = ?"
    return _execute_query(query, (note, page_id), commit=True)

def update_account_note(account_id, note):
    query = "UPDATE accounts SET note = ?, status = 'Note Saved' WHERE account_id = ?"
    return _execute_query(query, (note, account_id), commit=True)

def soft_delete(item_type, item_id):
    table = 'accounts' if item_type == 'account' else 'pages'
    column = 'account_id' if item_type == 'account' else 'page_id'
    query = f"UPDATE {table} SET is_deleted = 1, status = 'Deleted' WHERE {column} = ?"
    return _execute_query(query, (item_id,), commit=True)

def restore_item(item_type, item_id):
    table = 'accounts' if item_type == 'Account' else 'pages'
    column = 'account_id' if item_type == 'Account' else 'page_id'
    query = f"UPDATE {table} SET is_deleted = 0, status = 'Restored' WHERE {column} = ?"
    return _execute_query(query, (item_id,), commit=True)

def permanently_delete_items(items_to_delete):
    conn = create_connection()
    if not conn: return (False, "Database connection failed.")
    try:
        cursor = conn.cursor()
        for item_type, item_id in items_to_delete:
            table = 'accounts' if item_type == 'Account' else 'pages'
            column = 'account_id' if item_type == 'Account' else 'page_id'
            cursor.execute(f"DELETE FROM {table} WHERE {column} = ?", (item_id,))
        conn.commit()
        return (True, "Items deleted.")
    except Exception as e:
        conn.rollback()
        return (False, str(e))
    finally:
        if conn: conn.close()

def quick_edit_items(item_type, item_ids, field, value):
    table = 'accounts' if item_type == 'account' else 'pages'
    col_id = 'account_id' if item_type == 'account' else 'page_id'
    if field in ['account_category', 'category', 'page_name', 'account_name']:
        value = value.strip().title()
    placeholders = ','.join(['?'] * len(item_ids))
    query = f"UPDATE {table} SET {field} = ?, status = 'Quick Updated' WHERE {col_id} IN ({placeholders})"
    params = [value] + item_ids
    return _execute_query(query, tuple(params), commit=True)

def bulk_update_pages_partial(updates):
    conn = create_connection()
    if not conn: return (False, "Database connection failed.")
    try:
        cursor = conn.cursor()
        for item in updates:
            if len(item) <= 1: continue
            page_id = item.pop('page_id')
            if 'page_name' in item: item['page_name'] = item['page_name'].strip().title()
            if 'category' in item: item['category'] = item['category'].strip().title()
            
            fields = [f"{key} = ?" for key in item.keys()]
            params = list(item.values()) + [page_id]
            query = f"UPDATE pages SET {', '.join(fields)}, status = 'Bulk Updated' WHERE page_id = ?"
            cursor.execute(query, tuple(params))
        conn.commit()
        return (True, f"{len(updates)} pages processed.")
    except Exception as e:
        conn.rollback()
        return (False, str(e))
    finally:
        if conn: conn.close()