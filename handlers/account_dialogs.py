# handlers/account_dialogs.py

from PyQt5.QtWidgets import QDialog, QMessageBox
import database as db
from dialogs import (AddAccountDialog, EditAccountDialog, ImportAccountsDialog,
                     BulkEditAccountsDialog, BulkProxyDialog)


class AccountDialogHandler:
    """Handles all account-related dialog operations"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_widget = main_window.main_widget

    def open_add_account_dialog(self):
        """Open dialog to add a new account"""
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

    def open_edit_account_dialog(self, account_id):
        """Open dialog to edit a single account"""
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
        """Open dialog to bulk edit multiple accounts"""
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

    def open_import_accounts_dialog(self):
        """Open dialog to import multiple accounts from text data"""
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

    def open_bulk_proxy_dialog(self):
        """Open dialog to bulk edit proxy settings"""
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

    def _prepare_records_for_import(self, data):
        """Prepare text data for account import"""
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
