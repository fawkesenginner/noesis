from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit
)
from PyQt5.QtCore import pyqtSignal, Qt, QSettings
from PyQt5.QtGui import QFont

class SettingsPage(QWidget):
    theme_changed = pyqtSignal(str)

    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.settings = QSettings()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_label = QLabel("Configurações")
        header_label.setObjectName("settingsHeader") 
        layout.addWidget(header_label)

        # Configurações de Tema
        theme_section_label = QLabel("Aparência")
        theme_section_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(theme_section_label)

        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.theme_manager.get_available_themes())
        
        last_theme_name = self.settings.value("theme/last_selected", "Ciano (Padrão)", type=str)
        current_index = self.theme_combo.findText(last_theme_name)
        if current_index != -1:
            self.theme_combo.setCurrentIndex(current_index)

        self.theme_combo.currentIndexChanged.connect(self.on_theme_selection_changed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        layout.addStretch()

    def on_theme_selection_changed(self, index):
        selected_theme = self.theme_combo.currentText()
        self.theme_manager.apply_theme(selected_theme)
        self.settings.setValue("theme/last_selected", selected_theme)
        self.theme_changed.emit(selected_theme)
