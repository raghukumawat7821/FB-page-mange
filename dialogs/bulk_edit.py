# dialogs/bulk_edit.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox)
from PyQt5.QtCore import Qt
from utils import log

class BulkEditAccountsDialog(QDialog):
    def __init__(self, accounts_data, account_categories, parent=None):
        super().__init__(parent); self.setWindowTitle(f"Bulk Edit {len(accounts_data)} Accounts"); self.setMinimumSize(900, 400)
        main_layout = QVBoxLayout(self); self.table = QTableWidget()
        self.table.setColumnCount(6); self.table.setHorizontalHeaderLabels(["Profile ID", "Account Name", "Category", "Monetization", "Proxy", "Proxy Location"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setFixedWidth(40)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.accounts_data = accounts_data
        
        self._edited_cells = set()
        self.populate_table(account_categories)
        self.table.cellChanged.connect(self._mark_edited)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.table); main_layout.addWidget(self.button_box)

    def _mark_edited(self, row, column):
        self._edited_cells.add((row, column))

    def populate_table(self, account_categories):
        for row, acc in enumerate(self.accounts_data):
            self.table.insertRow(row)
            
            profile_item = QTableWidgetItem(acc[1]); profile_item.setData(Qt.UserRole, acc[0])
            profile_item.setFlags(profile_item.flags() & ~Qt.ItemIsEditable); profile_item.setTextAlignment(Qt.AlignCenter)
            
            name_item = QTableWidgetItem(acc[2])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable); name_item.setTextAlignment(Qt.AlignCenter)
            
            self.table.setItem(row, 0, profile_item)
            self.table.setItem(row, 1, name_item)
            
            cat_combo = QComboBox()
            cat_combo.setEditable(True)
            cat_combo.addItems(account_categories)
            cat_combo.lineEdit().setText(acc[4] or "") # account_category is at index 4
            cat_combo.currentTextChanged.connect(lambda text, r=row: self._mark_edited(r, 2))
            self.table.setCellWidget(row, 2, cat_combo)
            
            self.table.setItem(row, 3, QTableWidgetItem(acc[6] or "")) # monetization is at index 6
            self.table.setItem(row, 4, QTableWidgetItem(acc[7] or "")) # proxy is at index 7
            self.table.setItem(row, 5, QTableWidgetItem(acc[8] or "")) # proxy_location is at index 8

    def get_data(self):
        updated_data = []
        for row in range(self.table.rowCount()):
            fields_to_update = {}
            if (row, 2) in self._edited_cells: fields_to_update['account_category'] = self.table.cellWidget(row, 2).currentText().strip()
            if (row, 3) in self._edited_cells: fields_to_update['monetization'] = self.table.item(row, 3).text().strip()
            if (row, 4) in self._edited_cells: fields_to_update['proxy'] = self.table.item(row, 4).text().strip()
            if (row, 5) in self._edited_cells: fields_to_update['proxy_location'] = self.table.item(row, 5).text().strip()

            if fields_to_update:
                fields_to_update['account_id'] = self.table.item(row, 0).data(Qt.UserRole)
                updated_data.append(fields_to_update)
        return updated_data

class BulkEditPagesDialog(QDialog):
    def __init__(self, pages_data, all_accounts, parent=None):
        super().__init__(parent); self.setWindowTitle(f"Bulk Edit {len(pages_data)} Pages"); self.setMinimumSize(900, 400)
        main_layout = QVBoxLayout(self); self.table = QTableWidget()
        self.table.setColumnCount(6); self.table.setHorizontalHeaderLabels(["Current Account", "Page Name", "UID/Page ID", "Category", "Monetization", "Move to Account"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive); self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.verticalHeader().setFixedWidth(40)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.pages_data = pages_data; self.all_accounts = all_accounts
        
        self._edited_cells = set()
        self.populate_table()
        self.table.cellChanged.connect(self._mark_edited)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.table); main_layout.addWidget(self.button_box)

    def _mark_edited(self, row, column):
        self._edited_cells.add((row, column))

    def populate_table(self):
        for row, page in enumerate(self.pages_data):
            self.table.insertRow(row)
            (page_id, page_name, uid, cat, mon, acc_id, profile_id) = page
            
            acc_item = QTableWidgetItem(profile_id); acc_item.setData(Qt.UserRole, page_id)
            acc_item.setFlags(acc_item.flags() & ~Qt.ItemIsEditable); acc_item.setTextAlignment(Qt.AlignCenter)
            
            self.table.setItem(row, 0, acc_item)
            self.table.setItem(row, 1, QTableWidgetItem(page_name))
            self.table.setItem(row, 2, QTableWidgetItem(uid or ""))
            self.table.setItem(row, 3, QTableWidgetItem(cat or ""))
            self.table.setItem(row, 4, QTableWidgetItem(mon or ""))

            combo = QComboBox()
            combo.addItem(f"{profile_id} (Current)", acc_id)
            for a_id, p_id, a_name in self.all_accounts:
                if a_id != acc_id: combo.addItem(f"{p_id} ({a_name})", a_id)
            combo.currentIndexChanged.connect(lambda index, r=row: self._mark_edited(r, 5))
            self.table.setCellWidget(row, 5, combo)

    def get_data(self):
        updated_data = []
        for row in range(self.table.rowCount()):
            fields_to_update = {}
            if (row, 1) in self._edited_cells: fields_to_update['page_name'] = self.table.item(row, 1).text().strip()
            if (row, 2) in self._edited_cells: fields_to_update['uid_page_id'] = self.table.item(row, 2).text().strip()
            if (row, 3) in self._edited_cells: fields_to_update['category'] = self.table.item(row, 3).text().strip()
            if (row, 4) in self._edited_cells: fields_to_update['monetization'] = self.table.item(row, 4).text().strip()
            if (row, 5) in self._edited_cells: fields_to_update['linked_account_id'] = self.table.cellWidget(row, 5).currentData()
            
            if fields_to_update:
                fields_to_update['page_id'] = self.table.item(row, 0).data(Qt.UserRole)
                updated_data.append(fields_to_update)
        return updated_data

class BulkProxyDialog(QDialog):
    def __init__(self, accounts_data, parent=None):
        super().__init__(parent); self.setWindowTitle("Bulk Edit Proxies"); self.setMinimumSize(600, 400)
        main_layout = QVBoxLayout(self); self.table = QTableWidget()
        self.table.setColumnCount(3); self.table.setHorizontalHeaderLabels(["Profile ID", "Proxy", "Proxy Location"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self._edited_cells = set()
        self.populate_table(accounts_data)
        self.table.cellChanged.connect(self._mark_edited)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(self.table); main_layout.addWidget(self.button_box)

    def _mark_edited(self, row, column):
        self._edited_cells.add((row, column))

    def populate_table(self, accounts_data):
        for row, row_data in enumerate(accounts_data):
            if len(row_data) < 4:
                log.warning(f"Skipping malformed row in BulkProxyDialog: {row_data}")
                continue

            self.table.insertRow(row)
            acc_id, profile_id, proxy, proxy_loc = row_data[0], row_data[1], row_data[2], row_data[3]
            
            item = QTableWidgetItem(profile_id); item.setData(Qt.UserRole, acc_id)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item)
            self.table.setItem(row, 1, QTableWidgetItem(proxy or ""))
            self.table.setItem(row, 2, QTableWidgetItem(proxy_loc or ""))

    def get_data(self):
        updated_data = []
        for row in range(self.table.rowCount()):
            fields_to_update = {}
            if (row, 1) in self._edited_cells: fields_to_update['proxy'] = self.table.item(row, 1).text().strip()
            if (row, 2) in self._edited_cells: fields_to_update['proxy_location'] = self.table.item(row, 2).text().strip()
            
            if fields_to_update:
                fields_to_update['account_id'] = self.table.item(row, 0).data(Qt.UserRole)
                updated_data.append(fields_to_update)
        return updated_data