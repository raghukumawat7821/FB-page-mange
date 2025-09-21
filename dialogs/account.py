
# dialogs/account.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, 
                             QFormLayout, QLabel, QComboBox, QTextEdit, QHBoxLayout)

class AddAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Add New Account")
        form_layout = QFormLayout(); self.profile_id_input = QLineEdit(self); self.account_name_input = QLineEdit(self)
        self.uid_input = QLineEdit(self); self.category_input = QLineEdit(self)
        form_layout.addRow(QLabel("Profile ID (Unique):"), self.profile_id_input); form_layout.addRow(QLabel("Account Name:"), self.account_name_input)
        form_layout.addRow(QLabel("UID (Unique, Optional):"), self.uid_input); form_layout.addRow(QLabel("Account Category:"), self.category_input)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        main_layout = QVBoxLayout(); main_layout.addLayout(form_layout); main_layout.addWidget(self.button_box); self.setLayout(main_layout)
    def get_data(self): return {"profile_id": self.profile_id_input.text().strip(), "account_name": self.account_name_input.text().strip(), "uid": self.uid_input.text().strip(), "category": self.category_input.text().strip()}

class EditAccountDialog(QDialog):
    def __init__(self, account_data, parent=None):
        super().__init__(parent); self.setWindowTitle("Edit Account")
        (acc_id, profile_id, acc_name, uid, cat, status, mon, proxy, proxy_loc, deleted, note) = account_data
        
        form_layout = QFormLayout(); self.profile_id_label = QLabel(f"<b>{profile_id}</b>"); self.uid_label = QLabel(f"<b>{uid or 'Not Set'}</b>")
        self.account_name_input = QLineEdit(acc_name); self.category_input = QLineEdit(cat); self.monetization_input = QLineEdit(mon); self.proxy_input = QLineEdit(proxy); self.proxy_location_input = QLineEdit(proxy_loc)
        self.note_input = QLineEdit(note)
        
        form_layout.addRow(QLabel("Profile ID:"), self.profile_id_label); form_layout.addRow(QLabel("UID:"), self.uid_label)
        form_layout.addRow(QLabel("Account Name:"), self.account_name_input); form_layout.addRow(QLabel("Account Category:"), self.category_input)
        form_layout.addRow(QLabel("Monetization:"), self.monetization_input); form_layout.addRow(QLabel("Proxy:"), self.proxy_input); form_layout.addRow(QLabel("Proxy Location:"), self.proxy_location_input)
        form_layout.addRow(QLabel("Note:"), self.note_input)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        main_layout = QVBoxLayout(); main_layout.addLayout(form_layout); main_layout.addWidget(self.button_box); self.setLayout(main_layout)
        
    def get_data(self): 
        return {
            "account_name": self.account_name_input.text().strip(), 
            "account_category": self.category_input.text().strip(), 
            "monetization": self.monetization_input.text().strip(), 
            "proxy": self.proxy_input.text().strip(), 
            "proxy_location": self.proxy_location_input.text().strip(),
            "note": self.note_input.text().strip()
        }

class ImportAccountsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Import Multiple Accounts"); self.setMinimumSize(800, 500)
        main_layout = QVBoxLayout(); self.data_input = QTextEdit(); self.data_input.setPlaceholderText("Paste your data here, one account per line."); self.data_input.setMinimumHeight(250)
        format_layout = QHBoxLayout(); self.separator_input = QLineEdit("|"); self.separator_input.setFixedWidth(30)
        self.column_options = ["(Not Used)", "Profile ID", "Account Name", "UID", "Category", "Proxy", "Proxy Location", "Monetization"]
        self.combos = [QComboBox() for _ in range(6)]
        format_layout.addWidget(QLabel("Separator:")); format_layout.addWidget(self.separator_input)
        for combo in self.combos: combo.addItems(self.column_options); format_layout.addWidget(combo)
        self.combos[0].setCurrentText("Profile ID"); self.combos[1].setCurrentText("UID"); self.combos[2].setCurrentText("Account Name")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(QLabel("Define the format of your pasted data:")); main_layout.addWidget(self.data_input); main_layout.addLayout(format_layout); main_layout.addWidget(self.button_box); self.setLayout(main_layout)
    def get_data(self):
        db_mapping = {"Profile ID": "profile_id", "Account Name": "account_name", "UID": "uid", "Category": "account_category", "Proxy": "proxy", "Proxy Location": "proxy_location", "Monetization": "monetization"}; mapping = {}
        for i, combo in enumerate(self.combos):
            text = combo.currentText()
            if text != "(Not Used)": mapping[i] = db_mapping[text]
        return {"text_data": self.data_input.toPlainText(), "separator": self.separator_input.text(), "mapping": mapping}