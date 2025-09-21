# handlers/page_dialogs.py

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt
from utils import log
import database as db
from dialogs import (AddPageDialog, EditPageDialog, AdvancedBulkAddPagesDialog,
                     BulkEditPagesDialog, ScheduleDetailDialog)


class PageDialogHandler:
    """Handles all page-related dialog operations"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_widget = main_window.main_widget

    def open_add_page_dialog(self, account_id=None):
        """Open dialog to add a new page"""
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

    def open_edit_page_dialog(self, page_id):
        """Open dialog to edit a single page"""
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

    def open_bulk_edit_pages_dialog(self, page_ids):
        """Open dialog to bulk edit multiple pages"""
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

    def open_bulk_add_pages_dialog(self):
        """Open advanced bulk add pages dialog"""
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

    def handle_schedule_double_click(self, table, row, column):
        """FIXED: Handle schedule column double clicks - SINGLE DIALOG ONLY"""
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
