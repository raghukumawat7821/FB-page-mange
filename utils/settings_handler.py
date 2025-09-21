# utils/settings_handler.py

import json
import os
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt
from .logger_config import log

SETTINGS_FILE = 'settings.json'

ALL_COLUMNS = {
    'unified': [
        {'id': 'status', 'label': 'Status', 'fixed': True},
        {'id': 'profile_id', 'label': 'Profile ID', 'fixed': True},
        {'id': 'name', 'label': 'Name', 'fixed': True},
        {'id': 'admin', 'label': 'Admin', 'fixed': False},
        {'id': 'page_count', 'label': 'Pages', 'fixed': False},
        {'id': 'followers', 'label': 'Followers', 'fixed': False},
        {'id': 'last_interaction', 'label': 'Last Interaction', 'fixed': False},
        {'id': 'uid_page_id', 'label': 'UID/Page ID', 'fixed': False},
        {'id': 'category', 'label': 'Category', 'fixed': False},
        {'id': 'proxy', 'label': 'Proxy', 'fixed': False},
        {'id': 'proxy_location', 'label': 'Proxy Location', 'fixed': False},
        {'id': 'video_ends', 'label': 'Video Ends', 'fixed': False},
        {'id': 'reels_ends', 'label': 'Reels Ends', 'fixed': False},
        {'id': 'photo_ends', 'label': 'Photo Ends', 'fixed': False},
        {'id': 'note', 'label': 'Note', 'fixed': False}
    ],
    'accounts': [
        {'id': 'status', 'label': 'Status', 'fixed': True},
        {'id': 'profile_id', 'label': 'Profile ID', 'fixed': True},
        {'id': 'name', 'label': 'Name', 'fixed': True},
        {'id': 'page_count', 'label': 'Pages', 'fixed': False},
        {'id': 'uid', 'label': 'UID', 'fixed': False},
        {'id': 'account_category', 'label': 'Category', 'fixed': False},
        {'id': 'proxy', 'label': 'Proxy', 'fixed': False},
        {'id': 'proxy_location', 'label': 'Proxy Location', 'fixed': False},
        {'id': 'note', 'label': 'Note', 'fixed': False}
    ],
    'pages': [
        {'id': 'status', 'label': 'Status', 'fixed': True},
        {'id': 'name', 'label': 'Name', 'fixed': True},
        {'id': 'uid_page_id', 'label': 'UID/Page ID', 'fixed': False},
        {'id': 'admin', 'label': 'Admin', 'fixed': False},
        {'id': 'category', 'label': 'Category', 'fixed': False},
        {'id': 'monetization', 'label': 'Monetization', 'fixed': False},
        {'id': 'followers', 'label': 'Followers', 'fixed': False},
        {'id': 'last_interaction', 'label': 'Last Interaction', 'fixed': False},
        {'id': 'video_ends', 'label': 'Video Ends', 'fixed': False},
        {'id': 'reels_ends', 'label': 'Reels Ends', 'fixed': False},
        {'id': 'photo_ends', 'label': 'Photo Ends', 'fixed': False},
        {'id': 'note', 'label': 'Note', 'fixed': False}
    ]
}

def get_default_settings():
    """Generates the default settings structure including new row colors."""
    settings = {
        "columns": {
            "unified": {
                "order": [col['id'] for col in ALL_COLUMNS['unified']],
                "visible": {col['id']: True for col in ALL_COLUMNS['unified']},
                "widths": {"profile_id": 120, "name": 300, "note": 400, "admin": 250}
            },
            "accounts": {
                "order": [col['id'] for col in ALL_COLUMNS['accounts']],
                "visible": {col['id']: True for col in ALL_COLUMNS['accounts']},
                "widths": {"profile_id": 120, "name": 200, "note": 300}
            },
            "pages": {
                "order": [col['id'] for col in ALL_COLUMNS['pages']],
                "visible": {col['id']: True for col in ALL_COLUMNS['pages']},
                "widths": {"name": 250, "admin": 250, "note": 400}
            }
        },
        "appearance": {
            "header_bg": "#E6D8D8", 
            "row_bg": "#ffffff", 
            "alt_row_bg": "#f7f7f7",
            "selection_bg": "#3b82f6", 
            "note_highlight": "#fff1c2",
            "account_row_bg": "#e6f2ff",  # Light Blue for accounts
            "page_row_bg": "#e6ffe6",      # Light Green for pages
            "font_size": 10,
            "row_height": 25, 
            "compact_mode": False, 
            "use_zebra_striping": True, 
            "show_grid": True
        }
    }
    return settings

def load_settings():
    """Loads settings and migrates new keys if they are missing."""
    if not os.path.exists(SETTINGS_FILE):
        log.info(f"'{SETTINGS_FILE}' not found. Creating with default settings.")
        default_settings = get_default_settings()
        save_settings(default_settings)
        return default_settings
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        
        is_dirty = False
        default_settings = get_default_settings()
        
        if 'appearance' not in settings:
            settings['appearance'] = default_settings['appearance']
            is_dirty = True
        else:
            for key, value in default_settings['appearance'].items():
                if key not in settings['appearance']:
                    settings['appearance'][key] = value
                    is_dirty = True
        
        for view_key, default_view in default_settings['columns'].items():
            if view_key not in settings['columns']:
                settings['columns'][view_key] = default_view
                is_dirty = True
            else:
                for col_id in default_view['order']:
                    if col_id not in settings['columns'][view_key]['order']:
                        settings['columns'][view_key]['order'].append(col_id)
                        settings['columns'][view_key]['visible'][col_id] = True
                        is_dirty = True
        
        if is_dirty:
            log.info("Settings file updated with new keys.")
            save_settings(settings)
        return settings
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load or parse '{SETTINGS_FILE}': {e}. Using defaults.")
        return get_default_settings()

def save_settings(settings):
    """Saves the settings dictionary to settings.json."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        log.info(f"Settings successfully saved to '{SETTINGS_FILE}'.")
    except IOError as e:
        log.error(f"Failed to save settings to '{SETTINGS_FILE}': {e}")

def apply_table_layout(table, settings, view_type):
    """Applies column layout (order, visibility, width) to a table."""
    if view_type not in settings['columns']: return
    view_settings = settings['columns'][view_type]
    header = table.horizontalHeader()
    
    master_ids = [col['id'] for col in ALL_COLUMNS[view_type]]
    order = [col_id for col_id in view_settings.get('order', master_ids) if col_id in master_ids]
    
    id_to_logical_map = {table.horizontalHeaderItem(i).data(Qt.UserRole): i for i in range(table.columnCount())}

    for target_idx, col_id in enumerate(order):
        if col_id in id_to_logical_map:
            current_idx = header.visualIndex(id_to_logical_map[col_id])
            if current_idx != target_idx:
                header.moveSection(current_idx, target_idx)

    visible = view_settings.get('visible', {})
    widths = view_settings.get('widths', {})
    for col_id in master_ids:
        if col_id in id_to_logical_map:
            index = id_to_logical_map[col_id]
            is_visible = visible.get(col_id, True)
            table.setColumnHidden(index, not is_visible)
            if is_visible and col_id in widths:
                table.setColumnWidth(index, widths[col_id])
            header.setSectionResizeMode(index, QHeaderView.Interactive)
    
    if 'note' in id_to_logical_map:
        note_index = id_to_logical_map['note']
        if not table.isColumnHidden(note_index):
            header.setSectionResizeMode(note_index, QHeaderView.Stretch)

def generate_stylesheet(appearance):
    """Generates a QSS stylesheet from appearance settings."""
    return f"""
        QWidget {{ font-size: {appearance.get('font_size', 10)}pt; }}
        QTableWidget {{
            background-color: {appearance.get('row_bg', '#ffffff')};
            alternate-background-color: {appearance.get('alt_row_bg', '#f7f7f7')};
        }}
        QHeaderView::section {{
            background-color: {appearance.get('header_bg', '#f0f0f0')};
            border-bottom: 1px solid #d0d0d0; padding: 4px;
        }}
        QTableWidget::item:selected {{
            background-color: {appearance.get('selection_bg', '#3b82f6')};
            color: white;
        }}
    """