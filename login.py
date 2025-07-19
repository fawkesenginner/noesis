import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QGraphicsDropShadowEffect, QFrame, QMessageBox
)
import auth
from dashboard import NoesisDashboard
import database

class NoesisLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noesis Login")
        self.setFixedSize(820, 500)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(self.style_sheet())
        self.init_ui()
        self.apply_shadow()

    def style_sheet(self):
        return """
        QWidget {
            background-color: transparent;
            color: white;
            font-family: 'Segoe UI';
        }
        QFrame#main_frame {
            background-color: rgba(30, 30, 30, 240);
            border-radius: 15px;
        }
        QPushButton {
            background-color: #0078D7;
            border: none;
            padding: 10px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #005999;
        }
        QLineEdit {
            padding: 10px;
            border: 1px solid #444;
            border-radius: 5px;
            background-color: #222;
            color: white;
        }
        QLabel#title {
            font-size: 28px;
            font-weight: bold;
        }
        QLabel#subtitle {
            font-size: 13px;
            color: #bbb;
        }
        QLabel#features {
            font-size: 11px;
            color: #ccc;
            line-height: 1.4;
        }
        QPushButton#close, QPushButton#min {
            background-color: transparent;
            color: white;
            font-size: 14px;
        }
        QPushButton#close:hover {
            color: red;
        }
        QPushButton#min:hover {
            color: #aaa;
        }
        QLabel#credit {
            font-size: 10px;
            color: gray;
        }
        QLabel#quote {
            font-size: 14px;
            font-style: italic;
            color: #999;
            max-width: 280px;
            margin-left: 20px;
        }
        """

    def apply_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

    def init_ui(self):
        self.old_pos = self.pos()
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignCenter)

        container = QFrame()
        container.setObjectName("main_frame")
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(40)
        container_layout.setAlignment(Qt.AlignCenter)

        left = QVBoxLayout()
        left.setAlignment(Qt.AlignCenter)
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(10)
        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setMinimumWidth(440)

        title = QLabel("NOESIS")
        title.setObjectName("title")
        subtitle = QLabel("Painel Acadêmico Inteligente")
        subtitle.setObjectName("subtitle")

        features = QLabel(
            "• Gerencie suas disciplinas e aulas\n"
            "• Armazene materiais de estudo\n"
            "• Crie notas e lembretes\n"
            "• Organize eventos e tarefas"
        )
        features.setObjectName("features")
        features.setAlignment(Qt.AlignLeft)

        credit = QLabel("Desenvolvido por Fawkes")
        credit.setObjectName("credit")
        credit.setAlignment(Qt.AlignCenter)

        left.addWidget(title)
        left.addWidget(subtitle)
        left.addSpacing(10)
        left.addWidget(features)
        left.addSpacing(60)
        left.addWidget(credit)

        right_container = QVBoxLayout()
        right_container.setAlignment(Qt.AlignCenter)
        right_container.setSpacing(12)
        right_container.setContentsMargins(0, 0, 0, 0)
        right_widget = QWidget()
        right_widget.setLayout(right_container)
        right_widget.setMinimumWidth(360)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        btn_min = QPushButton("—")
        btn_min.setObjectName("min")
        btn_min.setFixedWidth(24)
        btn_min.clicked.connect(self.showMinimized)
        btn_close = QPushButton("✕")
        btn_close.setObjectName("close")
        btn_close.setFixedWidth(24)
        btn_close.clicked.connect(self.close)
        top_bar.addWidget(btn_min)
        top_bar.addWidget(btn_close)

        user_input = QLineEdit()
        user_input.setPlaceholderText("Usuário")
        user_input.setFixedWidth(320)

        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText("Senha")
        password_input.setFixedWidth(320)

        login_btn = QPushButton("Entrar")
        login_btn.setFixedWidth(320)
        login_btn.clicked.connect(lambda: self.login(user_input.text(), password_input.text()))

        register_btn = QPushButton("Registrar")
        register_btn.setFixedWidth(320)
        register_btn.clicked.connect(lambda: self.register(user_input.text(), password_input.text()))

        visitor_btn = QPushButton("Entrar como Visitante")
        visitor_btn.setFixedWidth(320)
        visitor_btn.clicked.connect(self.enter_as_guest)

        quote = QLabel("“O sucesso é a soma de pequenos esforços repetidos dia após dia.”")
        quote.setObjectName("quote")
        quote.setWordWrap(True)
        quote.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        right_container.addLayout(top_bar)
        right_container.addSpacing(35)
        right_container.addWidget(user_input)
        right_container.addWidget(password_input)
        right_container.addSpacing(15)
        right_container.addWidget(login_btn)
        right_container.addWidget(register_btn)
        right_container.addWidget(visitor_btn)
        right_container.addSpacing(40)
        right_container.addWidget(quote)

        container_layout.addWidget(left_widget)
        container_layout.addWidget(right_widget)

        main_layout.addWidget(container)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def login(self, username, password):
        if not username or not password:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return
        if auth.validate_user(username, password):
            user_data = auth.get_user_data(username)
            if user_data:
                user_id = user_data[0]
                is_admin = bool(user_data[3])
                self.open_dashboard(username, user_id, is_admin)
            else:
                QMessageBox.warning(self, "Erro", "Erro ao obter dados do usuário.")
        else:
            QMessageBox.warning(self, "Erro", "Credenciais inválidas.")

    def register(self, username, password):
        if not username or not password:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos para registrar.")
            return
        if auth.register_user(username, password):
            QMessageBox.information(self, "Sucesso", "Usuário registrado com sucesso.")
        else:
            QMessageBox.warning(self, "Erro", "Usuário já existe.")

    def enter_as_guest(self):
        self.open_dashboard("Visitante", 0, False)

    def open_dashboard(self, username, user_id, is_admin_status):
        self.dashboard = NoesisDashboard(username, user_id, is_admin_status)
        self.dashboard.show()
        self.close()

if __name__ == "__main__":
    database.create_tables()
    app = QApplication(sys.argv)
    window = NoesisLogin()
    window.show()
    sys.exit(app.exec_())
