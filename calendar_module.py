from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCalendarWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QDateTimeEdit, QLineEdit,
    QTextEdit, QMessageBox, QFrame, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QColor, QTextCharFormat
import database
import datetime

class NoesisCalendarWidget(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.current_event_id = None
        self.initUI()
        self.load_events_for_selected_date()
        self.highlight_dates_with_events()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        page_title_label = QLabel("Meu Calendário", self)
        page_title_label.setObjectName("pageTitle")
        main_layout.addWidget(page_title_label)

        calendar_and_form_layout = QHBoxLayout()

        calendar_frame = QFrame(self)
        calendar_frame.setObjectName("calendarFrame")
        calendar_layout = QVBoxLayout(calendar_frame)
        calendar_layout.setContentsMargins(20, 20, 20, 20)
        calendar_layout.setSpacing(10)

        calendar_label = QLabel("Selecione uma Data", calendar_frame)
        calendar_label.setObjectName("sectionTitle")
        calendar_layout.addWidget(calendar_label)

        self.calendar_widget = QCalendarWidget(calendar_frame)
        self.calendar_widget.clicked[QDate].connect(self.load_events_for_selected_date)
        self.calendar_widget.clicked[QDate].connect(self.highlight_dates_with_events)
        self.calendar_widget.currentPageChanged.connect(self.highlight_dates_with_events)
        calendar_layout.addWidget(self.calendar_widget)
        calendar_and_form_layout.addWidget(calendar_frame)

        event_form_frame = QFrame(self)
        event_form_frame.setObjectName("eventFormFrame")
        event_form_layout = QVBoxLayout(event_form_frame)
        event_form_layout.setContentsMargins(20, 20, 20, 20)
        event_form_layout.setSpacing(10)

        event_form_title = QLabel("Adicionar/Editar Evento", event_form_frame)
        event_form_title.setObjectName("sectionTitle")
        event_form_layout.addWidget(event_form_title)

        event_form_layout.addWidget(QLabel("Título do Evento:", event_form_frame))
        self.event_title_input = QLineEdit(event_form_frame)
        self.event_title_input.setPlaceholderText("Título do evento...")
        event_form_layout.addWidget(self.event_title_input)

        event_form_layout.addWidget(QLabel("Descrição:", event_form_frame))
        self.event_description_input = QTextEdit(event_form_frame)
        self.event_description_input.setPlaceholderText("Detalhes do evento...")
        self.event_description_input.setMinimumHeight(60)
        event_form_layout.addWidget(self.event_description_input)

        start_end_layout = QHBoxLayout()
        start_end_layout.addWidget(QLabel("Início:", event_form_frame))
        self.start_datetime_input = QDateTimeEdit(self)
        self.start_datetime_input.setCalendarPopup(True)
        self.start_datetime_input.setDateTime(QDateTime.currentDateTime())
        start_end_layout.addWidget(self.start_datetime_input)

        start_end_layout.addWidget(QLabel("Fim (Opcional):", event_form_frame))
        self.end_datetime_input = QDateTimeEdit(self)
        self.end_datetime_input.setCalendarPopup(True)
        self.end_datetime_input.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        start_end_layout.addWidget(self.end_datetime_input)

        event_form_layout.addLayout(start_end_layout)

        button_layout = QHBoxLayout()
        self.save_event_button = QPushButton("Salvar Evento", event_form_frame)
        self.save_event_button.setObjectName("primaryButton")
        self.save_event_button.clicked.connect(self.save_event)
        button_layout.addWidget(self.save_event_button)

        self.clear_event_button = QPushButton("Limpar Campos", event_form_frame)
        self.clear_event_button.setObjectName("secondaryButton")
        self.clear_event_button.clicked.connect(self.clear_event_fields)
        button_layout.addWidget(self.clear_event_button)

        event_form_layout.addLayout(button_layout)
        event_form_layout.addStretch()
        calendar_and_form_layout.addWidget(event_form_frame)
        main_layout.addLayout(calendar_and_form_layout)

        events_list_frame = QFrame(self)
        events_list_frame.setObjectName("eventListFrame")
        events_list_layout = QVBoxLayout(events_list_frame)
        events_list_layout.setContentsMargins(20, 20, 20, 20)
        events_list_layout.setSpacing(10)

        events_list_title = QLabel("Eventos para a Data Selecionada", events_list_frame)
        events_list_title.setObjectName("sectionTitle")
        events_list_layout.addWidget(events_list_title)

        self.events_table = QTableWidget(events_list_frame)
        self.events_table.setObjectName("eventsTable")
        self.events_table.setColumnCount(5)
        self.events_table.setHorizontalHeaderLabels(["ID", "Título", "Descrição", "Início", "Fim"])
        self.events_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.events_table.hideColumn(0)
        self.events_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.events_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.events_table.itemSelectionChanged.connect(self.select_event_to_edit)
        events_list_layout.addWidget(self.events_table)

        table_button_layout = QHBoxLayout()
        self.edit_event_button = QPushButton("Editar Selecionado", events_list_frame)
        self.edit_event_button.setObjectName("secondaryButton")
        self.edit_event_button.clicked.connect(self.select_event_to_edit)
        table_button_layout.addWidget(self.edit_event_button)

        self.delete_event_button = QPushButton("Excluir Selecionado", events_list_frame)
        self.delete_event_button.setObjectName("dangerButton")
        self.delete_event_button.clicked.connect(self.delete_selected_event)
        table_button_layout.addWidget(self.delete_event_button)
        events_list_layout.addLayout(table_button_layout)

        main_layout.addWidget(events_list_frame)
        main_layout.addStretch()

    def load_events_for_selected_date(self):
        selected_date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
        self.events_table.setRowCount(0)
        events = database.get_events(self.user_id, start_date=f"{selected_date} 00:00:00", end_date=f"{selected_date} 23:59:59")
        for row_num, event in enumerate(events):
            event_id, title, description, start_dt, end_dt = event
            self.events_table.insertRow(row_num)
            self.events_table.setItem(row_num, 0, QTableWidgetItem(str(event_id)))
            self.events_table.setItem(row_num, 1, QTableWidgetItem(title))
            self.events_table.setItem(row_num, 2, QTableWidgetItem(description))
            self.events_table.setItem(row_num, 3, QTableWidgetItem(self.format_datetime(start_dt)))
            self.events_table.setItem(row_num, 4, QTableWidgetItem(self.format_datetime(end_dt)))

    def save_event(self):
        title = self.event_title_input.text().strip()
        description = self.event_description_input.toPlainText().strip()
        start_datetime = self.start_datetime_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_datetime = self.end_datetime_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        if not title:
            QMessageBox.warning(self, "Campo Vazio", "O título do evento não pode ser vazio.")
            return
        
        if self.user_id is None:
            QMessageBox.warning(self, "Erro", "Não é possível salvar eventos. Usuário não autenticado.")
            return

        if self.current_event_id:
            database.update_event(self.current_event_id, title, description, start_datetime, end_datetime)
            QMessageBox.information(self, "Sucesso", "Evento atualizado com sucesso!")
        else:
            database.add_event(self.user_id, title, description, start_datetime, end_datetime)
            QMessageBox.information(self, "Sucesso", "Evento adicionado com sucesso!")

        self.clear_event_fields()
        self.load_events_for_selected_date()
        self.highlight_dates_with_events()

    def clear_event_fields(self):
        self.event_title_input.clear()
        self.event_description_input.clear()
        self.start_datetime_input.setDateTime(QDateTime.currentDateTime())
        self.end_datetime_input.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.current_event_id = None
        self.events_table.clearSelection()

    def select_event_to_edit(self):
        selected_items = self.events_table.selectedItems()
        if not selected_items:
            self.clear_event_fields()
            return

        row = selected_items[0].row()
        event_id = int(self.events_table.item(row, 0).text())
        title = self.events_table.item(row, 1).text()
        description = self.events_table.item(row, 2).text()
        start_dt_str = self.events_table.item(row, 3).text()
        end_dt_str = self.events_table.item(row, 4).text()

        self.current_event_id = event_id
        self.event_title_input.setText(title)
        self.event_description_input.setPlainText(description)
        self.start_datetime_input.setDateTime(QDateTime.fromString(start_dt_str, "dd/MM/yyyy HH:mm"))
        if end_dt_str:
            self.end_datetime_input.setDateTime(QDateTime.fromString(end_dt_str, "dd/MM/yyyy HH:mm"))
        else:
            self.end_datetime_input.setDateTime(self.start_datetime_input.dateTime().addSecs(3600))


    def delete_selected_event(self):
        selected_items = self.events_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Nenhum Evento Selecionado", "Por favor, selecione um evento para excluir.")
            return

        reply = QMessageBox.question(self, "Confirmar Exclusão",
                                     "Tem certeza que deseja excluir este evento?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = selected_items[0].row()
            event_id = int(self.events_table.item(row, 0).text())
            database.delete_event(event_id)
            QMessageBox.information(self, "Sucesso", "Evento excluído com sucesso.")
            self.clear_event_fields()
            self.load_events_for_selected_date()
            self.highlight_dates_with_events()

    def format_datetime(self, datetime_str):
        if not datetime_str:
            return ""
        try:
            dt_object = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return dt_object.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return datetime_str

    def highlight_dates_with_events(self):
        default_format = self.calendar_widget.dateTextFormat(QDate(2000, 1, 1))
        
        current_month_first_day = self.calendar_widget.selectedDate().addDays(1 - self.calendar_widget.selectedDate().day())
        current_month_last_day = self.calendar_widget.selectedDate().addDays(self.calendar_widget.selectedDate().daysInMonth() - self.calendar_widget.selectedDate().day())
        
        temp_date = QDate(current_month_first_day)
        while temp_date <= current_month_last_day:
            self.calendar_widget.setDateTextFormat(temp_date, default_format)
            temp_date = temp_date.addDays(1)

        start_of_month_str = self.calendar_widget.selectedDate().addDays(1 - self.calendar_widget.selectedDate().day()).toString("yyyy-MM-dd 00:00:00")
        end_of_month_str = self.calendar_widget.selectedDate().addDays(self.calendar_widget.selectedDate().daysInMonth() - self.calendar_widget.selectedDate().day()).toString("yyyy-MM-dd 23:59:59")
        
        all_month_events = database.get_events(self.user_id, start_date=start_of_month_str, end_date=end_of_month_str)
            
        dates_with_events = set()
        for event in all_month_events:
            start_dt_str = event[3]
            try:
                event_date = datetime.datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M:%S").date()
                dates_with_events.add(QDate(event_date.year, event_date.month, event_date.day))
            except ValueError:
                pass

        highlight_format = QTextCharFormat(default_format)
        highlight_format.setBackground(QColor("#00aaff"))
        highlight_format.setForeground(QColor("#1A222F"))
            
        for date in dates_with_events:
            if date.month() == self.calendar_widget.selectedDate().month() and \
               date.year() == self.calendar_widget.selectedDate().year():
                self.calendar_widget.setDateTextFormat(date, highlight_format)

    def showEvent(self, event):
        super().showEvent(event)
        self.highlight_dates_with_events()

    def update_style(self, stylesheet):
        self.setStyleSheet(stylesheet)
        for child_widget in self.findChildren(QWidget):
            child_widget.style().polish(child_widget)
