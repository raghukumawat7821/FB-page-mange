# dialogs/page.py

import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, 
                             QFormLayout, QLabel, QComboBox, QTextEdit,
                             QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QFileDialog, QMessageBox, QWidget, QDateEdit, 
                             QSpinBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QCursor, QFont
from utils import log
from .utility import CompleterDelegate


class ScheduleDetailDialog(QDialog):
    """Dialog for viewing and editing schedule details for Video/Reels/Photos"""
    def __init__(self, page_data, content_type, parent=None):
        super().__init__(parent)
        self.page_data = page_data
        self.content_type = content_type  # 'video', 'reels', or 'photo'
        
        self.setWindowTitle(f"Schedule Details - {page_data.get('page_name', 'Unknown')} - {content_type.capitalize()}")
        self.setMinimumSize(500, 400)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header with page info
        header_layout = QHBoxLayout()
        page_name = QLabel(f"📄 Page: {self.page_data.get('page_name', 'Unknown')}")
        page_name.setFont(QFont("Arial", 12, QFont.Bold))
        content_label = QLabel(f"🎬 Content Type: {self.content_type.capitalize()}")
        content_label.setFont(QFont("Arial", 10))
        
        header_layout.addWidget(page_name)
        header_layout.addStretch()
        header_layout.addWidget(content_label)
        main_layout.addLayout(header_layout)
        
        # Schedule Details Group
        schedule_group = QGroupBox("📅 Schedule Information")
        schedule_layout = QFormLayout(schedule_group)
        
        # Current schedule end date
        current_end_date = self.page_data.get(f'{self.content_type}_schedule_date', '')
        self.end_date_label = QLabel(current_end_date if current_end_date else "Not Set")
        self.end_date_label.setStyleSheet("QLabel { background-color: #f0f8ff; padding: 5px; border: 1px solid #ccc; }")
        
        # Posts per day
        current_ppd = self.page_data.get(f'{self.content_type}_posts_per_day', 0)
        self.ppd_label = QLabel(str(current_ppd) if current_ppd else "Not Set")
        self.ppd_label.setStyleSheet("QLabel { background-color: #f0f8ff; padding: 5px; border: 1px solid #ccc; }")
        
        schedule_layout.addRow("Schedule Ends On:", self.end_date_label)
        schedule_layout.addRow("Posts Per Day:", self.ppd_label)
        
        # Content Folder Group
        folder_group = QGroupBox("📁 Content Folder Information")
        folder_layout = QFormLayout(folder_group)
        
        current_folder = self.page_data.get(f'{self.content_type}_folder', '')
        self.folder_label = QLabel(current_folder if current_folder else "Not Set")
        self.folder_label.setStyleSheet("QLabel { background-color: #f0fff0; padding: 5px; border: 1px solid #ccc; }")
        
        # Count files in folder
        file_count = self.count_files(current_folder) if current_folder else 0
        self.file_count_label = QLabel(f"{file_count} files")
        self.file_count_label.setStyleSheet("QLabel { background-color: #fff0f0; padding: 5px; border: 1px solid #ccc; }")
        
        folder_layout.addRow("Current Folder:", self.folder_label)
        folder_layout.addRow("Files Available:", self.file_count_label)
        
        # Used Folders Group
        used_group = QGroupBox("♻️ Previously Used Folders")
        used_layout = QVBoxLayout(used_group)
        
        self.used_folders_display = QTextEdit()
        self.used_folders_display.setReadOnly(True)
        self.used_folders_display.setMaximumHeight(100)
        self.update_used_folders_display()
        used_layout.addWidget(self.used_folders_display)
        
        # Add all groups to main layout
        main_layout.addWidget(schedule_group)
        main_layout.addWidget(folder_group)
        main_layout.addWidget(used_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("✏️ Edit Schedule")
        self.edit_btn.clicked.connect(self.open_edit_dialog)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        button_layout.addWidget(self.edit_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        main_layout.addLayout(button_layout)
    
    def count_files(self, folder_path):
        """Count files in the given folder"""
        if folder_path and os.path.isdir(folder_path):
            try:
                return len([f for f in os.listdir(folder_path) 
                          if os.path.isfile(os.path.join(folder_path, f))])
            except OSError:
                return 0
        return 0
    
    def update_used_folders_display(self):
        """Update the display of previously used folders"""
        try:
            used_folders = json.loads(self.page_data.get('used_folders', '[]'))
            if used_folders:
                self.used_folders_display.setText('\n'.join(used_folders))
            else:
                self.used_folders_display.setText("No previously used folders")
        except (json.JSONDecodeError, TypeError):
            self.used_folders_display.setText("No previously used folders")
    
    def open_edit_dialog(self):
        """FIXED: Open inline edit dialog and save directly - NO DOUBLE POPUP"""
        edit_dialog = EditScheduleDialog(self.page_data, self.content_type, self)
        if edit_dialog.exec_() == QDialog.Accepted:
            # Get updated data
            updated_data = edit_dialog.get_data()
            
            # CRITICAL FIX: Update database directly here - ONE SAVE ONLY
            try:
                import database as db
                
                # Update only this specific schedule type in database
                page_id = self.page_data.get('page_id')
                if page_id:
                    # Prepare update data for specific content type only
                    update_data = {
                        f'{self.content_type}_schedule_date': updated_data.get(f'{self.content_type}_schedule_date'),
                        f'{self.content_type}_posts_per_day': updated_data.get(f'{self.content_type}_posts_per_day'),
                        f'{self.content_type}_folder': updated_data.get(f'{self.content_type}_folder', '')
                    }
                    
                    success, msg = db.update_page_details(page_id, update_data)
                    if success:
                        # Update local data
                        self.page_data.update(updated_data)
                        self.refresh_display()
                        
                        # Show success message
                        QMessageBox.information(self, "Success", f"{self.content_type.capitalize()} schedule updated successfully!")
                        
                        # IMPORTANT: Refresh main window data - ONE TIME ONLY
                        main_window = self.parent()
                        while main_window and not hasattr(main_window, 'refresh_all_data'):
                            main_window = main_window.parent()
                        if main_window:
                            main_window.refresh_all_data()
                    else:
                        QMessageBox.critical(self, "Error", f"Failed to update schedule: {msg}")
                else:
                    QMessageBox.warning(self, "Error", "Page ID not found")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save schedule: {str(e)}")
    
    def refresh_display(self):
        """Refresh the display with updated data"""
        # Update schedule info
        end_date = self.page_data.get(f'{self.content_type}_schedule_date', '')
        ppd = self.page_data.get(f'{self.content_type}_posts_per_day', 0)
        folder = self.page_data.get(f'{self.content_type}_folder', '')
        
        self.end_date_label.setText(end_date if end_date else "Not Set")
        self.ppd_label.setText(str(ppd) if ppd else "Not Set")
        self.folder_label.setText(folder if folder else "Not Set")
        
        # Update file count
        file_count = self.count_files(folder) if folder else 0
        self.file_count_label.setText(f"{file_count} files")
        
        # Update used folders
        self.update_used_folders_display()


class EditScheduleDialog(QDialog):
    """Dialog for editing schedule settings - INLINE EDITING ONLY"""
    def __init__(self, page_data, content_type, parent=None):
        super().__init__(parent)
        self.page_data = page_data
        self.content_type = content_type
        
        self.setWindowTitle(f"Edit {content_type.capitalize()} Schedule")
        self.setMinimumSize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout(self)
        
        # Schedule end date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        current_date = self.page_data.get(f'{self.content_type}_schedule_date', '')
        if current_date:
            try:
                self.date_edit.setDate(QDate.fromString(current_date, "yyyy-MM-dd"))
            except:
                self.date_edit.setDate(QDate.currentDate().addDays(30))
        else:
            self.date_edit.setDate(QDate.currentDate().addDays(30))
        
        # Posts per day - FIXED: Safe handling of None values
        self.ppd_spin = QSpinBox()
        self.ppd_spin.setRange(0, 50)
        
        # SAFE VALUE HANDLING TO AVOID TypeError
        ppd_value = self.page_data.get(f'{self.content_type}_posts_per_day')
        if ppd_value is None or ppd_value == '':
            ppd_value = 1  # Default to 1 instead of 0
        else:
            try:
                ppd_value = int(ppd_value)
            except (ValueError, TypeError):
                ppd_value = 1
        
        self.ppd_spin.setValue(ppd_value)  # Now safe from None
        
        # Folder selection
        folder_layout = QHBoxLayout()
        current_folder = self.page_data.get(f'{self.content_type}_folder', '')
        self.folder_label = QLabel(current_folder if current_folder else "Not Set")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.select_folder)
        
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(browse_btn)
        
        layout.addRow("Schedule Ends On:", self.date_edit)
        layout.addRow("Posts Per Day:", self.ppd_spin)
        layout.addRow("Content Folder:", folder_layout)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
    
    def select_folder(self):
        """Select content folder"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            f"Select {self.content_type.capitalize()} Folder",
            self.folder_label.text() if os.path.isdir(self.folder_label.text()) else ""
        )
        if folder:
            self.folder_label.setText(folder)
    
    def get_data(self):
        """Get updated schedule data - ONLY FOR THIS CONTENT TYPE"""
        return {
            f'{self.content_type}_schedule_date': self.date_edit.date().toString("yyyy-MM-dd"),
            f'{self.content_type}_posts_per_day': self.ppd_spin.value(),
            f'{self.content_type}_folder': self.folder_label.text() if self.folder_label.text() != "Not Set" else ''
        }


class AddPageDialog(QDialog):
    def __init__(self, accounts, pre_selected_account_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Page")
        form_layout = QFormLayout()
        self.account_combo = QComboBox(self)
        current_index = 0
        
        if accounts:
            for i, (acc_id, profile_id, acc_name) in enumerate(accounts):
                self.account_combo.addItem(f"{profile_id} ({acc_name})", acc_id)
                if pre_selected_account_id and acc_id == pre_selected_account_id:
                    current_index = i
                    
        self.account_combo.setCurrentIndex(current_index)
        
        self.page_name_input = QLineEdit(self)
        self.uid_page_id_input = QLineEdit(self)
        self.category_input = QLineEdit(self)
        self.monetization_input = QLineEdit(self)
        
        form_layout.addRow(QLabel("Link to Account:"), self.account_combo)
        form_layout.addRow(QLabel("Page Name:"), self.page_name_input)
        form_layout.addRow(QLabel("UID/Page ID (Optional):"), self.uid_page_id_input)
        form_layout.addRow(QLabel("Page Category:"), self.category_input)
        form_layout.addRow(QLabel("Monetization:"), self.monetization_input)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)
    
    def get_data(self): 
        return {
            "page_name": self.page_name_input.text().strip(), 
            "uid_page_id": self.uid_page_id_input.text().strip(), 
            "category": self.category_input.text().strip(), 
            "monetization": self.monetization_input.text().strip(), 
            "linked_account_id": self.account_combo.currentData(),
            # Default schedule values - reasonable defaults
            "video_schedule_date": QDate.currentDate().addDays(30).toString("yyyy-MM-dd"),
            "video_posts_per_day": 1,
            "reels_schedule_date": QDate.currentDate().addDays(30).toString("yyyy-MM-dd"),
            "reels_posts_per_day": 2,
            "photo_schedule_date": QDate.currentDate().addDays(30).toString("yyyy-MM-dd"),
            "photo_posts_per_day": 1,
            "video_folder": "",
            "reels_folder": "",
            "photo_folder": "",
            "used_folders": "[]"
        }


class AdvancedBulkAddPagesDialog(QDialog):
    def __init__(self, profile_id_map, page_categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Bulk Add Pages")
        self.setMinimumSize(800, 500)
        self.profile_id_map = profile_id_map

        main_layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Profile ID", "Page Name", "UID/Page ID", "Page Category"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        if page_categories:
            self.table.setItemDelegateForColumn(3, CompleterDelegate(self, page_categories))
        
        self.table.cellChanged.connect(self.validate_profile_id)
        
        button_layout = QHBoxLayout()
        add_row_btn = QPushButton("+ Add Row")
        add_row_btn.clicked.connect(self.add_row)
        remove_row_btn = QPushButton("- Remove Selected Row")
        remove_row_btn.clicked.connect(self.remove_row)
        
        button_layout.addWidget(add_row_btn)
        button_layout.addWidget(remove_row_btn)
        button_layout.addStretch()
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_data)
        self.button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(self.table)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.button_box)
        
        # Add initial rows
        for _ in range(5):
            self.add_row()
    
    def add_row(self):
        self.table.insertRow(self.table.rowCount())
    
    def remove_row(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        for index in sorted(selected_rows, reverse=True):
            self.table.removeRow(index.row())
    
    def validate_profile_id(self, row, column):
        if column == 0:
            item = self.table.item(row, column)
            if not item:
                return
                
            self.table.blockSignals(True)
            profile_id = item.text().strip().split(' ')[0].upper()
            
            if profile_id in self.profile_id_map:
                original_case_id, account_name = self.profile_id_map[profile_id]
                item.setText(f"{original_case_id} ({account_name})")
                item.setBackground(QColor("white"))
            else:
                item.setBackground(QColor("#FFCCCB"))
            
            self.table.blockSignals(False)
    
    def accept_data(self):
        invalid_rows = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text().strip() and item.background().color() == QColor("#FFCCCB"):
                invalid_rows.append(str(row + 1))
                
        if invalid_rows:
            QMessageBox.warning(self, "Invalid Profile ID", 
                              f"Rows {', '.join(invalid_rows)} have invalid Profile IDs. Please correct them before saving.")
            return
        
        reply = QMessageBox.question(self, 'Confirm Save', 
                                   'Are you sure you want to add these pages?', 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.accept()
    
    def get_data(self):
        pages_to_add = []
        for row in range(self.table.rowCount()):
            profile_id_item = self.table.item(row, 0)
            page_name_item = self.table.item(row, 1)
            uid_item = self.table.item(row, 2)
            category_item = self.table.item(row, 3)
            
            profile_id = profile_id_item.text().strip().split(' ')[0] if profile_id_item and profile_id_item.text() else ""
            page_name = page_name_item.text().strip() if page_name_item and page_name_item.text() else ""
            category = category_item.text().strip() if category_item and category_item.text() else ""
            uid = uid_item.text().strip() if uid_item and uid_item.text() else ""

            if profile_id and page_name:
                page_data = {
                    "profile_id": profile_id, 
                    "page_name": page_name, 
                    "uid_page_id": uid, 
                    "category": category,
                    "video_schedule_date": QDate.currentDate().addDays(30).toString("yyyy-MM-dd"),
                    "video_posts_per_day": 1,
                    "reels_schedule_date": QDate.currentDate().addDays(30).toString("yyyy-MM-dd"),
                    "reels_posts_per_day": 2,
                    "photo_schedule_date": QDate.currentDate().addDays(30).toString("yyyy-MM-dd"),
                    "photo_posts_per_day": 1,
                    "video_folder": "",
                    "reels_folder": "",
                    "photo_folder": "",
                    "used_folders": "[]"
                }
                pages_to_add.append(page_data)
        return pages_to_add


class EditPageDialog(QDialog):
    def __init__(self, page_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Page: {page_data.get('page_name', '')}")
        self.setMinimumSize(600, 500)
        self.page_data = page_data
        
        # CRITICAL FIX: Store original schedule values to detect changes
        self.original_schedule_data = {
            'video_schedule_date': self.page_data.get('video_schedule_date', ''),
            'video_posts_per_day': self.page_data.get('video_posts_per_day', 0),
            'reels_schedule_date': self.page_data.get('reels_schedule_date', ''),
            'reels_posts_per_day': self.page_data.get('reels_posts_per_day', 0),
            'photo_schedule_date': self.page_data.get('photo_schedule_date', ''),
            'photo_posts_per_day': self.page_data.get('photo_posts_per_day', 0)
        }
        
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Basic page information
        self.page_name_input = QLineEdit(self.page_data.get('page_name', ''))
        self.category_input = QLineEdit(self.page_data.get('category', ''))
        self.monetization_input = QLineEdit(self.page_data.get('monetization', ''))
        self.followers_input = QLineEdit(self.page_data.get('followers', ''))
        self.interaction_input = QLineEdit(self.page_data.get('last_interaction', ''))
        
        form_layout.addRow("Page Name:", self.page_name_input)
        form_layout.addRow("Followers:", self.followers_input)
        form_layout.addRow("Last Interaction:", self.interaction_input)
        form_layout.addRow("Page Category:", self.category_input)
        form_layout.addRow("Monetization:", self.monetization_input)
        
        # Folder selectors
        self.video_folder_widget, self.video_folder_label = self.create_folder_selector('video_folder', "Select Video Folder")
        self.reels_folder_widget, self.reels_folder_label = self.create_folder_selector('reels_folder', "Select Reels Folder")
        self.photo_folder_widget, self.photo_folder_label = self.create_folder_selector('photo_folder', "Select Photo Folder")
        
        form_layout.addRow("Video Folder:", self.video_folder_widget)
        form_layout.addRow("Reels Folder:", self.reels_folder_widget)
        form_layout.addRow("Photo Folder:", self.photo_folder_widget)
        
        # Schedule widgets - FIXED: Don't auto-set dates
        self.video_date, self.video_ppd = self.create_schedule_widgets('video_schedule_date', 'video_posts_per_day')
        self.reels_date, self.reels_ppd = self.create_schedule_widgets('reels_schedule_date', 'reels_posts_per_day')
        self.photo_date, self.photo_ppd = self.create_schedule_widgets('photo_schedule_date', 'photo_posts_per_day')

        form_layout.addRow("Video Schedule (Ends On / Per Day):", self.create_schedule_layout(self.video_date, self.video_ppd))
        form_layout.addRow("Reels Schedule (Ends On / Per Day):", self.create_schedule_layout(self.reels_date, self.reels_ppd))
        form_layout.addRow("Photo Schedule (Ends On / Per Day):", self.create_schedule_layout(self.photo_date, self.photo_ppd))

        # Used folders display
        self.used_folders_display = QTextEdit()
        self.used_folders_display.setReadOnly(True)
        self.update_used_folders_display()
        form_layout.addRow("Used Folders:", self.used_folders_display)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

    def create_folder_selector(self, key, title):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        folder_path = self.page_data.get(key, 'Not Set')
        label = QLabel(folder_path)
        count_label = QLabel(f"({self.count_files(folder_path)} files)")
        button = QPushButton("Browse...")
        button.clicked.connect(lambda: self.select_folder(label, count_label, title, key))
        
        layout.addWidget(label)
        layout.addWidget(count_label)
        layout.addWidget(button)
        return widget, label

    def select_folder(self, label, count_label, title, key):
        folder = QFileDialog.getExistingDirectory(self, title, 
                                                 label.text() if os.path.isdir(label.text()) else "")
        if folder:
            self.setCursor(QCursor(Qt.WaitCursor))
            count = self.count_files(folder)
            label.setText(folder)
            count_label.setText(f"({count} files)")
            self.unsetCursor()
            
            try:
                current_folders = json.loads(self.page_data.get('used_folders') or '[]')
                if folder not in current_folders:
                    current_folders.append(folder)
                    self.page_data['used_folders'] = json.dumps(current_folders)
                    self.update_used_folders_display()
            except json.JSONDecodeError:
                pass

    def update_used_folders_display(self):
        try:
            used_folders_list = json.loads(self.page_data.get('used_folders') or '[]')
            self.used_folders_display.setText('\n'.join(used_folders_list))
        except json.JSONDecodeError:
            self.used_folders_display.setText("")

    def count_files(self, path):
        if path and os.path.isdir(path):
            try:
                return sum(1 for name in os.listdir(path) if os.path.isfile(os.path.join(path, name)))
            except OSError:
                return 0
        return 0

    def create_schedule_widgets(self, date_key, ppd_key):
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")
        
        # CRITICAL FIX: Use existing values ONLY, no auto-setting
        date_str = self.page_data.get(date_key, '')
        if date_str and date_str.strip():
            try:
                date_edit.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
            except:
                # If parsing fails, keep it blank/minimum date
                date_edit.setDate(QDate.fromString("2000-01-01", "yyyy-MM-dd"))
        else:
            # If no existing date, set to a recognizable "not set" date
            date_edit.setDate(QDate.fromString("2000-01-01", "yyyy-MM-dd"))
        
        spin_box = QSpinBox()
        spin_box.setRange(0, 100)
        
        # FIXED: Safe handling of None values
        ppd = self.page_data.get(ppd_key)
        try:
            if ppd is None or ppd == '':
                spin_box.setValue(0)
            else:
                spin_box.setValue(int(ppd))
        except (ValueError, TypeError):
            spin_box.setValue(0)
            
        return date_edit, spin_box

    def create_schedule_layout(self, date_edit, spin_box):
        layout = QHBoxLayout()
        layout.addWidget(date_edit)
        layout.addWidget(spin_box)
        return layout

    def get_data(self):
        """CRITICAL FIX: Only return schedule data if user actually changed it"""
        result_data = {
            "page_name": self.page_name_input.text().strip(),
            "category": self.category_input.text().strip(),
            "monetization": self.monetization_input.text().strip(),
            "followers": self.followers_input.text().strip(),
            "last_interaction": self.interaction_input.text().strip(),
            "video_folder": self.video_folder_label.text() if self.video_folder_label.text() != 'Not Set' else '',
            "reels_folder": self.reels_folder_label.text() if self.reels_folder_label.text() != 'Not Set' else '',
            "photo_folder": self.photo_folder_label.text() if self.photo_folder_label.text() != 'Not Set' else '',
            "used_folders": self.page_data.get('used_folders', '[]')
        }
        
        # CRITICAL FIX: Only include schedule data if it was actually changed
        current_video_date = self.video_date.date().toString("yyyy-MM-dd")
        current_video_ppd = self.video_ppd.value()
        if (current_video_date != "2000-01-01" and 
            (current_video_date != self.original_schedule_data['video_schedule_date'] or 
             current_video_ppd != self.original_schedule_data['video_posts_per_day'])):
            result_data["video_schedule_date"] = current_video_date
            result_data["video_posts_per_day"] = current_video_ppd
        
        current_reels_date = self.reels_date.date().toString("yyyy-MM-dd")
        current_reels_ppd = self.reels_ppd.value()
        if (current_reels_date != "2000-01-01" and 
            (current_reels_date != self.original_schedule_data['reels_schedule_date'] or 
             current_reels_ppd != self.original_schedule_data['reels_posts_per_day'])):
            result_data["reels_schedule_date"] = current_reels_date
            result_data["reels_posts_per_day"] = current_reels_ppd
        
        current_photo_date = self.photo_date.date().toString("yyyy-MM-dd")
        current_photo_ppd = self.photo_ppd.value()
        if (current_photo_date != "2000-01-01" and 
            (current_photo_date != self.original_schedule_data['photo_schedule_date'] or 
             current_photo_ppd != self.original_schedule_data['photo_posts_per_day'])):
            result_data["photo_schedule_date"] = current_photo_date
            result_data["photo_posts_per_day"] = current_photo_ppd
        
        return result_data
