# dialogs/recycle_bin.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, 
                             QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QAbstractItemView, QFormLayout)

class RecycleBinDialog(QDialog):
    def __init__(self, deleted_items, parent=None):
        super().__init__(parent); self.setWindowTitle("Recycle Bin"); self.setMinimumSize(600, 400)
        main_layout = QVBoxLayout(); self.table = QTableWidget(); self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "ID"]); self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers); self.table.setColumnHidden(2, True); self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.populate_table(deleted_items)
        button_layout = QHBoxLayout(); self.restore_btn = QPushButton("Restore Selected"); self.delete_perm_btn = QPushButton("Delete Permanently"); self.close_btn = QPushButton("Close")
        button_layout.addStretch(); button_layout.addWidget(self.restore_btn); button_layout.addWidget(self.delete_perm_btn); button_layout.addWidget(self.close_btn)
        self.restore_btn.clicked.connect(self.restore_selected); self.delete_perm_btn.clicked.connect(self.delete_permanently); self.close_btn.clicked.connect(self.accept)
        main_layout.addWidget(self.table); main_layout.addLayout(button_layout); self.setLayout(main_layout)
    def populate_table(self, items):
        for item_id, name, _, item_type in items: row = self.table.rowCount(); self.table.insertRow(row); self.table.setItem(row, 0, QTableWidgetItem(name)); self.table.setItem(row, 1, QTableWidgetItem(item_type)); self.table.setItem(row, 2, QTableWidgetItem(str(item_id)))
    def get_selected_items(self):
        selected = [];
        for item in self.table.selectedItems():
            row = item.row(); item_type = self.table.item(row, 1).text(); item_id = int(self.table.item(row, 2).text())
            if (item_type, item_id) not in selected: selected.append((item_type, item_id))
        return selected
    def restore_selected(self): self.done(1)
    def delete_permanently(self): self.done(2)

class ConfirmDeleteDialog(QDialog):
    def __init__(self, num_accounts, num_pages, dependent_pages, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Permanent Deletion")
        
        main_layout = QVBoxLayout(self)
        
        message = f"You are about to permanently delete:\n\n"
        if num_accounts > 0:
            message += f"  • <b>{num_accounts}</b> account(s)\n"
        if num_pages > 0:
            message += f"  • <b>{num_pages}</b> page(s)\n\n"
        if dependent_pages > 0:
            message += f"Deleting these accounts will also permanently delete <b>{dependent_pages}</b> associated pages.\n"
        
        message += "\nThis action <b>CANNOT</b> be undone."

        self.label = QLabel(message)
        main_layout.addWidget(self.label)
        
        form_layout = QFormLayout()
        self.confirm_input = QLineEdit(self)
        self.confirm_input.setPlaceholderText("Type DELETE to confirm")
        form_layout.addRow(QLabel("Please type <b>DELETE</b> to confirm:"), self.confirm_input)
        main_layout.addLayout(form_layout)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.ok_button = self.button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setText("Confirm Deletion")
        self.ok_button.setEnabled(False)
        
        self.confirm_input.textChanged.connect(self.check_confirmation_text)
        
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(self.button_box)
        
    def check_confirmation_text(self, text):
        if text == "DELETE":
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)