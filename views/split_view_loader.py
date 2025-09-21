# views/split_view_loader.py

from .view_utils import set_item_and_highlight
from utils import log
from PyQt5.QtCore import Qt

def populate_accounts_table(table, accounts_chunk, full_pages_cache, search_text, settings):
    """Populates the accounts table widget in the split view."""
    table.blockSignals(True)
    header_map = {table.horizontalHeaderItem(i).data(Qt.UserRole): i for i in range(table.columnCount())}
    table.setRowCount(0) # Clear table before populating

    for row_index, acc_data in enumerate(accounts_chunk):
        if len(acc_data) < 11:
            log.warning(f"Skipping malformed account data row: {acc_data}")
            continue
        
        table.insertRow(row_index)
        
        (acc_id, profile_id, acc_name, acc_uid, acc_cat, acc_status, acc_mon, 
         acc_proxy, acc_proxy_loc, is_deleted, acc_note) = acc_data
        
        page_count = sum(1 for page in full_pages_cache if page[16] == acc_id)
        
        # --- ALL CALLS NOW CORRECTLY PASS 'settings' ---
        set_item_and_highlight(table, row_index, 'status', acc_status, search_text, header_map, settings, data={'type': 'account', 'id': acc_id}, centered=True, is_account_row=True)
        set_item_and_highlight(table, row_index, 'profile_id', profile_id, search_text, header_map, settings, centered=True, is_account_row=True)
        set_item_and_highlight(table, row_index, 'name', acc_name, search_text, header_map, settings, is_account_row=True)
        set_item_and_highlight(table, row_index, 'page_count', page_count, search_text, header_map, settings, centered=True, is_account_row=True)
        set_item_and_highlight(table, row_index, 'uid', acc_uid, search_text, header_map, settings, centered=True, is_account_row=True)
        set_item_and_highlight(table, row_index, 'account_category', acc_cat, search_text, header_map, settings, centered=True, is_account_row=True)
        set_item_and_highlight(table, row_index, 'proxy', acc_proxy, search_text, header_map, settings, is_account_row=True)
        set_item_and_highlight(table, row_index, 'proxy_location', acc_proxy_loc, search_text, header_map, settings, is_account_row=True)
        set_item_and_highlight(table, row_index, 'note', acc_note, search_text, header_map, settings, is_account_row=True)
    
    table.blockSignals(False)

def populate_pages_table(table, pages_to_show, search_text, settings):
    """Populates the pages table widget in the split view."""
    table.blockSignals(True)
    table.setRowCount(0)
    header_map = {table.horizontalHeaderItem(i).data(Qt.UserRole): i for i in range(table.columnCount())}

    pages_to_show.sort(key=lambda page: (page[22], page[1]))

    for row_index, page_data in enumerate(pages_to_show):
        if len(page_data) < 24:
            log.warning(f"Skipping malformed page data row: {page_data}")
            continue
            
        table.insertRow(row_index)
        
        admin_text = f"{page_data[22]} ({page_data[23]})"

        # --- ALL CALLS NOW CORRECTLY PASS 'settings' ---
        set_item_and_highlight(table, row_index, 'status', page_data[13], search_text, header_map, settings, data={'type': 'page', 'id': page_data[0]}, centered=True)
        set_item_and_highlight(table, row_index, 'name', page_data[1], search_text, header_map, settings)
        set_item_and_highlight(table, row_index, 'admin', admin_text, search_text, header_map, settings)
        set_item_and_highlight(table, row_index, 'uid_page_id', page_data[2], search_text, header_map, settings, centered=True)
        set_item_and_highlight(table, row_index, 'category', page_data[3], search_text, header_map, settings, centered=True)
        set_item_and_highlight(table, row_index, 'monetization', page_data[14], search_text, header_map, settings, centered=True)
        set_item_and_highlight(table, row_index, 'followers', page_data[20], search_text, header_map, settings, centered=True)
        set_item_and_highlight(table, row_index, 'last_interaction', page_data[21], search_text, header_map, settings)
        set_item_and_highlight(table, row_index, 'video_ends', page_data[6], search_text, header_map, settings)
        set_item_and_highlight(table, row_index, 'reels_ends', page_data[8], search_text, header_map, settings)
        set_item_and_highlight(table, row_index, 'photo_ends', page_data[10], search_text, header_map, settings)
        set_item_and_highlight(table, row_index, 'note', page_data[12], search_text, header_map, settings)
        
    table.blockSignals(False)