# ui_components/sortable_table.py

from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtCore import Qt

class SortableTableWidget(QTableWidget):
    """
    An enhanced QTableWidget that supports selective column sorting and a custom
    sorting method for the unified view to keep accounts and pages grouped.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSortingEnabled(False) # We handle sorting manually
        self._sortable_columns_by_id = []
        self._current_sort_column = -1
        self._current_sort_order = Qt.AscendingOrder
        self.horizontalHeader().sectionClicked.connect(self._handle_header_click)

    def setSortableColumnsById(self, columns_ids):
        """
        Sets which columns are allowed to be sorted.
        Args:
            columns_ids (list): A list of column ID strings that are sortable.
        """
        self._sortable_columns_by_id = columns_ids

    def _handle_header_click(self, logicalIndex):
        """
        Handles a click on a header section. It checks if the column is sortable
        before proceeding with the sort.
        """
        header_item = self.horizontalHeaderItem(logicalIndex)
        if not header_item: return
        
        column_id = header_item.data(Qt.UserRole)
        
        # Enforce selective sorting: if the column ID isn't in our allowed list, do nothing.
        if column_id not in self._sortable_columns_by_id:
            # Keep the sort indicator on the previously sorted column
            if self._current_sort_column != -1:
                self.horizontalHeader().setSortIndicator(self._current_sort_column, self._current_sort_order)
            return

        # Determine the new sort order
        if self._current_sort_column == logicalIndex:
            new_order = Qt.DescendingOrder if self._current_sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            new_order = Qt.AscendingOrder
            
        self._current_sort_column = logicalIndex
        self._current_sort_order = new_order

        # Set the visual sort indicator on the header
        self.horizontalHeader().setSortIndicator(logicalIndex, new_order)
        # Trigger the custom sorting logic
        self.customSort(logicalIndex, new_order)

    def customSort(self, column, order):
        """
        Performs sorting. It dynamically chooses the sorting method based on the table's content.
        - If the table contains account groups (like in "Show All" view), it sorts the groups.
        - If the table contains only pages (like in "Only Pages" view), it performs a standard row sort.
        """
        # This logic is primarily for the unified table. Other tables can use standard sorting.
        if self.objectName() != "unified_table":
            self.sortByColumn(column, order)
            return

        # Check if the table is in "group mode" (contains account rows)
        is_group_mode = False
        if self.rowCount() > 0:
            first_item = self.item(0, 0)
            if first_item and first_item.data(Qt.UserRole):
                item_data = first_item.data(Qt.UserRole)
                if item_data.get('type') == 'account':
                    is_group_mode = True
        
        if is_group_mode:
            # -- GROUP SORTING LOGIC (for "Show All" view) --
            all_rows_data = []
            for row in range(self.rowCount()):
                row_items = [self.takeItem(row, col) for col in range(self.columnCount())]
                all_rows_data.append(row_items)

            groups = {}
            current_account_id = None
            for row_items in all_rows_data:
                item_with_data = row_items[0]
                if item_with_data and item_with_data.data(Qt.UserRole):
                    data = item_with_data.data(Qt.UserRole)
                    is_account_row = data.get('type') == 'account'
                    if is_account_row:
                        current_account_id = data['id']
                        groups[current_account_id] = {'account_row_items': row_items, 'page_rows_items': []}
                    elif current_account_id in groups:
                        groups[current_account_id]['page_rows_items'].append(row_items)

            def sort_key(item):
                account_row_items = item[1]['account_row_items']
                if account_row_items and column < len(account_row_items) and account_row_items[column]:
                    return account_row_items[column].text()
                return ""

            sorted_groups = sorted(groups.items(), key=sort_key, reverse=(order == Qt.DescendingOrder))
            
            self.setRowCount(0)
            
            for account_id, data in sorted_groups:
                if not data['account_row_items']: continue
                
                row_pos = self.rowCount()
                self.insertRow(row_pos)
                for col, item in enumerate(data['account_row_items']):
                    self.setItem(row_pos, col, item)
                
                for page_row_data in data['page_rows_items']:
                    row_pos = self.rowCount()
                    self.insertRow(row_pos)
                    for col, item in enumerate(page_row_data):
                        self.setItem(row_pos, col, item)
        else:
            # -- STANDARD SORTING LOGIC (for "Only Pages" view) --
            self.sortByColumn(column, order)