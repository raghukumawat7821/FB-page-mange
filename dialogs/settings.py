# dialogs/settings.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, 
                             QLabel, QPushButton, QHBoxLayout, QWidget, 
                             QListWidget, QListWidgetItem, QAbstractItemView, QCheckBox)
from utils.settings_handler import get_default_settings

class ColumnSettingsDialog(QDialog):
    """
    A dialog for users to customize table columns: reorder, show/hide.
    """
    def __init__(self, settings, view_type, all_columns_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Column Settings for {view_type.title()} View")
        self.setMinimumSize(400, 500)

        self.view_type = view_type
        self.all_columns_info = all_columns_info
        self.original_settings = settings
        self.view_settings = self.original_settings['columns'][self.view_type]

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel("Drag to reorder. Check to show/hide."))
        
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.populate_list()
        
        main_layout.addWidget(self.list_widget)
        
        button_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.button_box)
        
        main_layout.addLayout(button_layout)

    def populate_list(self):
        self.list_widget.clear()
        current_visible = self.view_settings.get('visible', {})
        current_order = self.view_settings.get('order', [c['id'] for c in self.all_columns_info])
        info_map = {c['id']: c for c in self.all_columns_info}

        for col_id in current_order:
            if col_id not in info_map: continue
            col_info = info_map[col_id]
            
            item = QListWidgetItem(self.list_widget)
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(5, 5, 5, 5)
            
            checkbox = QCheckBox(col_info['label'])
            checkbox.setChecked(current_visible.get(col_info['id'], True))
            checkbox.setProperty("col_id", col_info['id'])
            
            if col_info.get('fixed', False):
                checkbox.setEnabled(False)
                font = checkbox.font(); font.setItalic(True); checkbox.setFont(font)

            layout.addWidget(checkbox)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.setItemWidget(item, widget)

    def reset_to_defaults(self):
        default_settings = get_default_settings()
        self.view_settings = default_settings['columns'][self.view_type]
        self.populate_list()
        
    def get_updated_settings(self):
        new_order = []
        new_visible = {}
        widths = self.view_settings.get('widths', {})

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            checkbox = self.list_widget.itemWidget(item).findChild(QCheckBox)
            col_id = checkbox.property("col_id")
            new_order.append(col_id)
            new_visible[col_id] = checkbox.isChecked()
            
        self.original_settings['columns'][self.view_type]['order'] = new_order
        self.original_settings['columns'][self.view_type]['visible'] = new_visible
        self.original_settings['columns'][self.view_type]['widths'] = widths
        return self.original_settings