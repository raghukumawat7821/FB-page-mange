# ui_table_setup.py

from PyQt5.QtWidgets import QAbstractItemView, QHeaderView
from PyQt5.QtCore import Qt, QTimer
from utils import settings_handler


class UITableSetup:
    """Handles table setup, grid management, and selection handling for MainUI"""
    
    def __init__(self, main_ui):
        self.main_ui = main_ui

    def fix_table_selection_modes(self):
        """Fix selection modes and colors for all tables"""
        tables = [
            (self.main_ui.unified_table, "unified_table"),
            (self.main_ui.accounts_table, "accounts_table"), 
            (self.main_ui.pages_table, "pages_table")
        ]
        
        for table, name in tables:
            try:
                # Clear any existing selection issues
                table.clearSelection()
                
                # Set proper multi-selection mode
                table.setSelectionMode(QAbstractItemView.ExtendedSelection)
                
                # Ensure row-based selection
                table.setSelectionBehavior(QAbstractItemView.SelectRows)
                
                # Allow keyboard focus
                table.setFocusPolicy(Qt.StrongFocus)
                
                # Enable auto-scroll during selection
                table.setAutoScroll(True)
                
                print(f"Fixed multi-selection for {name}")
                
            except Exception as e:
                print(f"Failed to fix selection for {name}: {e}")

    def fix_empty_cells_display(self, table):
        """Keep empty cells empty - don't show placeholder text for irrelevant columns"""
        try:
            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item:
                        text = item.text()
                        
                        # Get row type to determine relevance
                        first_item = table.item(row, 0)
                        row_type = None
                        if first_item and first_item.data(Qt.UserRole):
                            data_info = first_item.data(Qt.UserRole)
                            row_type = data_info.get('type', '').lower()
                        
                        # Get column header
                        header_item = table.horizontalHeaderItem(col)
                        if header_item:
                            header_text = header_item.text()
                            
                            # KEEP IRRELEVANT COLUMNS EMPTY
                            if row_type == 'account':
                                # For account rows, keep these columns empty
                                if header_text in ['Followers', 'Last Interaction', 'Video Ends', 'Reels Ends', 'Photo Ends', 'Monetization']:
                                    if text and (text.lower() in ['none', 'null', 'no data', 'not scheduled']):
                                        item.setText('')  # Keep empty
                                    continue
                            
                            # For all rows, keep certain columns empty if no data
                            if header_text in ['Note']:
                                if not text or text.strip() == '' or text.lower() in ['none', 'null', 'no note']:
                                    item.setText('')  # Keep empty
                                    continue
                            
                            # Only fix specific columns that need meaningful defaults
                            if text and text.lower() in ['none', 'null'] and header_text in ['Pages']:
                                item.setText('0')  # Only for count columns
                                
        except Exception as e:
            print(f"Error fixing empty cells: {e}")

    def get_cell_display_text(self, item_text):
        """Get proper display text for cells, avoiding 'None' display"""
        if not item_text or item_text.strip() == '' or item_text.lower() == 'none':
            return ''  # Keep empty instead of showing placeholder
        return item_text

    def setup_table_properties(self, table, columns_info, view_type):
        """ENHANCED table setup with DOUBLE CLICK HANDLER and BETTER SCROLLBARS"""
        headers = [col['label'] for col in columns_info]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        for i, col_info in enumerate(columns_info):
            item = table.horizontalHeaderItem(i)
            item.setData(Qt.UserRole, col_info['id'])

        table.verticalHeader().setFixedWidth(50)
        table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        
        # FORCE BLACK GRID LINES
        table.setShowGrid(True)
        table.setGridStyle(Qt.SolidLine)
        
        # ENHANCED STYLING WITH BETTER SCROLLBARS
        enhanced_stylesheet = f"""
        QTableWidget #{table.objectName()} {{
            gridline-color: black !important;
            border: 1px solid #d0d0d0;
            font-size: 8pt;
            outline: none;
        }}
        
        QTableWidget#{table.objectName()}::item:selected {{
            background-color: #0078d4 !important;
            color: white !important;
        }}
        
        QHeaderView::section {{
            background-color: #f5f5f5;
            border: 1px solid black !important;
            padding: 6px;
            font-weight: bold;
            color: #404040;
            font-size: 8pt;
        }}
        
        /* ENHANCED SCROLLBARS WITH BETTER VISIBILITY */
        QScrollBar:vertical {{
            background: #E0E0E0;
            width: 14px;
            margin: 0px;
            border: 1px solid #C0C0C0;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4A90E2, stop:0.5 #357ABD, stop:1 #2E5984);
            min-height: 30px;
            border-radius: 5px;
            border: 1px solid #2E5984;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #5BA0F2, stop:0.5 #4A90E2, stop:1 #357ABD);
        }}
        
        QScrollBar::handle:vertical:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #357ABD, stop:0.5 #2E5984, stop:1 #1F4A6B);
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
        
        QScrollBar:horizontal {{
            background: #E0E0E0;
            height: 14px;
            margin: 0px;
            border: 1px solid #C0C0C0;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4A90E2, stop:0.5 #357ABD, stop:1 #2E5984);
            min-width: 30px;
            border-radius: 5px;
            border: 1px solid #2E5984;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5BA0F2, stop:0.5 #4A90E2, stop:1 #357ABD);
        }}
        
        QScrollBar::handle:horizontal:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #357ABD, stop:0.5 #2E5984, stop:1 #1F4A6B);
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        """
        table.setStyleSheet(enhanced_stylesheet)
        
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # MULTI-SELECTION SETUP
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setFocusPolicy(Qt.StrongFocus)
        table.setAutoScroll(True)
        table.clearSelection()
        
        # NEW: CONNECT DOUBLE CLICK HANDLER FOR SCHEDULE COLUMNS
        table.cellDoubleClicked.connect(
            lambda row, col: self.main_ui.handle_table_double_click(table, row, col)
        )
        
        # Enhanced responsive behavior
        header = table.horizontalHeader()
        header.setHighlightSections(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setMinimumSectionSize(80)
        header.setDefaultSectionSize(120)

        settings_handler.apply_table_layout(table, self.main_ui.settings, view_type)

    def force_grid_visibility(self, table):
        """FORCE grid lines WITHOUT clearing colors"""
        try:
            # Force refresh grid display
            table.setShowGrid(False)
            table.setShowGrid(True)
            
            # DON'T clear cell backgrounds - preserve colors
            # Just force table viewport update
            table.viewport().update()
            table.repaint()
            
        except Exception as e:
            print(f"Grid visibility refresh failed: {e}")

    def refresh_all_table_grids(self):
        """PUBLIC METHOD: Refresh grids, apply colors, and fix empty cells"""
        tables = [
            (self.main_ui.unified_table, "unified_table"),
            (self.main_ui.accounts_table, "accounts_table"), 
            (self.main_ui.pages_table, "pages_table")
        ]
        
        for table, name in tables:
            if table and hasattr(table, 'rowCount') and table.rowCount() > 0:
                print(f"Refreshing grid for {name} with {table.rowCount()} rows")
                self.force_grid_visibility(table)
                
                # NEW: Fix empty cells showing "None" - keep them empty
                self.fix_empty_cells_display(table)
        
        # APPLY DATA-BASED COLORS AFTER GRID REFRESH
        QTimer.singleShot(100, self.main_ui.styling.apply_data_based_colors)
