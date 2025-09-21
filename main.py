import sys
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, 
                             QLabel, QStatusBar)
from PyQt5.QtCore import QItemSelectionModel, QTimer
from utils import log, settings_handler
import database as db
from ui_main_window import MainUI
from handlers import UIEventHandler
from views import populate_unified_table, populate_accounts_table, populate_pages_table


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log.critical(f"Unhandled exception caught:\n{error_msg}")
    QMessageBox.critical(None, "Critical Error", "An unexpected error occurred and the application must close.\n\nA detailed error report has been saved to 'tool.log'.")
    sys.exit(1)


class MainWindow(QMainWindow):
    PAGE_SIZE = 100 

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Page Manage Data Tool")
        self.setGeometry(50, 50, 1800, 950)
        
        self.settings = settings_handler.load_settings()
        self.main_widget = MainUI(self.settings)
        self.setCentralWidget(self.main_widget)
        self.recycle_bin_window = None
        
        self.event_handler = UIEventHandler(self)
        
        self._full_pages_cache = []
        self._accounts_with_pages_loaded = set()
        
        self._current_offset_unified = 0
        self._total_accounts_unified = 0
        self._is_loading_unified = False
        self._current_offset_accounts = 0
        self._total_accounts_split = 0
        self._is_loading_accounts = False
        
        self.setup_status_bar()
        self.setup_connections()
        self.apply_styles()
        self.refresh_all_data()
        
        # ADDED: Initial grid setup after UI is fully loaded
        QTimer.singleShot(1000, self.refresh_ui_grids)

    # ADDED: Grid refresh method for all tables
    def refresh_ui_grids(self):
        """Refresh grid lines after data loading to ensure visibility"""
        try:
            if hasattr(self, 'main_widget') and self.main_widget:
                if hasattr(self.main_widget, 'refresh_all_table_grids'):
                    QTimer.singleShot(300, self.main_widget.refresh_all_table_grids)
                    log.info("Grid refresh scheduled for all tables")
                else:
                    log.warning("refresh_all_table_grids method not found on main_widget")
            else:
                log.warning("main_widget is not initialized")
        except Exception as e:
            log.error(f"Exception while scheduling grid refresh: {e}")

    def setup_connections(self):
        eh = self.event_handler
        
        self.main_widget.search_input.textChanged.connect(self.load_data_into_table)
        self.main_widget.page_category_filter.currentIndexChanged.connect(self.load_data_into_table)
        self.main_widget.account_category_filter.currentIndexChanged.connect(self.load_data_into_table)
        self.main_widget.show_view_filter.currentIndexChanged.connect(self.load_data_into_table)
        self.main_widget.split_view_checkbox.stateChanged.connect(eh.toggle_view)
        
        self.main_widget.import_accounts_btn.clicked.connect(eh.open_import_accounts_dialog)
        self.main_widget.export_backup_btn.clicked.connect(eh.open_export_dialog)
        self.main_widget.import_backup_btn.clicked.connect(eh.open_import_dialog)
        self.main_widget.bulk_add_pages_btn.clicked.connect(eh.open_bulk_add_pages_dialog)
        self.main_widget.edit_btn.clicked.connect(eh.open_edit_dialog)
        self.main_widget.delete_btn.clicked.connect(eh.delete_selected_items)
        self.main_widget.recycle_bin_btn.clicked.connect(eh.open_recycle_bin)
        self.main_widget.refresh_btn.clicked.connect(self.refresh_all_data)
        
        from PyQt5.QtWidgets import QMenu
        settings_menu = QMenu(self)
        settings_menu.addAction("Column Settings...").triggered.connect(eh.open_column_settings_dialog)
        self.main_widget.settings_btn.setMenu(settings_menu)
        
        self.main_widget.unified_table.customContextMenuRequested.connect(eh.setup_context_menu)
        self.main_widget.unified_table.cellDoubleClicked.connect(eh.handle_cell_double_click)
        self.main_widget.unified_table.itemSelectionChanged.connect(self.update_status_bar)
        self.main_widget.unified_table.verticalScrollBar().valueChanged.connect(self._on_unified_scroll)

        self.main_widget.accounts_table.customContextMenuRequested.connect(eh.setup_context_menu)
        self.main_widget.accounts_table.itemSelectionChanged.connect(self.on_account_selected)
        self.main_widget.accounts_table.itemSelectionChanged.connect(self.update_status_bar)
        self.main_widget.accounts_table.cellDoubleClicked.connect(eh.handle_cell_double_click)
        self.main_widget.accounts_table.verticalScrollBar().valueChanged.connect(self._on_accounts_scroll)

        self.main_widget.pages_table.customContextMenuRequested.connect(eh.setup_context_menu)
        self.main_widget.pages_table.cellDoubleClicked.connect(eh.handle_cell_double_click)
        self.main_widget.pages_table.itemSelectionChanged.connect(self.update_status_bar)
        
        self.main_widget.get_pages_btn.clicked.connect(self.load_selected_account_pages)

    def setup_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.total_accounts_label = QLabel("Total Accounts: 0")
        self.total_pages_label = QLabel("Total Pages: 0")
        self.selection_label = QLabel("Selected: 0")
        self.statusBar.addPermanentWidget(self.total_accounts_label)
        self.statusBar.addPermanentWidget(QLabel(" | "))
        self.statusBar.addPermanentWidget(self.total_pages_label)
        self.statusBar.addPermanentWidget(QLabel(" | "))
        self.statusBar.addPermanentWidget(self.selection_label)

    def apply_styles(self):
        """ENHANCED apply styles with grid support"""
        stylesheet = settings_handler.generate_stylesheet(self.settings['appearance'])
        self.setStyleSheet(stylesheet)
        
        show_grid = self.settings['appearance'].get('show_grid', True)
        use_zebra = self.settings['appearance'].get('use_zebra_striping', True)
        
        # Apply basic table settings (detailed grid styling is handled in ui_main_window.py)
        for table in [self.main_widget.unified_table, self.main_widget.accounts_table, self.main_widget.pages_table]:
            table.setShowGrid(show_grid)
            table.setAlternatingRowColors(use_zebra)
        
        # ADDED: Schedule grid refresh to ensure visibility
        QTimer.singleShot(500, self.refresh_ui_grids)

    def refresh_all_data(self):
        """ENHANCED refresh all data with grid refresh"""
        if self.recycle_bin_window:
            self.recycle_bin_window.close()
            self.recycle_bin_window = None
        self.main_widget.search_input.clear()
        self._accounts_with_pages_loaded.clear()
        
        if self._load_pages_to_cache():
            self.populate_filters()
            settings_handler.apply_table_layout(self.main_widget.unified_table, self.settings, 'unified')
            settings_handler.apply_table_layout(self.main_widget.accounts_table, self.settings, 'accounts')
            settings_handler.apply_table_layout(self.main_widget.pages_table, self.settings, 'pages')
            self.load_data_into_table()
            
            # ADDED: Grid refresh after complete refresh
            self.refresh_ui_grids()

    def populate_filters(self):
        self.main_widget.page_category_filter.blockSignals(True)
        current_page_cat = self.main_widget.page_category_filter.currentText()
        self.main_widget.page_category_filter.clear()
        self.main_widget.page_category_filter.addItem("All Categories")
        page_categories = sorted(list(set(p[3] for p in self._full_pages_cache if p[3])))
        self.main_widget.page_category_filter.addItems(page_categories)
        idx = self.main_widget.page_category_filter.findText(current_page_cat)
        if idx != -1: self.main_widget.page_category_filter.setCurrentIndex(idx)
        self.main_widget.page_category_filter.blockSignals(False)

        self.main_widget.account_category_filter.blockSignals(True)
        current_acc_cat = self.main_widget.account_category_filter.currentText()
        self.main_widget.account_category_filter.clear()
        self.main_widget.account_category_filter.addItem("All Categories")
        success, acc_categories = db.get_unique_account_categories()
        if success: self.main_widget.account_category_filter.addItems(acc_categories)
        idx = self.main_widget.account_category_filter.findText(current_acc_cat)
        if idx != -1: self.main_widget.account_category_filter.setCurrentIndex(idx)
        self.main_widget.account_category_filter.blockSignals(False)

    def _load_pages_to_cache(self):
        log.info("Caching all pages from database...")
        success, all_pages = db.get_all_pages_data()
        if not success:
            QMessageBox.critical(self, "Database Error", f"Failed to load pages into cache:\n{all_pages}")
            return False
        self._full_pages_cache = all_pages
        log.info(f"Page caching complete. {len(all_pages)} pages.")
        return True

    def _filter_pages_from_cache(self):
        search_text = self.main_widget.search_input.text().lower()
        page_category = self.main_widget.page_category_filter.currentText()
        
        filtered_pages = []
        if search_text:
            for page in self._full_pages_cache:
                search_fields = list(page[1:5]) + [page[6], page[12], page[13], page[17], page[18], page[20], page[21]]
                if any(search_text in str(field or '').lower() for field in search_fields):
                    filtered_pages.append(page)
        else:
            filtered_pages = self._full_pages_cache

        final_pages = [p for p in filtered_pages if page_category == 'All Categories' or p[3] == page_category]

        pages_by_account_id = {}
        for page_row in final_pages:
            acc_id = page_row[16]
            pages_by_account_id.setdefault(acc_id, []).append(page_row)
            
        account_ids_from_page_matches = {p[16] for p in final_pages if search_text}
        return pages_by_account_id, account_ids_from_page_matches

    def load_data_into_table(self):
        if self.main_widget.split_view_checkbox.isChecked():
            self.load_split_view(is_new_load=True)
        else:
            self.load_unified_view(is_new_load=True)

    def update_status_bar(self):
        total_accounts_displayed = 0
        if self.main_widget.split_view_checkbox.isChecked():
            total_accounts_displayed = self.main_widget.accounts_table.rowCount()
        else:
            total_accounts_displayed = self._total_accounts_unified

        selection_count = 0
        if self.main_widget.split_view_checkbox.isChecked():
            selection_count += len(self.main_widget.accounts_table.selectionModel().selectedRows())
            selection_count += len(self.main_widget.pages_table.selectionModel().selectedRows())
        else:
            selection_count = len(self.main_widget.unified_table.selectionModel().selectedRows())

        self.total_accounts_label.setText(f"Accounts Displayed: {total_accounts_displayed}")
        self.total_pages_label.setText(f"Total Pages in DB: {len(self._full_pages_cache)}")
        self.selection_label.setText(f"Selected: {selection_count}")

    def load_unified_view(self, is_new_load=False):
        """ENHANCED unified view loading with grid refresh"""
        if self._is_loading_unified and not is_new_load: return
        self._is_loading_unified = True

        table = self.main_widget.unified_table
        if is_new_load:
            table.setRowCount(0)
            self._current_offset_unified = 0
        
        search_text = self.main_widget.search_input.text().lower()
        account_category = self.main_widget.account_category_filter.currentText()
        show_view = self.main_widget.show_view_filter.currentText()
        
        pages_by_account_id, account_ids_from_page_search = self._filter_pages_from_cache()
        
        success, accounts_chunk = db.get_all_accounts_data(search_text, account_category, self.PAGE_SIZE, self._current_offset_unified, account_ids_from_page_search)
        if not success:
            QMessageBox.critical(self, "Database Error", f"Failed to load accounts:\n{accounts_chunk}")
            self._is_loading_unified = False; return

        if is_new_load:
            self._total_accounts_unified = len(accounts_chunk)

        populate_unified_table(table, accounts_chunk, pages_by_account_id, search_text, show_view, self.settings)

        self._current_offset_unified += len(accounts_chunk)
        self.update_status_bar()
        self._is_loading_unified = False
        
        # ADDED: Grid refresh after data loading
        self.refresh_ui_grids()

    def load_split_view(self, is_new_load=False):
        """ENHANCED split view loading with grid refresh"""
        if self._is_loading_accounts and not is_new_load: return
        self._is_loading_accounts = True

        accounts_table = self.main_widget.accounts_table
        pages_table = self.main_widget.pages_table
        
        if is_new_load:
            accounts_table.setRowCount(0)
            self._current_offset_accounts = 0
        
        search_text = self.main_widget.search_input.text().lower()
        account_category = self.main_widget.account_category_filter.currentText()
        page_category = self.main_widget.page_category_filter.currentText()

        _, account_ids_from_page_matches = self._filter_pages_from_cache()
        
        success, accounts_chunk = db.get_all_accounts_data(search_text, account_category, self.PAGE_SIZE, self._current_offset_accounts, account_ids_from_page_matches)
        if not success:
            QMessageBox.critical(self, "Database Error", f"Failed to load accounts:\n{accounts_chunk}")
            self._is_loading_accounts = False; return
        
        populate_accounts_table(accounts_table, accounts_chunk, self._full_pages_cache, search_text, self.settings)
        
        pages_to_show = []
        visible_account_ids = {self.get_item_info_from_row(accounts_table, r)[1] for r in range(accounts_table.rowCount())}
        
        for page in self._full_pages_cache:
            page_account_id = page[16]
            if (page_account_id in self._accounts_with_pages_loaded and
                page_account_id in visible_account_ids and
                (page_category == "All Categories" or page[3] == page_category)):
                
                if search_text:
                    search_fields = list(page[1:5]) + [page[6], page[12], page[13], page[17], page[18], page[20], page[21]]
                    if any(search_text in str(field or '').lower() for field in search_fields):
                        pages_to_show.append(page)
                else:
                    pages_to_show.append(page)

        populate_pages_table(pages_table, pages_to_show, search_text, self.settings)
        
        self._current_offset_accounts += len(accounts_chunk)
        self.update_status_bar()
        self._is_loading_accounts = False
        
        # ADDED: Grid refresh after data loading
        self.refresh_ui_grids()

    def load_selected_account_pages(self):
        """ENHANCED selected account pages loading with grid refresh"""
        selected_rows = self.main_widget.accounts_table.selectionModel().selectedRows()
        if not selected_rows: 
            self.main_widget.pages_table.setRowCount(0)
            return

        selected_account_ids = {self.get_item_info_from_row(self.main_widget.accounts_table, r.row())[1] for r in selected_rows}
        self._accounts_with_pages_loaded.update(selected_account_ids)
        
        self.load_split_view(is_new_load=True)
        
        # ADDED: Grid refresh after loading selected pages
        self.refresh_ui_grids()

    def _on_unified_scroll(self, value):
        scrollbar = self.main_widget.unified_table.verticalScrollBar()
        if value >= scrollbar.maximum() - 20:
            if not self._is_loading_unified and self._current_offset_unified < self._total_accounts_unified:
                self.load_unified_view(is_new_load=False)

    def _on_accounts_scroll(self, value):
        scrollbar = self.main_widget.accounts_table.verticalScrollBar()
        if value >= scrollbar.maximum() - 20:
            if not self._is_loading_accounts and self._current_offset_accounts < self._total_accounts_split:
                self.load_split_view(is_new_load=False)
    
    def on_account_selected(self):
        has_selection = bool(self.main_widget.accounts_table.selectionModel().selectedRows())
        self.main_widget.get_pages_btn.setVisible(has_selection)

    def get_current_selection_info(self):
        if self.main_widget.split_view_checkbox.isChecked():
            active_table = self.main_widget.pages_table if self.main_widget.pages_table.hasFocus() or self.main_widget.pages_table.selectionModel().hasSelection() else self.main_widget.accounts_table
        else:
            active_table = self.main_widget.unified_table
        
        selected_rows = active_table.selectionModel().selectedRows()
        if not selected_rows: return None, None
        
        selected_items = [self.get_item_info_from_row(active_table, index.row()) for index in selected_rows]
        return selected_items, active_table

    def get_item_info_from_row(self, table, row):
        item = table.item(row, 0)
        if item and item.data(256): # Qt.UserRole
            data = item.data(256)
            return data.get('type'), data.get('id')
        return None, None


if __name__ == "__main__":
    sys.excepthook = handle_exception
    log.info("====================================")
    log.info("Application starting...")
    
    db.create_tables()
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    main_win = MainWindow()
    main_win.show()
    
    sys.exit(app.exec_())
