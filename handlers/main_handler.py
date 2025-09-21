# handlers/main_handler.py

from .dialog_handler import DialogHandler
from .menu_handler import MenuHandler

class UIEventHandler:
    """
    The main event handler. It delegates tasks to specialized sub-handlers.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_widget = main_window.main_widget
        
        # Create instances of sub-handlers
        self.dialog_handler = DialogHandler(main_window)
        self.menu_handler = MenuHandler(main_window, self.dialog_handler)

    def toggle_view(self):
        """Switches between unified and split table views."""
        is_split = self.main_widget.split_view_checkbox.isChecked()
        self.main_widget.view_stack.setCurrentIndex(1 if is_split else 0)
        self.main_widget.show_view_filter.setEnabled(not is_split)
        self.main_window.load_data_into_table()

    # --- Dialog-Related Events (Delegated) ---
    def open_export_dialog(self):
        self.dialog_handler.open_export_dialog()

    def open_import_dialog(self):
        self.dialog_handler.open_import_dialog()

    def open_column_settings_dialog(self):
        self.dialog_handler.open_column_settings_dialog()
    
    def open_add_account_dialog(self):
        self.dialog_handler.open_add_account_dialog()

    def open_bulk_add_pages_dialog(self):
        self.dialog_handler.open_bulk_add_pages_dialog()
        
    def open_edit_dialog(self):
        self.dialog_handler.open_edit_dialog()

    def open_import_accounts_dialog(self):
        self.dialog_handler.open_import_accounts_dialog()
    
    def open_recycle_bin(self):
        self.dialog_handler.open_recycle_bin()
        
    def delete_selected_items(self):
        self.dialog_handler.delete_selected_items()

    # --- Cell-Specific Events (Delegated) ---
    def handle_cell_double_click(self, row, column):
        active_table = self.main_window.sender()
        header_item = active_table.horizontalHeaderItem(column)
        if not header_item: return
        
        col_id = header_item.data(256) # Qt.UserRole
        item_type, item_id = self.main_window.get_item_info_from_row(active_table, row)
        if not item_id: return

        if col_id == 'note':
            self.dialog_handler.open_note_dialog(active_table, row, item_id, item_type)
        elif item_type == 'page' and col_id in ['video_ends', 'reels_ends', 'photo_ends']:
            # MODIFIED: Open the full edit dialog instead of the details dialog
            self.dialog_handler.open_edit_page_dialog(item_id)

    # --- Context Menu Events (Delegated) ---
    def setup_context_menu(self, pos):
        self.menu_handler.setup_context_menu(pos)