# handlers/utility_dialogs.py

import os
import csv
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog
from PyQt5.QtCore import QDate, Qt
from utils import log, settings_handler
import database as db
from dialogs import (RecycleBinDialog, ConfirmDeleteDialog, ColumnSettingsDialog)


class UtilityDialogHandler:
    """Handles export, import, settings and other utility dialogs"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_widget = main_window.main_widget

    def open_export_dialog(self):
        """Open dialog to export data to CSV files"""
        path, _ = QFileDialog.getSaveFileName(self.main_window, "Save Backup As", "", "CSV Files (*.csv)")
        if not path:
            return
            
        base_path = path[:-4] if path.endswith('.csv') else path
        accounts_path = f"{base_path}_accounts.csv"
        pages_path = f"{base_path}_pages.csv"
        
        try:
            success, headers, data = db.get_table_data_for_export('accounts')
            if not success:
                raise IOError(f"Failed to fetch accounts: {data}")
            with open(accounts_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
            
            success, headers, data = db.get_table_data_for_export('pages')
            if not success:
                raise IOError(f"Failed to fetch pages: {data}")
            with open(pages_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
                
            QMessageBox.information(self.main_window, "Export Successful", 
                                  f"Data backed up to:\n{accounts_path}\n{pages_path}")
        except Exception as e:
            log.error(f"Export error: {e}")
            QMessageBox.critical(self.main_window, "Export Failed", str(e))

    def open_import_dialog(self):
        """Open dialog to import data from CSV backup files"""
        path, _ = QFileDialog.getOpenFileName(self.main_window, "Select Accounts Backup File", 
                                            "", "Accounts CSV (*_accounts.csv)")
        if not path:
            return
            
        accounts_path = path
        pages_path = path.replace("_accounts.csv", "_pages.csv")
        
        if not os.path.exists(pages_path):
            QMessageBox.critical(self.main_window, "Import Failed", 
                               f"Pages file not found at: {pages_path}")
            return
        
        reply = QMessageBox.question(self.main_window, 'Confirm Restore', 
                                   "<b>WARNING:</b> This will delete all current data and replace it with the backup. This is irreversible.\n\nAre you sure?", 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return
        
        try:
            with open(accounts_path, 'r', encoding='utf-8') as f:
                accounts_data = list(csv.DictReader(f))
            with open(pages_path, 'r', encoding='utf-8') as f:
                pages_data = list(csv.DictReader(f))
            
            success, message = db.wipe_and_restore_database(accounts_data, pages_data)
            if not success:
                raise Exception(message)
            
            QMessageBox.information(self.main_window, "Restore Successful", "Data successfully restored.")
            self.main_window.refresh_all_data()
        except Exception as e:
            log.error(f"Import error: {e}")
            QMessageBox.critical(self.main_window, "Import Failed", str(e))

    def open_column_settings_dialog(self):
        """Open column settings dialog"""
        view_type = 'unified'
        if self.main_widget.split_view_checkbox.isChecked():
            view_type = 'pages' if (self.main_widget.pages_table.hasFocus() or 
                                  self.main_widget.pages_table.selectionModel().hasSelection()) else 'accounts'
        
        dialog = ColumnSettingsDialog(self.main_window.settings, view_type, 
                                    settings_handler.ALL_COLUMNS[view_type], self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            self.main_window.settings = dialog.get_updated_settings()
            settings_handler.save_settings(self.main_window.settings)
            self.main_window.refresh_all_data()

    def open_recycle_bin(self):
        """Open recycle bin dialog"""
        success, items = db.get_deleted_items()
        if not success:
            QMessageBox.critical(self.main_window, "DB Error", f"Could not open recycle bin: {items}")
            return
        
        dialog = RecycleBinDialog(items, self.main_window)
        self.main_window.recycle_bin_window = dialog
        result = dialog.exec_()
        selected = dialog.get_selected_items()
        if not selected:
            return
            
        if result == 1:  # Restore
            for item_type, item_id in selected:
                db.restore_item(item_type, item_id)
        elif result == 2:  # Delete Permanently
            self._permanently_delete_items_from_recycle_bin(selected)
        
        self.main_window.refresh_all_data()

    def _permanently_delete_items_from_recycle_bin(self, selected):
        """Permanently delete items from recycle bin"""
        acc_ids = [item[1] for item in selected if item[0] == 'Account']
        page_ids = [item[1] for item in selected if item[0] == 'Page']
        
        dep_pages = 0
        if acc_ids:
            success, count = db.get_dependent_pages_count(acc_ids)
            if success:
                dep_pages = count
            else:
                QMessageBox.critical(self.main_window, "DB Error", f"Could not check dependent pages: {count}")
                return
        
        dialog = ConfirmDeleteDialog(len(acc_ids), len(page_ids), dep_pages, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            success, msg = db.permanently_delete_items(selected)
            if not success:
                QMessageBox.critical(self.main_window, "Delete Error", f"Could not delete items: {msg}")
