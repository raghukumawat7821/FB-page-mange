# views/view_utils.py

from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

def set_item_and_highlight(table, row, col_id, text, search_text, header_map, settings, data=None, centered=False, is_account_row=False):
    """
    A helper function to create, style, highlight, and set a table item.
    It now handles custom row colors for accounts and pages.
    """
    col_index = header_map.get(col_id)
    if col_index is None:
        return

    item = QTableWidgetItem(str(text))
    if data:
        item.setData(Qt.UserRole, data)
    if centered:
        item.setTextAlignment(Qt.AlignCenter)
    
    appearance_settings = settings['appearance']
    use_zebra = appearance_settings.get('use_zebra_striping', True)
    
    # 1. Determine base row color
    if is_account_row:
        base_color = QColor(appearance_settings.get('account_row_bg', '#e6f2ff'))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    else: # It's a page row
        base_color = QColor(appearance_settings.get('page_row_bg', '#e6ffe6'))

    # 2. Apply zebra striping if enabled
    if use_zebra and row % 2 != 0:
        item.setBackground(base_color.darker(105)) 
    else:
        item.setBackground(base_color)

    # 3. Highlight for search results overrides any other color
    if search_text and search_text in item.text().lower():
        item.setBackground(QColor("yellow"))
        
    table.setItem(row, col_index, item)