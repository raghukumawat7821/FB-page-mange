# dialogs/schedule_dialogs.py

import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, 
                             QFormLayout, QLabel, QHBoxLayout,
                             QPushButton, QFileDialog, QMessageBox, QDateEdit, 
                             QSpinBox, QGroupBox, QGridLayout, QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QCursor, QFont
from utils import log


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
        """Initialize the dialog UI"""
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
        """Initialize the dialog UI"""
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
