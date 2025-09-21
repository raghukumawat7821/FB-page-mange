# handlers/menu_handler.py

from PyQt5.QtWidgets import QMenu, QInputDialog, QFileDialog
import database as db

class MenuHandler:
    """Handles the creation and actions of the right-click context menu."""
    def __init__(self, main_window, dialog_handler):
        self.main_window = main_window
        self.dialog_handler = dialog_handler # To call dialog-opening methods

    def setup_context_menu(self, pos):
        selected_items, active_table = self.main_window.get_current_selection_info()
        if not selected_items: return
        
        valid_items = [item for item in selected_items if item and item[0]]
        if not valid_items: return
        
        item_types = {info[0] for info in valid_items}
        menu = QMenu()
        
        # Add actions for single item selection
        if len(valid_items) == 1:
            item_type, item_id = valid_items[0]
            if item_type == 'account':
                menu.addAction("Add Page to this Account...").triggered.connect(lambda: self.dialog_handler.open_add_page_dialog(account_id=item_id))
                menu.addAction("Edit Full Account Details...").triggered.connect(lambda: self.dialog_handler.open_edit_account_dialog(item_id))
            elif item_type == 'page':
                menu.addAction("Edit Full Page Details...").triggered.connect(lambda: self.dialog_handler.open_edit_page_dialog(item_id))
        
        if menu.actions(): menu.addSeparator()

        # Add actions for multi-item selection (Quick Edit)
        quick_edit_menu = menu.addMenu("Quick Edit")
        if 'account' in item_types:
            quick_edit_menu.addAction("Set Category...").triggered.connect(lambda: self._quick_edit('account', 'account_category'))
            quick_edit_menu.addAction("Set Proxies (Bulk)...").triggered.connect(self.dialog_handler.open_bulk_proxy_dialog)
        
        if 'page' in item_types:
            quick_edit_menu.addAction("Set Category...").triggered.connect(lambda: self._quick_edit('page', 'category'))
            quick_edit_menu.addAction("Set Monetization...").triggered.connect(lambda: self._quick_edit('page', 'monetization'))
            quick_edit_menu.addSeparator()
            quick_edit_menu.addAction("Set Video Folder...").triggered.connect(lambda: self._quick_edit_folder('page', 'video_folder'))
            quick_edit_menu.addAction("Set Reels Folder...").triggered.connect(lambda: self._quick_edit_folder('page', 'reels_folder'))
            quick_edit_menu.addAction("Set Photo Folder...").triggered.connect(lambda: self._quick_edit_folder('page', 'photo_folder'))

        if quick_edit_menu.actions():
            menu.exec_(active_table.mapToGlobal(pos))
    
    def _quick_edit_folder(self, item_type, field):
        selected_items, _ = self.main_window.get_current_selection_info()
        item_ids = [info[1] for info in selected_items if info and info[0] == item_type]
        if not item_ids: return

        folder = QFileDialog.getExistingDirectory(self.main_window, f"Select {field.replace('_', ' ').title()} for {len(item_ids)} pages")
        if folder:
            success, message = db.quick_edit_items(item_type, item_ids, field, folder)
            if success: self.main_window.refresh_all_data()
            else: self.main_window.show_error(f"Failed to quick edit:\n{message}")

    def _quick_edit(self, item_type, field):
        selected_items, _ = self.main_window.get_current_selection_info()
        item_ids = [info[1] for info in selected_items if info and info[0] == item_type]
        if not item_ids: return

        text, ok = QInputDialog.getText(self.main_window, f'Quick Edit {field.replace("_", " ").title()}', f'Enter new value for all selected {item_type}s:')
        if ok and text is not None:
            success, message = db.quick_edit_items(item_type, item_ids, field, text)
            if success: self.main_window.refresh_all_data()
            else: self.main_window.show_error(f"Failed to quick edit:\n{message}")