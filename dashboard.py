import sys
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSizePolicy, QScrollArea,
    QFrame, QLineEdit, QTextEdit, QMessageBox, QProgressBar
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QSettings, QCoreApplication

import database
import materials_module
import disciplines_module
import notes_module
import calendar_module
import tasks_module

from themes import ThemeManager
from settings_page import SettingsPage

from datetime import datetime, timedelta

class NoesisDashboard(QMainWindow):
    def __init__(self, username, user_id, is_admin_status, parent=None):
        super().__init__(parent)
        self.username = username
        self.user_id = user_id
        self.is_admin = bool(is_admin_status)
        self.current_active_button = None

        self.settings = QSettings()
        
        self.theme_manager = ThemeManager(QApplication.instance())
        
        last_theme_name = self.settings.value("theme/last_selected", "Ciano (Padrão)", type=str)
        self.theme_manager.apply_theme(last_theme_name)

        self.init_ui()
        self.update_welcome_message()
        self.load_quick_notes()
        self.update_dashboard_cards()

    def init_ui(self):
        self.setWindowTitle("Noesis - Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.create_sidebar()
        self.create_content_area()

        self.content_area.setCurrentIndex(0)
        self.set_active_button(self.dashboard_button)

    def create_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 20, 0, 20)
        self.sidebar_layout.setSpacing(10)
        self.sidebar_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.logo_text_label = QLabel("Noesis")
        self.logo_text_label.setAlignment(Qt.AlignCenter)
        font = QFont("Segoe UI", 20, QFont.Bold)
        self.logo_text_label.setFont(font)
        self.logo_text_label.setStyleSheet("color: #7289DA;")
        self.sidebar_layout.addWidget(self.logo_text_label)

        self.welcome_label = QLabel(f"Bem-vindo(a), {self.username}!")
        self.welcome_label.setObjectName("welcomeLabel")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.welcome_label)

        self.sidebar_layout.addSpacing(20)

        self.dashboard_button = self._create_sidebar_button("Dashboard", "icons/dashboard_icon.png")
        self.materials_button = self._create_sidebar_button("Materiais", "icons/materials_icon.png")
        self.disciplines_button = self._create_sidebar_button("Disciplinas", "icons/disciplines_icon.png")
        self.notes_button = self._create_sidebar_button("Notas", "icons/notes_icon.png")
        self.calendar_button = self._create_sidebar_button("Calendário", "icons/calendar_icon.png")
        self.tasks_button = self._create_sidebar_button("Tarefas", "icons/task_icon.png")
        self.settings_button = self._create_sidebar_button("Configurações", "icons/settings_icon.png")
        self.logout_button = self._create_sidebar_button("Sair", "icons/logout_icon.png")

        self.dashboard_button.clicked.connect(lambda: self.switch_page_and_set_active(self.dashboard_button, 0))
        self.materials_button.clicked.connect(lambda: self.switch_page_and_set_active(self.materials_button, 1))
        self.disciplines_button.clicked.connect(lambda: self.switch_page_and_set_active(self.disciplines_button, 2))
        self.notes_button.clicked.connect(lambda: self.switch_page_and_set_active(self.notes_button, 3))
        self.calendar_button.clicked.connect(lambda: self.switch_page_and_set_active(self.calendar_button, 4))
        self.tasks_button.clicked.connect(lambda: self.switch_page_and_set_active(self.tasks_button, 5))
        self.settings_button.clicked.connect(lambda: self.switch_page_and_set_active(self.settings_button, 6))
        self.logout_button.clicked.connect(self.logout)

        self.sidebar_layout.addWidget(self.dashboard_button)
        self.sidebar_layout.addWidget(self.materials_button)
        self.sidebar_layout.addWidget(self.disciplines_button)
        self.sidebar_layout.addWidget(self.notes_button)
        self.sidebar_layout.addWidget(self.calendar_button)
        self.sidebar_layout.addWidget(self.tasks_button)
        self.sidebar_layout.addWidget(self.settings_button)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.logout_button)

        self.main_layout.addWidget(self.sidebar)

    def set_active_button(self, button_to_activate):
        if self.current_active_button:
            self.current_active_button.setProperty("active", "false")
            self.current_active_button.style().polish(self.current_active_button)
            
        button_to_activate.setProperty("active", "true")
        self.current_active_button = button_to_activate
        self.current_active_button.style().polish(self.current_active_button)

    def switch_page_and_set_active(self, button, index):
        self.content_area.setCurrentIndex(index)
        self.set_active_button(button)

    def _create_sidebar_button(self, text, icon_path):
        button = QPushButton(text)
        button.setObjectName("sidebarButton")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_icon_path = os.path.join(current_dir, icon_path)

        icon = QIcon(full_icon_path)
        if icon.isNull():
            print(f"Aviso: Ícone não encontrado em {full_icon_path} para o botão '{text}'")
        
        button.setIcon(icon)
        button.setIconSize(QSize(24, 24))
        button.setProperty("active", "false")
        return button

    def create_content_area(self):
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("contentArea")
        self.main_layout.addWidget(self.content_area)

        self.dashboard_home_page = self.create_dashboard_home_page()
        self.materials_page = materials_module.NoesisMaterialsWidget(self.user_id)
        self.disciplines_page = disciplines_module.NoesisDisciplinesWidget()
        self.notes_page = notes_module.NoesisFullNotesWidget(self.user_id)
        self.calendar_page = calendar_module.NoesisCalendarWidget(self.user_id)
        self.tasks_page = tasks_module.NoesisTasksWidget(self.user_id)
        self.settings_page = SettingsPage(self.theme_manager)

        self.content_area.addWidget(self.dashboard_home_page)
        self.content_area.addWidget(self.materials_page)
        self.content_area.addWidget(self.disciplines_page)
        self.content_area.addWidget(self.notes_page)
        self.content_area.addWidget(self.calendar_page)
        self.content_area.addWidget(self.tasks_page)
        self.content_area.addWidget(self.settings_page)

        self.settings_page.theme_changed.connect(self.handle_theme_change)

    def create_dashboard_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_label = QLabel("Visão Geral do Dashboard")
        header_label.setObjectName("dashboardHeader")
        layout.addWidget(header_label)

        self.cards_layout = QHBoxLayout()
        self.card_progress_label = QLabel("Carregando...")
        self.card_progress_bar = QProgressBar(self)
        self.card_progress = self._add_dashboard_card("Progresso Geral", self.card_progress_label, self.card_progress_bar)

        self.card_next_class_label = QLabel("Carregando...")
        self.card_next_class = self._add_dashboard_card("Próxima Aula", self.card_next_class_label)
        
        self.card_pending_tasks_label = QLabel("Carregando...")
        self.card_pending_tasks = self._add_dashboard_card("Tarefas Pendentes", self.card_pending_tasks_label)
        
        self.card_recent_materials_label = QLabel("Carregando...")
        self.card_recent_materials = self._add_dashboard_card("Materiais Recentes", self.card_recent_materials_label)

        self.cards_layout.addWidget(self.card_progress)
        self.cards_layout.addWidget(self.card_next_class)
        self.cards_layout.addWidget(self.card_pending_tasks)
        self.cards_layout.addWidget(self.card_recent_materials)
        layout.addLayout(self.cards_layout)

        layout.addSpacing(30)

        notes_tasks_layout = QHBoxLayout()

        self.quick_notes_card = self.create_quick_notes_card()
        notes_tasks_layout.addWidget(self.quick_notes_card, 1)

        self.upcoming_tasks_card = self.create_upcoming_tasks_card()
        notes_tasks_layout.addWidget(self.upcoming_tasks_card, 1)

        layout.addLayout(notes_tasks_layout)

        layout.addStretch()

        return page

    def _add_dashboard_card(self, title, content_widget, extra_widget=None):
        card_frame = QFrame()
        card_frame.setObjectName("dashboardCard")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        card_layout.addWidget(title_label)

        if isinstance(content_widget, QLabel):
            content_widget.setObjectName("cardContent")
            content_widget.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(content_widget)
        else:
            card_layout.addWidget(content_widget)

        if extra_widget:
            card_layout.addWidget(extra_widget)
            
        card_layout.addStretch()
        return card_frame

    def update_welcome_message(self):
        if self.username == "Visitante":
            self.welcome_label.setText("Bem-vindo(a), Visitante!")
        else:
            self.welcome_label.setText(f"Bem-vindo(a), {self.username}!")

    def load_quick_notes(self):
        if self.user_id is None:
            self.quick_notes_area.setText("Notas rápidas não disponíveis para visitantes.")
            return

        notes = database.get_notes(self.user_id, limit=3)
        if notes:
            notes_text = ""
            for note_id, content, created_at in notes:
                notes_text += f"- {content}\n"
            self.quick_notes_area.setText(notes_text)
        else:
            self.quick_notes_area.setText("Nenhuma nota rápida adicionada ainda.")

    def add_quick_note(self):
        if self.user_id is None:
            QMessageBox.warning(self, "Aviso", "Funcionalidade de nota não disponível para visitantes.")
            return

        content = self.quick_note_input.text().strip()
        if content:
            database.add_note(self.user_id, content)
            self.quick_note_input.clear()
            self.load_quick_notes()
            QMessageBox.information(self, "Sucesso", "Nota rápida adicionada!")
        else:
            QMessageBox.warning(self, "Erro", "A nota não pode estar vazia.")

    def create_quick_notes_card(self):
        card_frame = QFrame()
        card_frame.setObjectName("dashboardCard")
        layout = QVBoxLayout(card_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title_label = QLabel("Notas Rápidas")
        title_label.setObjectName("cardTitle")
        layout.addWidget(title_label)

        self.quick_notes_area = QTextEdit()
        self.quick_notes_area.setReadOnly(True)
        self.quick_notes_area.setObjectName("quickNotesArea")
        self.quick_notes_area.setFixedHeight(100)
        layout.addWidget(self.quick_notes_area)

        self.quick_note_input = QLineEdit()
        self.quick_note_input.setPlaceholderText("Adicione uma nota rápida...")
        self.quick_note_input.setObjectName("quickNoteInput")
        layout.addWidget(self.quick_note_input)

        add_note_button = QPushButton("Adicionar Nota")
        add_note_button.setObjectName("primaryButton")
        add_note_button.clicked.connect(self.add_quick_note)
        layout.addWidget(add_note_button)

        layout.addStretch()
        return card_frame

    def create_upcoming_tasks_card(self):
        card_frame = QFrame()
        card_frame.setObjectName("dashboardCard")
        layout = QVBoxLayout(card_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title_label = QLabel("Próximas Tarefas")
        title_label.setObjectName("cardTitle")
        layout.addWidget(title_label)

        self.upcoming_tasks_area = QTextEdit()
        self.upcoming_tasks_area.setReadOnly(True)
        self.upcoming_tasks_area.setObjectName("upcomingTasksArea")
        self.upcoming_tasks_area.setFixedHeight(150)
        layout.addWidget(self.upcoming_tasks_area)
        
        layout.addStretch()
        return card_frame

    def load_upcoming_tasks(self):
        if self.user_id is None:
            self.upcoming_tasks_area.setText("Tarefas não disponíveis para visitantes.")
            return

        tasks = database.get_tasks(self.user_id, include_completed=False)
        if tasks:
            tasks_text = ""
            for task_id, title, description, due_date, is_completed, created_at in tasks[:5]:
                due_date_str = f" ({due_date})" if due_date else ""
                tasks_text += f"- {title}{due_date_str}\n"
            self.upcoming_tasks_area.setText(tasks_text)
        else:
            self.upcoming_tasks_area.setText("Nenhuma tarefa pendente.")

    def update_dashboard_cards(self):
        if self.user_id is None:
            self.card_progress_label.setText("N/A")
            self.card_next_class_label.setText("N/A")
            self.card_pending_tasks_label.setText("N/A")
            self.card_recent_materials_label.setText("N/A")
            self.card_progress_bar.setValue(0)
            self.upcoming_tasks_area.setText("Tarefas não disponíveis para visitantes.")
            self.quick_notes_area.setText("Notas não disponíveis para visitantes.")
            return

        self.load_upcoming_tasks()

        num_pending_tasks = len(database.get_tasks(self.user_id, include_completed=False))
        self.card_pending_tasks_label.setText(str(num_pending_tasks))

        recent_materials = database.get_materials()
        if recent_materials:
            # Assuming latest_material[1] is discipline name and [2] is title from previous database.py version
            # With updated database.py, get_materials returns (id, title, type, file_path, discipline_id, lesson_id, description, uploaded_at)
            # So, latest_material[1] is title and you might want to show description or file_path as well.
            # To show discipline name, you'd need to fetch it using latest_material[4] (discipline_id)
            
            # Option 1: Just show title
            # self.card_recent_materials_label.setText(f"{recent_materials[0][1]}") 
            
            # Option 2: Show title and discipline name (requires fetching discipline name)
            discipline_name = database.get_discipline_name(recent_materials[0][4]) if recent_materials[0][4] else "N/A"
            self.card_recent_materials_label.setText(f"{recent_materials[0][1]} ({discipline_name})")
        else:
            self.card_recent_materials_label.setText("Nenhum material.")

        self.card_next_class_label.setText("Em Breve")
        self.card_progress_label.setText("Em Andamento")
        self.card_progress_bar.setValue(50) # Exemplo de progresso

    def handle_theme_change(self, theme_name):
        # Apply the theme globally via ThemeManager.
        # This will set the stylesheet for QApplication.instance()
        self.theme_manager.apply_theme(theme_name)
        
        # Get the stylesheet string that was just applied by the ThemeManager
        # This assumes ThemeManager has a way to retrieve the current stylesheet,
        # or you manually load it again here.
        # A robust way is to pass the stylesheet string *from* the ThemeManager signal.
        # If your ThemeManager.theme_changed signal emits the stylesheet string directly:
        # self.settings_page.theme_changed.connect(lambda name, style: self.handle_theme_change(name, style))
        # For now, let's assume QApplication.instance().styleSheet() returns the current one,
        # or we re-load it based on theme_name.
        
        # Method 1: Get stylesheet from QApplication (if ThemeManager already applied it)
        stylesheet = QApplication.instance().styleSheet()

        # Or, if ThemeManager had a method to return the stylesheet:
        # stylesheet = self.theme_manager.get_current_stylesheet_string() 
        # (You might need to add this method to your ThemeManager class)

        # Or, manually load it again (if ThemeManager just applies and doesn't return):
        # You'd need a similar `load_stylesheet` method as in my previous response if you don't have one.
        # This makes more sense if ThemeManager doesn't give you the string back directly.
        # stylesheet = self.settings_page.load_stylesheet(theme_name) # Assuming SettingsPage has this method

        # Re-polish widgets that need explicit refreshing
        self.central_widget.style().polish(self.central_widget)
        for btn in [self.dashboard_button, self.materials_button, self.disciplines_button,
                    self.notes_button, self.calendar_button, self.tasks_button,
                    self.settings_button, self.logout_button]:
            btn.style().polish(btn)
        
        # Now, call update_style on each page, passing the stylesheet
        # This is where the correction happens.
        if hasattr(self, 'materials_page') and self.materials_page:
            self.materials_page.update_style(stylesheet) # Pass the stylesheet
        if hasattr(self, 'disciplines_page') and self.disciplines_page:
            self.disciplines_page.update_style(stylesheet) # Pass the stylesheet
        if hasattr(self, 'notes_page') and self.notes_page:
            self.notes_page.update_style(stylesheet) # Pass the stylesheet
        if hasattr(self, 'calendar_page') and self.calendar_page:
            self.calendar_page.update_style(stylesheet) # Pass the stylesheet
        if hasattr(self, 'tasks_page') and self.tasks_page:
            self.tasks_page.update_style(stylesheet) # Pass the stylesheet

        # The dashboard_home_page usually only needs polishing, as its elements are direct children of DashboardWindow
        self.dashboard_home_page.style().polish(self.dashboard_home_page)


    def logout(self):
        confirm = QMessageBox.question(self, "Sair", "Tem certeza que deseja sair?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            from login import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
