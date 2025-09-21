# handlers/dialog_handler.py

import os
import csv
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog
from PyQt5.QtCore import QDate, Qt
from utils import log, settings_handler
import database as db
from dialogs import (AddAccountDialog, AddPageDialog, EditPageDialog, 
                     ImportAccountsDialog, RecycleBinDialog, EditAccountDialog,
                     AdvancedBulkAddPagesDialog, BulkEditAccountsDialog,
                     BulkEditPagesDialog, BulkProxyDialog, NoteDialog, ConfirmDeleteDialog,
                     ColumnSettingsDialog, ScheduleDetailDialog)


class DialogHandler:
    """Handles the logic for creating, showing, and processing all dialog boxes."""
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_widget = main_window.main_widget

    def open_export_dialog(self):
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

    def open_note_dialog(self, table, row, item_id, item_type):
        header_map = {table.horizontalHeaderItem(i).data(256): i for i in range(table.columnCount())}
        note_col_index = header_map.get('note')
        current_note = (table.item(row, note_col_index).text() 
                       if note_col_index is not None and table.item(row, note_col_index) else "")
        
        dialog = NoteDialog(current_note, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            handler = db.update_account_note if item_type == 'account' else db.update_page_note
            success, msg = handler(item_id, dialog.get_note())
            if success:
                self.main_window.refresh_all_data()
            else:
                QMessageBox.critical(self.main_window, "DB Error", f"Failed to update note: {msg}")

    # FIXED: Handle schedule column double clicks - SINGLE DIALOG ONLY
    def handle_schedule_double_click(self, table, row, column):
        """FIXED: Only open schedule detail dialog, no chaining - SINGLE POPUP"""
        try:
            # Get column header to determine content type
            header_text = table.horizontalHeaderItem(column).text()
            
            # Determine content type from header
            content_type = None
            if 'Video Ends' in header_text:
                content_type = 'video'
            elif 'Reels Ends' in header_text:
                content_type = 'reels'  
            elif 'Photo Ends' in header_text:
                content_type = 'photo'
            else:
                return  # Not a schedule column
            
            # Get page info from row
            page_info = self.get_page_info_from_table_row(table, row)
            if not page_info:
                QMessageBox.warning(self.main_window, "Error", "Could not retrieve page information.")
                return
            
            # CRITICAL FIX: Only open schedule detail dialog
            # DO NOT CHAIN ANY OTHER DIALOG - SINGLE POPUP ONLY
            dialog = ScheduleDetailDialog(page_info, content_type, self.main_window)
            dialog.exec_()  # Just show dialog, handle save internally
            
            # Note: ScheduleDetailDialog handles its own save operations
            # No need to refresh here as dialog does it internally
                
        except Exception as e:
            log.error(f"Error handling schedule double click: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to open schedule details: {str(e)}")

    def get_page_info_from_table_row(self, table, row):
        """Extract page information from table row"""
        try:
            # Get page ID from the row
            page_id = None
            
            # Try to get page ID from item data
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and item.data(Qt.UserRole):
                    data = item.data(Qt.UserRole)
                    if isinstance(data, dict) and 'id' in data:
                        page_id = data['id']
                        break
            
            if not page_id:
                # Fallback: try to get from main window method
                item_info = self.main_window.get_item_info_from_row(table, row)
                if item_info and len(item_info) > 1:
                    page_id = item_info[1]
            
            if not page_id:
                return None
            
            # Get page details from database
            success, details = db.get_page_details_for_edit(page_id)
            if not success:
                log.error(f"Failed to get page details: {details}")
                return None
            
            # Convert to dictionary format expected by dialog
            cols = ['page_id', 'page_name', 'uid_page_id', 'category', 'content_folder', 'used_folders', 
                   'video_schedule_date', 'video_posts_per_day', 'reels_schedule_date', 'reels_posts_per_day', 
                   'photo_schedule_date', 'photo_posts_per_day', 'note', 'status', 'monetization', 'is_deleted', 
                   'linked_account_id', 'video_folder', 'reels_folder', 'photo_folder', 'followers', 'last_interaction']
            
            page_data = dict(zip(cols, details))
            return page_data
            
        except Exception as e:
            log.error(f"Error getting page info from table row: {e}")
            return None

    def open_add_account_dialog(self):
        dialog = AddAccountDialog(self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['profile_id'] or not data['account_name']:
                QMessageBox.warning(self.main_window, "Input Error", "Profile ID and Account Name are required.")
                return
            success, field = db.check_duplicate(data['profile_id'], data['uid'])
            if not success or field:
                QMessageBox.critical(self.main_window, "Error", f"This {field} already exists." if field else "DB Error.")
                return
            success, msg = db.add_account(data)
            if success:
                self.main_window.refresh_all_data()
            else:
                QMessageBox.critical(self.main_window, "DB Error", f"Could not add account: {msg}")

    def open_add_page_dialog(self, account_id=None):
        success, accounts = db.get_all_accounts()
        if not success:
            QMessageBox.critical(self.main_window, "DB Error", f"Could not load accounts: {accounts}")
            return
        if not accounts:
            QMessageBox.warning(self.main_window, "No Accounts", "Please add an account first.")
            return
        
        dialog = AddPageDialog(accounts, account_id, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['page_name']:
                QMessageBox.warning(self.main_window, "Input Error", "Page Name is required.")
                return
            success, msg = db.add_page(data)
            if success:
                self.main_window.refresh_all_data()
            else:
                QMessageBox.critical(self.main_window, "DB Error", f"Failed to add page: {msg}")

    def open_edit_dialog(self):
        if self.main_widget.split_view_checkbox.isChecked():
            page_rows = self.main_widget.pages_table.selectionModel().selectedRows()
            if page_rows:
                ids = [self.main_window.get_item_info_from_row(self.main_widget.pages_table, r.row())[1] 
                      for r in page_rows 
                      if self.main_window.get_item_info_from_row(self.main_widget.pages_table, r.row())[1]]
                if len(ids) == 1:
                    self.open_edit_page_dialog(ids[0])
                elif len(ids) > 1:
                    self.open_bulk_edit_pages_dialog(ids)
                return

        items, _ = self.main_window.get_current_selection_info()
        if not items:
            QMessageBox.warning(self.main_window, "Selection Error", "Please select an item to edit.")
            return
        
        types = {info[0] for info in items if info and info[0]}
        ids = [info[1] for info in items if info and info[1]]
        if len(types) > 1:
            QMessageBox.warning(self.main_window, "Selection Error", "Select only accounts or only pages.")
            return
        
        item_type = types.pop()
        if item_type == 'account':
            if len(ids) == 1:
                self.open_edit_account_dialog(ids[0])
            else:
                self.open_bulk_edit_accounts_dialog(ids)
        elif item_type == 'page':
            if len(ids) == 1:
                self.open_edit_page_dialog(ids[0])
            else:
                self.open_bulk_edit_pages_dialog(ids)

    def open_edit_account_dialog(self, account_id):
        success, data = db.get_account_details(account_id)
        if not success:
            QMessageBox.critical(self.main_window, "DB Error", f"Failed to fetch details: {data}")
            return
        dialog = EditAccountDialog(data, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            if not updated['account_name']:
                QMessageBox.warning(self.main_window, "Input Error", "Account Name is required.")
                return
            success, msg = db.update_account_details(account_id, updated)
            if success:
                self.main_window.refresh_all_data()
            else:
                QMessageBox.critical(self.main_window, "DB Error", f"Failed to update: {msg}")

    def open_bulk_edit_accounts_dialog(self, account_ids):
        success, data = db.get_multiple_accounts_details(account_ids)
        if not success:
            QMessageBox.warning(self.main_window, "Error", f"Could not fetch details: {data}")
            return
        success, cats = db.get_unique_account_categories()
        
        dialog = BulkEditAccountsDialog(data, cats if success else [], self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            if not updated:
                return
            success, msg = db.bulk_update_accounts_partial(updated)
            if success:
                self.main_window.refresh_all_data()
            else:
                QMessageBox.critical(self.main_window, "DB Error", f"Failed to bulk update: {msg}")

    def open_edit_page_dialog(self, page_id):
        success, details = db.get_page_details_for_edit(page_id)
        if not success:
            QMessageBox.critical(self.main_window, "DB Error", f"Failed to fetch details: {details}")
            return
        
        cols = ['page_id', 'page_name', 'uid_page_id', 'category', 'content_folder', 'used_folders', 
               'video_schedule_date', 'video_posts_per_day', 'reels_schedule_date', 'reels_posts_per_day', 
               'photo_schedule_date', 'photo_posts_per_day', 'note', 'status', 'monetization', 'is_deleted', 
               'linked_account_id', 'video_folder', 'reels_folder', 'photo_folder', 'followers', 'last_interaction']
        data = dict(zip(cols, details))
        
        dialog = EditPageDialog(data, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            if not updated['page_name']:
                QMessageBox.warning(self.main_window, "Input Error", "Page Name is required.")
                return
            success, msg = db.update_page_details(page_id, updated)
            if success:
                self.main_window.refresh_all_data()
            else:
                QMessageBox.critical(self.main_window, "Update Error", f"Failed to update page: {msg}")

    def open_bulk_add_pages_dialog(self):
        success, profile_map = db.get_profile_id_map()
        if not success:
            QMessageBox.critical(self.main_window, "DB Error", f"Could not load profiles: {profile_map}")
            return
        
        page_cats = sorted(list(set(p[3] for p in self.main_window._full_pages_cache if p[3])))
        dialog = AdvancedBulkAddPagesDialog(profile_map, page_cats, self.main_window)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data:
                return
            success, msg = db.bulk_add_pages(data)
            if success:
                self.main_window.refresh_all_data()
            else:
                QMessageBox.critical(self.main_window, "DB Error", f"Failed to add pages: {msg}")

    def open_bulk_edit_pages_dialog(self, page_ids):
        success, data = db.get_multiple_pages_details(page_ids)
        if not success:
            QMessageBox.warning(self.main_window, "Error", f"Could not fetch details: {data}")
            return
        success, accounts = db.get_all_accounts()
        if not success:
            accounts = []
            
        dialog = BulkEditPagesDialog(data, accounts, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            if not updated:
                return
            success, msg = db.bulk_update_pages_partial(updated)
            if success:
                self.main_window.refresh_all_data()
            else:
                QMessageBox.critical(self.main_window, "DB Error", f"Failed to bulk update: {msg}")

    def open_import_accounts_dialog(self):
        dialog = ImportAccountsDialog(self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            records = self._prepare_records_for_import(data)
            if not records:
                QMessageBox.warning(self.main_window, "No Data", "No valid records to import.")
                return
            
            success, msg = db.bulk_import_accounts(records)
            if success:
                QMessageBox.information(self.main_window, "Success", f"Import complete. {msg} records processed.")
                self.main_window.refresh_all_data()
            else:
                QMessageBox.critical(self.main_window, "Import Error", f"An error occurred: {msg}")

    def _prepare_records_for_import(self, data):
        lines, sep, mapping = data['text_data'].strip().split('\n'), data['separator'], data['mapping']
        if not all([lines, sep, mapping]):
            return []
        records = []
        for line in lines:
            if not line.strip():
                continue
            parts = line.strip().split(sep)
            record = {db_col: parts[i] for i, db_col in mapping.items() if i < len(parts)}
            if record.get('profile_id') and record.get('account_name'):
                records.append(record)
        return records

    def delete_selected_items(self):
        items, _ = self.main_window.get_current_selection_info()
        if not items:
            return
        items_to_delete = list(set(item for item in items if item and item[0] and item[1]))
        if not items_to_delete:
            return

        reply = QMessageBox.question(self.main_window, 'Confirm Delete', 
                                   f'Move {len(items_to_delete)} item(s) to Recycle Bin?', 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for item_type, item_id in items_to_delete: 
                db.soft_delete(item_type, item_id)
            self.main_window.refresh_all_data()

    def open_recycle_bin(self):
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

    def open_bulk_proxy_dialog(self):
        items, _ = self.main_window.get_current_selection_info()
        if not items:
            return
        ids = [info[1] for info in items if info and info[0] == 'account']
        if not ids:
            return

        success, data = db.get_accounts_for_proxy_edit(ids)
        if not success:
            QMessageBox.critical(self.main_window, "DB Error", f"Could not fetch details: {data}")
            return
            
        dialog = BulkProxyDialog(data, self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            if not updated:
                return
            success, msg = db.bulk_update_accounts_partial(updated)
            if success:
                self.main_window.refresh_all_data()
            else:
                QMessageBox.critical(self.main_window, "DB Error", f"Failed to update proxies: {msg}")
