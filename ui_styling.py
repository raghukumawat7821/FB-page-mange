# ui_styling.py

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor


class UIStyling:
    """Handles all UI styling, coloring, and visual effects for MainUI"""
    
    def __init__(self, main_ui):
        self.main_ui = main_ui

    def apply_data_based_colors(self):
        """Apply colors based on actual data type - Keep irrelevant cells empty"""
        try:
            print("Applying data-based row colors...")
            
            # Color ALL rows in accounts table with blue
            for row in range(self.main_ui.accounts_table.rowCount()):
                for col in range(self.main_ui.accounts_table.columnCount()):
                    item = self.main_ui.accounts_table.item(row, col)
                    if item:
                        item.setBackground(self.main_ui.accounts_color)
                        # Keep irrelevant columns empty for accounts
                        header_item = self.main_ui.accounts_table.horizontalHeaderItem(col)
                        if header_item and header_item.text() in ['Followers', 'Last Interaction', 'Video Ends', 'Reels Ends', 'Photo Ends', 'Monetization']:
                            if item.text().lower() in ['none', 'null', 'no data', 'not scheduled']:
                                item.setText('')  # Keep empty
            
            # Color ALL rows in pages table with green
            for row in range(self.main_ui.pages_table.rowCount()):
                for col in range(self.main_ui.pages_table.columnCount()):
                    item = self.main_ui.pages_table.item(row, col)
                    if item:
                        item.setBackground(self.main_ui.pages_color)
                        # Keep note column empty if no actual note
                        header_item = self.main_ui.pages_table.horizontalHeaderItem(col)
                        if header_item and header_item.text() == 'Note':
                            if item.text().lower() in ['none', 'null', 'no note']:
                                item.setText('')  # Keep empty
            
            # Handle unified table
            for row in range(self.main_ui.unified_table.rowCount()):
                first_item = self.main_ui.unified_table.item(row, 0)
                if first_item and first_item.data(Qt.UserRole):
                    data_info = first_item.data(Qt.UserRole)
                    data_type = data_info.get('type', '').lower()
                    
                    if data_type == 'account':
                        row_color = self.main_ui.accounts_color
                    elif data_type == 'page':
                        row_color = self.main_ui.pages_color
                    else:
                        continue
                    
                    # Apply color and clean irrelevant cells
                    for col in range(self.main_ui.unified_table.columnCount()):
                        item = self.main_ui.unified_table.item(row, col)
                        if item:
                            item.setBackground(row_color)
                            
                            # Clean irrelevant columns based on row type
                            header_item = self.main_ui.unified_table.horizontalHeaderItem(col)
                            if header_item:
                                header_text = header_item.text()
                                
                                if data_type == 'account' and header_text in ['Followers', 'Last Interaction', 'Video Ends', 'Reels Ends', 'Photo Ends', 'Monetization']:
                                    if item.text().lower() in ['none', 'null', 'no data', 'not scheduled']:
                                        item.setText('')  # Keep empty
                                
                                if header_text == 'Note' and item.text().lower() in ['none', 'null', 'no note']:
                                    item.setText('')  # Keep empty
            
            print("Data-based row colors applied successfully!")
            
        except Exception as e:
            print(f"Error applying data-based colors: {e}")

    def fix_selection_highlighting(self):
        """Force proper selection highlighting without clearing colors"""
        tables = [self.main_ui.unified_table, self.main_ui.accounts_table, self.main_ui.pages_table]
        
        for table in tables:
            try:
                # Just refresh selection without clearing backgrounds
                selected_rows = table.selectionModel().selectedRows()
                if selected_rows:
                    current_selection = [index.row() for index in selected_rows]
                    table.clearSelection()
                    for row_index in current_selection:
                        table.selectRow(row_index)
                
                print(f"Fixed selection for {table.objectName()}")
                
            except Exception as e:
                print(f"Failed to fix selection for {table.objectName()}: {e}")

    def apply_professional_styling(self):
        """COMPACT styling - PRESERVES TABLE COLORS"""
        self.main_ui.setStyleSheet("""
            /* Main Widget */
            QWidget {
                background-color: #f5f5f5;
                color: #2c2c2c;
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
                font-size: 8pt;
            }
            
            /* COMPACT Panels */
            QFrame#filterPanel, QFrame#controlsPanel {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin: 1px;
                padding: 2px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            
            QFrame#viewContainer {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin: 1px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }
            
            /* Labels */
            QLabel {
                color: #404040;
                font-weight: 500;
                padding: 1px;
                letter-spacing: 0.3px;
                font-size: 8pt;
            }
            
            /* Filter Labels */
            QLabel[text*="👁️"], QLabel[text*="🔍"], QLabel[text*="👤"], QLabel[text*="📄"] {
                color: #2c2c2c;
                font-weight: 600;
                font-size: 8pt;
            }
            
            /* Buttons */
            QPushButton#responsiveButton {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: 500;
                color: #2c2c2c;
                min-height: 16px;
                text-align: left;
                padding-left: 8px;
                font-size: 8pt;
                transition: all 0.3s ease;
            }
            
            QPushButton#responsiveButton:hover {
                background-color: #e8f4fd;
                border-color: #0078d4;
                color: #0078d4;
                transform: translateY(-1px);
                box-shadow: 0 3px 12px rgba(0, 120, 212, 0.2);
            }
            
            QPushButton#responsiveButton:pressed {
                background-color: #d1e7f7;
                border-color: #005a9e;
                transform: translateY(0px);
                box-shadow: 0 1px 4px rgba(0, 120, 212, 0.3);
            }
            
            /* Primary Buttons */
            QPushButton#responsiveButton[text*="📥"], QPushButton#responsiveButton[text*="📤"], QPushButton#responsiveButton[text*="➕"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0078d4, stop:1 #005a9e);
                border-color: #005a9e;
                color: white;
                font-weight: 600;
            }
            
            QPushButton#responsiveButton[text*="📥"]:hover, QPushButton#responsiveButton[text*="📤"]:hover, QPushButton#responsiveButton[text*="➕"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #106ebe, stop:1 #0078d4);
                box-shadow: 0 4px 16px rgba(0, 120, 212, 0.4);
            }
            
            /* Deselect Button - Orange Theme */
            QPushButton#responsiveButton[text*="❌"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff8c00, stop:1 #ff6600);
                border-color: #ff6600;
                color: white;
                font-weight: 600;
            }
            
            QPushButton#responsiveButton[text*="❌"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff7700, stop:1 #ff4400);
                box-shadow: 0 4px 16px rgba(255, 140, 0, 0.4);
            }
            
            /* Danger Button */
            QPushButton#responsiveButton[text*="🗑️"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d13438, stop:1 #a4262c);
                border-color: #a4262c;
                color: white;
                font-weight: 600;
            }
            
            QPushButton#responsiveButton[text*="🗑️"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #b92329, stop:1 #8b1a1f);
                box-shadow: 0 4px 16px rgba(209, 52, 56, 0.4);
            }
            
            /* Special Buttons */
            QPushButton#responsiveButton[text*="♻️"] {
                background-color: #107c10;
                border-color: #0e6e0e;
                color: white;
                font-weight: 600;
            }
            
            QPushButton#responsiveButton[text*="♻️"]:hover {
                background-color: #0e6e0e;
                box-shadow: 0 4px 16px rgba(16, 124, 16, 0.4);
            }
            
            QPushButton#responsiveButton[text*="🔄"] {
                background-color: #6b69d6;
                border-color: #5a58c7;
                color: white;
                font-weight: 600;
            }
            
            QPushButton#responsiveButton[text*="🔄"]:hover {
                background-color: #5a58c7;
                box-shadow: 0 4px 16px rgba(107, 105, 214, 0.4);
            }
            
            QPushButton#responsiveButton[text*="⚙️"] {
                background-color: #8a8886;
                border-color: #797775;
                color: white;
                font-weight: 600;
            }
            
            QPushButton#responsiveButton[text*="⚙️"]:hover {
                background-color: #797775;
                box-shadow: 0 4px 16px rgba(138, 136, 134, 0.4);
            }
            
            /* ComboBox */
            QComboBox#adaptiveCombo {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 3px 8px;
                min-width: 80px;
                font-weight: 500;
                font-size: 8pt;
                transition: all 0.2s ease;
            }
            
            QComboBox#adaptiveCombo:hover {
                border-color: #0078d4;
                box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.1);
            }
            
            QComboBox#adaptiveCombo:focus {
                border-color: #0078d4;
                outline: none;
                box-shadow: 0 0 0 3px rgba(0, 120, 212, 0.2);
            }
            
            /* Search Input */
            QLineEdit#adaptiveSearch {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 8pt;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            
            QLineEdit#adaptiveSearch:focus {
                border-color: #0078d4;
                outline: none;
                box-shadow: 0 0 0 3px rgba(0, 120, 212, 0.2);
            }
            
            QLineEdit#adaptiveSearch:hover {
                border-color: #0078d4;
                box-shadow: 0 0 0 1px rgba(0, 120, 212, 0.1);
            }
            
            /* View Toggle */
            QCheckBox#viewToggle {
                spacing: 4px;
                font-weight: 600;
                color: #2c2c2c;
                padding: 2px;
                font-size: 8pt;
            }
            
            QCheckBox#viewToggle::indicator {
                width: 14px;
                height: 14px;
                border: 2px solid #d0d0d0;
                border-radius: 3px;
                background-color: #ffffff;
                transition: all 0.2s ease;
            }
            
            QCheckBox#viewToggle::indicator:hover {
                border-color: #0078d4;
                box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.1);
            }
            
            QCheckBox#viewToggle::indicator:checked {
                background-color: #0078d4;
                border-color: #005a9e;
                image: none;
            }
            
            /* Splitter */
            QSplitter#adaptiveSplitter::handle {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0e0e0, stop:0.5 #0078d4, stop:1 #e0e0e0);
                height: 4px;
                border-radius: 2px;
                margin: 2px 0px;
            }
            
            QSplitter#adaptiveSplitter::handle:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0078d4, stop:0.5 #005a9e, stop:1 #0078d4);
                height: 6px;
            }
            
            /* Stack Widget */
            QStackedWidget#animatedStack {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Schedule grid refresh to ensure visibility
        QTimer.singleShot(500, self.refresh_grids_after_styling)

    def refresh_grids_after_styling(self):
        """Refresh grids after styling is applied"""
        if hasattr(self.main_ui, 'table_setup') and self.main_ui.table_setup:
            self.main_ui.table_setup.refresh_all_table_grids()
        else:
            print("table_setup not found - skipping grid refresh")
