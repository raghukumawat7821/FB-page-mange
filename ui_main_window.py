# ui_main_window.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox,
                             QHeaderView, QLabel, QLineEdit, 
                             QAbstractItemView, QCheckBox, QStackedWidget,
                             QSplitter, QFrame, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QResizeEvent, QColor
from utils import settings_handler
from ui_components import SortableTableWidget

# FIXED: Direct imports instead of relative imports
from ui_styling import UIStyling
from ui_table_setup import UITableSetup


class MainUI(QWidget):
    # Signal for smooth state transitions
    viewChanged = pyqtSignal(str)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.current_view = "unified"
        self.window_state = {"width": 1200, "height": 800}
        
        # Initialize helper classes
        self.styling = UIStyling(self)
        self.table_setup = UITableSetup(self)
        
        # Define colors for different data types
        self.accounts_color = QColor(235, 245, 255)  # Light Blue for ALL Accounts
        self.pages_color = QColor(240, 255, 240)     # Light Green for ALL Pages
        
        self.init_ui()
        self.styling.apply_professional_styling()
        self.setup_responsive_behavior()
        
        # FIX MULTI-SELECTION AND COLORS AFTER UI SETUP
        QTimer.singleShot(500, self.table_setup.fix_table_selection_modes)

    def deselect_by_name(self):
        """Deselect all rows and clear search to allow searching by name"""
        try:
            # Deselect all rows in all tables
            for table in [self.accounts_table, self.pages_table, self.unified_table]:
                if table:
                    table.clearSelection()
                    print(f"Cleared selection in {table.objectName()}")
            
            # Clear search box
            self.search_input.clear()
            
            # Focus search box for immediate typing
            self.search_input.setFocus()
            
            print("Deselected all rows and cleared search - ready for name search")
            
        except Exception as e:
            print(f"Error in deselect_by_name: {e}")

    # NEW: Handle double clicks on table cells - especially schedule columns
    def handle_table_double_click(self, table, row, column):
        """Handle double clicks on table cells"""
        try:
            # Get column header text
            header_item = table.horizontalHeaderItem(column)
            if not header_item:
                return
            
            header_text = header_item.text()
            
            # Check if this is a schedule column
            schedule_columns = ['Video Ends', 'Reels Ends', 'Photo Ends']
            if header_text in schedule_columns:
                # Import here to avoid circular import
                try:
                    from handlers.dialog_handler import DialogHandler
                    # Get main window reference
                    main_window = self.parent()
                    if main_window:
                        dialog_handler = DialogHandler(main_window)
                        dialog_handler.handle_schedule_double_click(table, row, column)
                    else:
                        print("Could not get main window reference for dialog handler")
                except ImportError as e:
                    print(f"Could not import DialogHandler: {e}")
                except Exception as e:
                    print(f"Error opening schedule dialog: {e}")
            else:
                # Handle other column double clicks (existing functionality)
                print(f"Double clicked on {header_text} column")
                
        except Exception as e:
            print(f"Error handling table double click: {e}")

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # --- COMPACT Filter Panel ---
        self.filter_panel = QFrame()
        self.filter_panel.setObjectName("filterPanel")
        filter_panel_layout = QHBoxLayout(self.filter_panel)
        filter_panel_layout.setSpacing(6)
        filter_panel_layout.setContentsMargins(4, 4, 4, 4)
        
        # COMPACT Filter Components
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search anything...")
        self.search_input.setMaximumWidth(200)
        self.search_input.setMaximumHeight(24)
        self.search_input.setMinimumHeight(24)
        self.search_input.setObjectName("adaptiveSearch")
        
        self.show_view_filter = QComboBox()
        self.show_view_filter.addItems(["Show All", "Only Accounts", "Only Pages"])
        self.show_view_filter.setMaximumHeight(24)
        self.show_view_filter.setMinimumHeight(24)
        self.show_view_filter.setObjectName("adaptiveCombo")
        
        self.account_category_filter = QComboBox()
        self.account_category_filter.setMaximumHeight(24)
        self.account_category_filter.setMinimumHeight(24)
        self.account_category_filter.setObjectName("adaptiveCombo")
        
        self.page_category_filter = QComboBox()
        self.page_category_filter.setMaximumHeight(24)
        self.page_category_filter.setMinimumHeight(24)
        self.page_category_filter.setObjectName("adaptiveCombo")
        
        self.split_view_checkbox = QCheckBox("📋 Split View")
        self.split_view_checkbox.setMaximumHeight(24)
        self.split_view_checkbox.setObjectName("viewToggle")
        
        # INSTANT VIEW SWITCHING WITH EQUAL SPLIT SETUP
        self.split_view_checkbox.stateChanged.connect(self.instant_view_switch)

        # COMPACT Labels
        show_label = QLabel("👁️ Show:")
        search_label = QLabel("🔍 Search:")
        account_cat_label = QLabel("👤 Account:")
        page_cat_label = QLabel("📄 Page:")
        
        # Set smaller font for all labels
        compact_font = QFont()
        compact_font.setPointSize(8)
        for label in [show_label, search_label, account_cat_label, page_cat_label]:
            label.setFont(compact_font)
        
        filter_panel_layout.addWidget(show_label)
        filter_panel_layout.addWidget(self.show_view_filter)
        filter_panel_layout.addWidget(self.split_view_checkbox)
        filter_panel_layout.addSpacing(10)
        filter_panel_layout.addWidget(search_label)
        filter_panel_layout.addWidget(self.search_input)
        filter_panel_layout.addWidget(account_cat_label)
        filter_panel_layout.addWidget(self.account_category_filter)
        filter_panel_layout.addWidget(page_cat_label)
        filter_panel_layout.addWidget(self.page_category_filter)
        filter_panel_layout.addStretch()
        
        # --- COMPACT Controls Panel ---
        self.controls_panel = QFrame()
        self.controls_panel.setObjectName("controlsPanel")
        controls_layout = QHBoxLayout(self.controls_panel)
        controls_layout.setSpacing(8)
        controls_layout.setContentsMargins(4, 4, 4, 4)
        
        # COMPACT Buttons with SHORT NAMES
        self.import_accounts_btn = QPushButton("📥 Import Accounts")
        self.export_backup_btn = QPushButton("📤 Export")      # ← SHORT NAME
        self.import_backup_btn = QPushButton("📥 Import")      # ← SHORT NAME
        self.bulk_add_pages_btn = QPushButton("➕ Add Pages")
        
        # NEW: Short Deselect button
        self.deselect_by_name_btn = QPushButton("❌ Deselect")  # ← SHORT NAME
        self.deselect_by_name_btn.clicked.connect(self.deselect_by_name)
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.delete_btn = QPushButton("🗑️ Delete")
        self.recycle_bin_btn = QPushButton("♻️ Recycle Bin")
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.settings_btn = QPushButton("⚙️ Settings ▼")
        
        buttons = [self.import_accounts_btn, self.export_backup_btn, self.import_backup_btn,
                  self.bulk_add_pages_btn, self.deselect_by_name_btn, self.edit_btn, 
                  self.delete_btn, self.recycle_bin_btn, self.refresh_btn, self.settings_btn]
        
        for btn in buttons:
            btn.setMinimumHeight(28)
            btn.setMaximumHeight(28)
            btn.setObjectName("responsiveButton")
        
        # LEFT SIDE: Import/Export + Add Pages + Deselect
        left_button_layout = QHBoxLayout()
        left_button_layout.setSpacing(6)
        left_button_layout.addWidget(self.export_backup_btn)
        left_button_layout.addWidget(self.import_backup_btn)
        left_button_layout.addWidget(self.import_accounts_btn)
        left_button_layout.addWidget(self.bulk_add_pages_btn)
        left_button_layout.addWidget(self.deselect_by_name_btn)  # ← SHORT NAME BUTTON
        
        # RIGHT SIDE: Edit/Delete/etc
        right_button_layout = QHBoxLayout()
        right_button_layout.setSpacing(6)
        right_button_layout.addWidget(self.edit_btn)
        right_button_layout.addWidget(self.delete_btn)
        right_button_layout.addWidget(self.recycle_bin_btn)
        right_button_layout.addWidget(self.refresh_btn)
        right_button_layout.addWidget(self.settings_btn)
        
        controls_layout.addLayout(left_button_layout)
        controls_layout.addStretch()
        controls_layout.addLayout(right_button_layout)

        # --- Main View Area ---
        self.view_container = QFrame()
        self.view_container.setObjectName("viewContainer")
        container_layout = QVBoxLayout(self.view_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        self.view_stack = QStackedWidget()
        self.view_stack.setObjectName("animatedStack")
        container_layout.addWidget(self.view_stack)

        # View 1: Unified Table
        self.unified_table = SortableTableWidget()
        self.unified_table.setObjectName("unified_table")
        self.table_setup.setup_table_properties(self.unified_table, 
            settings_handler.ALL_COLUMNS['unified'], 'unified')
        self.unified_table.setSortableColumnsById(['status', 'profile_id', 'name', 'admin', 'category', 'page_count'])

        self.view_stack.addWidget(self.unified_table)

        # View 2: Split View
        split_view_widget = QWidget()
        split_view_widget.setObjectName("splitViewContainer")
        split_layout = QVBoxLayout(split_view_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(4)
        
        # Accounts section with BLUE THEME - SHORT NAME
        accounts_widget = QFrame()
        accounts_widget.setObjectName("accountsSection")
        accounts_widget.setStyleSheet("QFrame#accountsSection { background-color: #f0f8ff; border: 2px solid #0066cc; border-radius: 8px; }")
        accounts_layout = QVBoxLayout(accounts_widget)
        accounts_layout.setContentsMargins(6, 6, 6, 6)
        accounts_layout.setSpacing(4)
        
        self.accounts_label = QLabel("Accounts")  # ← SHORT NAME
        self.accounts_label.setStyleSheet("color: #0066cc; font-weight: bold; font-size: 10pt; padding: 4px;")
        accounts_layout.addWidget(self.accounts_label)
        
        self.accounts_table = SortableTableWidget()
        self.accounts_table.setObjectName("accounts_table")
        accounts_layout.addWidget(self.accounts_table)
        
        # Pages section with GREEN THEME - SHORT NAME
        pages_widget = QFrame()
        pages_widget.setObjectName("pagesSection")
        pages_widget.setStyleSheet("QFrame#pagesSection { background-color: #f0fff0; border: 2px solid #009900; border-radius: 8px; }")
        pages_layout = QVBoxLayout(pages_widget)
        pages_layout.setContentsMargins(6, 6, 6, 6)
        pages_layout.setSpacing(4)
        
        pages_header_layout = QHBoxLayout()
        self.pages_label = QLabel("Pages")  # ← SHORT NAME
        self.pages_label.setStyleSheet("color: #009900; font-weight: bold; font-size: 10pt; padding: 4px;")
        
        self.get_pages_btn = QPushButton("📄 Get Pages")
        self.get_pages_btn.setVisible(False)
        self.get_pages_btn.setMinimumHeight(26)
        self.get_pages_btn.setMaximumHeight(26)
        self.get_pages_btn.setObjectName("responsiveButton")
        
        pages_header_layout.addWidget(self.pages_label)
        pages_header_layout.addWidget(self.get_pages_btn)
        pages_header_layout.addStretch()
        
        pages_layout.addLayout(pages_header_layout)
        self.pages_table = SortableTableWidget()
        self.pages_table.setObjectName("pages_table")
        pages_layout.addWidget(self.pages_table)
        
        # Enhanced splitter with EQUAL SIZE SETUP
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setObjectName("adaptiveSplitter")
        self.splitter.addWidget(accounts_widget)
        self.splitter.addWidget(pages_widget)
        self.splitter.setSizes([250, 400])  # Initial sizes
        self.splitter.setChildrenCollapsible(False)
        
        split_layout.addWidget(self.splitter)
        self.view_stack.addWidget(split_view_widget)
        
        # Setup tables
        self.table_setup.setup_table_properties(self.accounts_table, 
            settings_handler.ALL_COLUMNS['accounts'], 'accounts')
        self.accounts_table.setSortableColumnsById(['status', 'profile_id', 'name', 'account_category', 'page_count'])

        self.table_setup.setup_table_properties(self.pages_table, 
            settings_handler.ALL_COLUMNS['pages'], 'pages')
        self.pages_table.setSortableColumnsById(['status', 'name', 'admin', 'category', 'monetization', 'followers'])

        # Layout Assembly
        main_layout.addWidget(self.filter_panel)
        main_layout.addWidget(self.controls_panel)
        main_layout.addWidget(self.view_container)
        self.setLayout(main_layout)

    def instant_view_switch(self, state):
        """INSTANT view switching with EQUAL SPLITTER SETUP"""
        if state == Qt.Checked:
            self.view_stack.setCurrentIndex(1)
            self.current_view = "split"
            
            # SET EQUAL SPLITTER SIZES ON SPLIT MODE ACTIVATION
            QTimer.singleShot(50, self.set_equal_splitter_sizes)
            
        else:
            self.view_stack.setCurrentIndex(0)
            self.current_view = "unified"
        
        self.viewChanged.emit(self.current_view)
        self.optimize_layout_for_current_view()

    def set_equal_splitter_sizes(self):
        """Set splitter panels to equal sizes when split view is first activated"""
        try:
            if self.splitter and self.current_view == "split":
                # Get total available height
                total_height = self.view_container.height() - 20  # Account for margins
                
                if total_height > 100:  # Only if reasonable size
                    # Set equal sizes for both panels
                    equal_size = total_height // 2
                    self.splitter.setSizes([equal_size, equal_size])
                    print(f"Set equal splitter sizes: {equal_size} x 2 = {total_height}")
                else:
                    # Fallback to default equal sizes
                    self.splitter.setSizes([300, 300])
                    print("Set fallback equal splitter sizes: 300 x 2")
                    
        except Exception as e:
            print(f"Error setting equal splitter sizes: {e}")

    def optimize_layout_for_current_view(self):
        """Optimize layout based on current view"""
        if self.current_view == "split":
            # For split view, sizes are set by set_equal_splitter_sizes
            pass
        else:
            # For unified view, no special handling needed
            pass

    def setup_responsive_behavior(self):
        """Setup responsive behavior for different screen sizes"""
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.handle_resize_complete)

    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize events smoothly"""
        super().resizeEvent(event)
        self.resize_timer.start(100)
        self.window_state["width"] = event.size().width()
        self.window_state["height"] = event.size().height()

    def handle_resize_complete(self):
        """Handle resize completion for responsive adjustments"""
        width = self.window_state["width"]
        
        if width < 1000:
            self.search_input.setMaximumWidth(160)
        else:
            self.search_input.setMaximumWidth(200)
        
        self.optimize_layout_for_current_view()

    # Delegate methods to helper classes
    def apply_data_based_colors(self):
        """Apply colors based on actual data type - Keep irrelevant cells empty"""
        return self.styling.apply_data_based_colors()

    def fix_selection_highlighting(self):
        """Force proper selection highlighting without clearing colors"""
        return self.styling.fix_selection_highlighting()

    def refresh_all_table_grids(self):
        """PUBLIC METHOD: Refresh grids, apply colors, and fix empty cells"""
        return self.table_setup.refresh_all_table_grids()
