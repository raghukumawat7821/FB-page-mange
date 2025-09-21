# dialogs/utility.py

import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, 
                             QFormLayout, QLabel, QTextEdit, QHBoxLayout,
                             QPushButton, QCompleter, QStyledItemDelegate,
                             QMessageBox)
from PyQt5.QtCore import Qt

class CompleterDelegate(QStyledItemDelegate):
    def __init__(self, parent, completion_list):
        super().__init__(parent)
        self.completion_list = completion_list

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        completer = QCompleter(self.completion_list, parent)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        editor.setCompleter(completer)
        return editor

class NoteDialog(QDialog):
    def __init__(self, current_note="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Note")
        self.setMinimumSize(400, 300)
        
        main_layout = QVBoxLayout(self)
        self.note_edit = QTextEdit(self)
        self.note_edit.setText(current_note)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(self.note_edit)
        main_layout.addWidget(self.button_box)

    def get_note(self):
        return self.note_edit.toPlainText().strip()