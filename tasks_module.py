from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame, QDateEdit, QCheckBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate
import database
import datetime

class NoesisTasksWidget(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.current_task_id = None
        self.initUI()
        self.load_tasks()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        page_title_label = QLabel("Minhas Tarefas", self)
        page_title_label.setObjectName("pageTitle")
        main_layout.addWidget(page_title_label)

        form_frame = QFrame(self)
        form_frame.setObjectName("taskFormFrame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)

        title_label = QLabel("Título da Tarefa:", form_frame)
        form_layout.addWidget(title_label)
        self.task_title_input = QLineEdit(form_frame)
        self.task_title_input.setPlaceholderText("Título da tarefa...")
        form_layout.addWidget(self.task_title_input)

        description_label = QLabel("Descrição:", form_frame)
        form_layout.addWidget(description_label)
        self.task_description_input = QTextEdit(form_frame)
        self.task_description_input.setPlaceholderText("Detalhes da tarefa...")
        self.task_description_input.setMinimumHeight(60)
        form_layout.addWidget(self.task_description_input)

        due_date_layout = QHBoxLayout()
        due_date_layout.addWidget(QLabel("Data de Vencimento:", form_frame))
        self.task_due_date_input = QDateEdit(self)
        self.task_due_date_input.setCalendarPopup(True)
        self.task_due_date_input.setDate(QDate.currentDate())
        due_date_layout.addWidget(self.task_due_date_input)
        due_date_layout.addStretch()
        form_layout.addLayout(due_date_layout)

        self.task_completed_checkbox = QCheckBox("Tarefa Concluída", form_frame)
        form_layout.addWidget(self.task_completed_checkbox)

        button_layout = QHBoxLayout()
        self.save_task_button = QPushButton("Salvar Tarefa", form_frame)
        self.save_task_button.setObjectName("primaryButton")
        self.save_task_button.clicked.connect(self.save_task)
        button_layout.addWidget(self.save_task_button)

        self.clear_task_button = QPushButton("Limpar Campos", form_frame)
        self.clear_task_button.setObjectName("secondaryButton")
        self.clear_task_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(self.clear_task_button)

        form_layout.addLayout(button_layout)
        main_layout.addWidget(form_frame)

        tasks_table_frame = QFrame(self)
        tasks_table_frame.setObjectName("taskTableFrame")
        tasks_table_layout = QVBoxLayout(tasks_table_frame)
        tasks_table_layout.setContentsMargins(20, 20, 20, 20)
        tasks_table_layout.setSpacing(10)

        table_title = QLabel("Minhas Tarefas Salvas", tasks_table_frame)
        table_title.setObjectName("sectionTitle")
        tasks_table_layout.addWidget(table_title)

        self.tasks_table = QTableWidget(tasks_table_frame)
        self.tasks_table.setObjectName("tasksTable")
        self.tasks_table.setColumnCount(5)
        self.tasks_table.setHorizontalHeaderLabels(["ID", "Título", "Data Venc.", "Concluída", "Criada Em"])
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tasks_table.hideColumn(0)
        self.tasks_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tasks_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tasks_table.itemSelectionChanged.connect(self.select_task_to_edit)
        tasks_table_layout.addWidget(self.tasks_table)

        table_button_layout = QHBoxLayout()
        self.edit_task_button = QPushButton("Editar Selecionada", tasks_table_frame)
        self.edit_task_button.setObjectName("secondaryButton")
        self.edit_task_button.clicked.connect(self.select_task_to_edit)
        table_button_layout.addWidget(self.edit_task_button)

        self.mark_completed_button = QPushButton("Marcar/Desmarcar Concluída", tasks_table_frame)
        self.mark_completed_button.setObjectName("secondaryButton")
        self.mark_completed_button.clicked.connect(self.toggle_task_completion)
        table_button_layout.addWidget(self.mark_completed_button)

        self.delete_task_button = QPushButton("Excluir Selecionada", tasks_table_frame)
        self.delete_task_button.setObjectName("dangerButton")
        self.delete_task_button.clicked.connect(self.delete_selected_task)
        table_button_layout.addWidget(self.delete_task_button)

        tasks_table_layout.addLayout(table_button_layout)
        main_layout.addWidget(tasks_table_frame)

        main_layout.addStretch()

    def load_tasks(self):
        self.tasks_table.setRowCount(0)
        tasks = database.get_tasks(self.user_id, include_completed=True)
        for row_num, task in enumerate(tasks):
            task_id, title, description, due_date, is_completed, created_at = task
            self.tasks_table.insertRow(row_num)
            self.tasks_table.setItem(row_num, 0, QTableWidgetItem(str(task_id)))
            self.tasks_table.setItem(row_num, 1, QTableWidgetItem(title))
            self.tasks_table.setItem(row_num, 2, QTableWidgetItem(self.format_date(due_date)))
            
            completed_text = "Sim" if is_completed else "Não"
            completed_item = QTableWidgetItem(completed_text)
            completed_item.setData(Qt.UserRole, is_completed)
            self.tasks_table.setItem(row_num, 3, completed_item)
            
            self.tasks_table.setItem(row_num, 4, QTableWidgetItem(self.format_datetime(created_at)))
            
            self.tasks_table.item(row_num, 0).setData(Qt.UserRole + 1, description)

    def save_task(self):
        title = self.task_title_input.text().strip()
        description = self.task_description_input.toPlainText().strip()
        due_date = self.task_due_date_input.date().toString("yyyy-MM-dd")
        is_completed = 1 if self.task_completed_checkbox.isChecked() else 0

        if not title:
            QMessageBox.warning(self, "Campo Vazio", "O título da tarefa não pode ser vazio.")
            return

        if self.current_task_id:
            database.update_task(self.current_task_id, title, description, due_date, is_completed)
            QMessageBox.information(self, "Sucesso", "Tarefa atualizada com sucesso!")
        else:
            database.add_task(self.user_id, title, description, due_date)
            QMessageBox.information(self, "Sucesso", "Tarefa adicionada com sucesso!")

        self.clear_fields()
        self.load_tasks()

    def clear_fields(self):
        self.task_title_input.clear()
        self.task_description_input.clear()
        self.task_due_date_input.setDate(QDate.currentDate())
        self.task_completed_checkbox.setChecked(False)
        self.current_task_id = None
        self.tasks_table.clearSelection()

    def select_task_to_edit(self):
        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            self.clear_fields()
            return

        row = selected_items[0].row()
        task_id = int(self.tasks_table.item(row, 0).text())
        title = self.tasks_table.item(row, 1).text()
        due_date_str = self.tasks_table.item(row, 2).text()
        is_completed = self.tasks_table.item(row, 3).data(Qt.UserRole)
        description = self.tasks_table.item(row, 0).data(Qt.UserRole + 1)

        self.current_task_id = task_id
        self.task_title_input.setText(title)
        self.task_description_input.setPlainText(description)
        self.task_due_date_input.setDate(QDate.fromString(due_date_str, "dd/MM/yyyy"))
        self.task_completed_checkbox.setChecked(bool(is_completed))

    def delete_selected_task(self):
        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Nenhuma Tarefa Selecionada", "Por favor, selecione uma tarefa para excluir.")
            return

        reply = QMessageBox.question(self, "Confirmar Exclusão",
                                     "Tem certeza que deseja excluir esta tarefa?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = selected_items[0].row()
            task_id = int(self.tasks_table.item(row, 0).text())
            database.delete_task(task_id)
            QMessageBox.information(self, "Sucesso", "Tarefa excluída com sucesso.")
            self.clear_fields()
            self.load_tasks()

    def toggle_task_completion(self):
        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Nenhuma Tarefa Selecionada", "Por favor, selecione uma tarefa para marcar/desmarcar.")
            return
        
        row = selected_items[0].row()
        task_id = int(self.tasks_table.item(row, 0).text())
        is_completed = self.tasks_table.item(row, 3).data(Qt.UserRole)
        
        new_status = not bool(is_completed)
        database.mark_task_completed(task_id, new_status)
        QMessageBox.information(self, "Sucesso", f"Tarefa marcada como {'concluída' if new_status else 'não concluída'}.")
        self.load_tasks()

    def format_date(self, date_str):
        if not date_str:
            return ""
        try:
            dt_object = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            return dt_object.strftime("%d/%m/%Y")
        except ValueError:
            return date_str

    def format_datetime(self, datetime_str):
        if not datetime_str:
            return ""
        try:
            dt_object = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return dt_object.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return datetime_str

    def update_style(self, stylesheet):
        self.setStyleSheet(stylesheet)
        for child_widget in self.findChildren(QWidget):
            child_widget.style().polish(child_widget)
