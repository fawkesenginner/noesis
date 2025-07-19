import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QScrollArea
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize

import database

class NoesisSettingsWidget(QWidget):
    def __init__(self, username, user_id, is_admin_status, parent=None):
        super().__init__(parent)
        self.username = username
        self.user_id = user_id
        self.is_admin = bool(is_admin_status)

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_label = QLabel("Configurações da Conta")
        header_label.setObjectName("settingsHeader")
        layout.addWidget(header_label)

        if self.is_admin:
            admin_info_label = QLabel("Você é um administrador. Opções adicionais podem estar disponíveis.")
            admin_info_label.setStyleSheet("color: green; font-weight: bold;")
            layout.addWidget(admin_info_label)

        self.username_label = QLabel(f"Nome de Usuário: {self.username}")
        self.username_label.setObjectName("settingLabel")
        layout.addWidget(self.username_label)

        self.change_password_button = QPushButton("Mudar Senha")
        self.change_password_button.setObjectName("primaryButton")
        layout.addWidget(self.change_password_button)

        self.delete_account_button = QPushButton("Excluir Conta")
        self.delete_account_button.setObjectName("dangerButton")
        layout.addWidget(self.delete_account_button)

        layout.addStretch()

    def load_settings(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings_widget = NoesisSettingsWidget("TesteUsuario", 1, 0)
    settings_widget.show()
    sys.exit(app.exec_())
