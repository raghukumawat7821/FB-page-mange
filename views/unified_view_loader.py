# views/unified_view_loader.py

from .view_utils import set_item_and_highlight
from utils import log
from PyQt5.QtCore import Qt

def populate_unified_table(table, accounts_chunk, pages_by_account_id, search_text, show_view, settings):
    """Populates the unified table widget with account and page data."""
    table.blockSignals(True)
    
    header_map = {table.horizontalHeaderItem(i).data(Qt.UserRole): i for i in range(table.columnCount())}

    admin_col_index = header_map.get('admin')
    if admin_col_index is not None:
        is_admin_visible = settings['columns']['unified']['visible'].get('admin', True)
        table.setColumnHidden(admin_col_index, not (show_view == "Only Pages" and is_admin_visible))

    for acc_data in accounts_chunk:
        if len(acc_data) < 11: 
            log.warning(f"Skipping malformed account data row: {acc_data}")
            continue

        (acc_id, profile_id, acc_name, acc_uid, acc_cat, acc_status, acc_mon, 
         acc_proxy, acc_proxy_loc, is_deleted, acc_note) = acc_data
        
        show_account_row = show_view in ["Show All", "Only Accounts"]
        show_page_rows = show_view in ["Show All", "Only Pages"]

        if show_account_row:
            current_row_for_coloring = table.rowCount()
            table.insertRow(current_row_for_coloring)
            page_count = len(pages_by_account_id.get(acc_id, []))
            
            # --- ALL CALLS NOW CORRECTLY PASS 'settings' ---
            set_item_and_highlight(table, current_row_for_coloring, 'status', acc_status, search_text, header_map, settings, data={'type': 'account', 'id': acc_id}, centered=True, is_account_row=True)
            set_item_and_highlight(table, current_row_for_coloring, 'profile_id', profile_id, search_text, header_map, settings, centered=True, is_account_row=True)
            set_item_and_highlight(table, current_row_for_coloring, 'name', acc_name, search_text, header_map, settings, is_account_row=True)
            set_item_and_highlight(table, current_row_for_coloring, 'page_count', page_count, search_text, header_map, settings, centered=True, is_account_row=True)
            set_item_and_highlight(table, current_row_for_coloring, 'uid_page_id', acc_uid, search_text, header_map, settings, centered=True, is_account_row=True)
            set_item_and_highlight(table, current_row_for_coloring, 'category', acc_cat, search_text, header_map, settings, centered=True, is_account_row=True)
            set_item_and_highlight(table, current_row_for_coloring, 'proxy', acc_proxy, search_text, header_map, settings, is_account_row=True)
            set_item_and_highlight(table, current_row_for_coloring, 'proxy_location', acc_proxy_loc, search_text, header_map, settings, is_account_row=True)
            set_item_and_highlight(table, current_row_for_coloring, 'note', acc_note, search_text, header_map, settings, is_account_row=True)
            
            for col_id in ['admin', 'followers', 'last_interaction', 'video_ends', 'reels_ends', 'photo_ends']:
                set_item_and_highlight(table, current_row_for_coloring, col_id, "", "", header_map, settings, is_account_row=True)

        if acc_id in pages_by_account_id and show_page_rows:
            for page_data in pages_by_account_id[acc_id]:
                if len(page_data) < 24:
                    log.warning(f"Skipping malformed page data row: {page_data}")
                    continue
                
                current_row_for_coloring = table.rowCount()
                table.insertRow(current_row_for_coloring)
                
                admin_text = f"{page_data[22]} — {page_data[23]}"
                
                # --- ALL CALLS NOW CORRECTLY PASS 'settings' ---
                set_item_and_highlight(table, current_row_for_coloring, 'status', page_data[13], search_text, header_map, settings, data={'type': 'page', 'id': page_data[0]}, centered=True)
                set_item_and_highlight(table, current_row_for_coloring, 'name', page_data[1], search_text, header_map, settings)
                set_item_and_highlight(table, current_row_for_coloring, 'admin', admin_text, search_text, header_map, settings)
                set_item_and_highlight(table, current_row_for_coloring, 'followers', page_data[20], search_text, header_map, settings, centered=True)
                set_item_and_highlight(table, current_row_for_coloring, 'last_interaction', page_data[21], search_text, header_map, settings)
                set_item_and_highlight(table, current_row_for_coloring, 'uid_page_id', page_data[2], search_text, header_map, settings, centered=True)
                set_item_and_highlight(table, current_row_for_coloring, 'category', page_data[3], search_text, header_map, settings, centered=True)
                set_item_and_highlight(table, current_row_for_coloring, 'video_ends', page_data[6], search_text, header_map, settings)
                set_item_and_highlight(table, current_row_for_coloring, 'reels_ends', page_data[8], search_text, header_map, settings)
                set_item_and_highlight(table, current_row_for_coloring, 'photo_ends', page_data[10], search_text, header_map, settings)
                set_item_and_highlight(table, current_row_for_coloring, 'note', page_data[12], search_text, header_map, settings)

                if show_view == "Only Pages":
                    set_item_and_highlight(table, current_row_for_coloring, 'profile_id', page_data[22], search_text, header_map, settings, centered=True)
                else: 
                    set_item_and_highlight(table, current_row_for_coloring, 'profile_id', "", search_text, header_map, settings)
                
                # Clear account-only columns that are not applicable in this row
                set_item_and_highlight(table, current_row_for_coloring, 'page_count', "", search_text, header_map, settings)
                set_item_and_highlight(table, current_row_for_coloring, 'proxy', "", search_text, header_map, settings)
                set_item_and_highlight(table, current_row_for_coloring, 'proxy_location', "", search_text, header_map, settings)


    table.blockSignals(False)