# dialogs/bulk_page_dialogs.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from .utility import CompleterDelegate


class AdvancedBulkAddPagesDialog(QDialog):
    """Dialog for advanced bulk addition of pages with validation"""
    
    def __init__(self, profile_id_map, page_categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Bulk Add Pages")
        self.setMinimumSize(800, 500)
        self.profile_id_map = profile_id_map
        self.init_ui(page_categories)
    
    def init_ui(self, page_categories):
        """Initialize the dialog UI"""
        main_layout = QVBoxLayout(self)
        
        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Profile ID", "Page Name", "UID/Page ID", "Page Category"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        if page_categories:
            self.table.setItemDelegateForColumn(3, CompleterDelegate(self, page_categories))
        
        self.table.cellChanged.connect(self.validate_profile_id)
        
        # Button layout
        button_layout = QHBoxLayout()
        add_row_btn = QPushButton("+ Add Row")
        add_row_btn.clicked.connect(self.add_row)
        remove_row_btn = QPushButton("- Remove Selected Row")
        remove_row_btn.clicked.connect(self.remove_row)
        
        button_layout.addWidget(add_row_btn)
        button_layout.addWidget(remove_row_btn)
        button_layout.addStretch()
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_data)
        self.button_box.rejected.connect(self.reject)
        
        # Layout assembly
        main_layout.addWidget(self.table)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.button_box)
        
        # Add initial rows
        for _ in range(5):
            self.add_row()
    
    def add_row(self):
        """Add a new row to the table"""
        self.table.insertRow(self.table.rowCount())
    
    def remove_row(self):
        """Remove selected rows from the table"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        for index in sorted(selected_rows, reverse=True):
            self.table.removeRow(index.row())
    
    def validate_profile_id(self, row, column):
        """Validate Profile ID as user types"""
        if column == 0:  # Profile ID column
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
                item.setBackground(QColor("#FFCCCB"))  # Light red for invalid
            
            self.table.blockSignals(False)
    
    def accept_data(self):
        """Validate data before accepting"""
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
        """Get validated page data for bulk creation"""
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
                    
                    # Default schedule values
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
