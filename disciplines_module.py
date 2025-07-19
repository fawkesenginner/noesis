from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
import database

class NoesisDisciplinesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("disciplinesPage")
        self.current_discipline_id = None
        self.initUI()
        self.load_disciplines()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Gerenciamento de Disciplinas", self)
        title_label.setObjectName("pageTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        form_frame = QFrame(self)
        form_frame.setObjectName("disciplineFormFrame")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.discipline_name_input = QLineEdit(self)
        self.discipline_name_input.setPlaceholderText("Nome da Disciplina (ex: Programação Python)")
        form_layout.addRow("Nome da Disciplina:", self.discipline_name_input)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar Disciplina", self)
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_discipline)
        button_layout.addWidget(self.save_button)

        self.clear_button = QPushButton("Limpar Formulário", self)
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_button)

        form_layout.addRow("", button_layout)

        main_layout.addWidget(form_frame)

        disciplines_list_label = QLabel("Minhas Disciplinas Cadastradas", self)
        disciplines_list_label.setObjectName("sectionTitle")
        main_layout.addWidget(disciplines_list_label)

        self.disciplines_table = QTableWidget(self)
        self.disciplines_table.setObjectName("disciplinesTable")
        self.disciplines_table.setColumnCount(2)
        self.disciplines_table.setHorizontalHeaderLabels(["ID", "Nome da Disciplina"])
        self.disciplines_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.disciplines_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.disciplines_table.setSelectionMode(QTableWidget.SingleSelection)
        self.disciplines_table.horizontalHeader().setStretchLastSection(True)
        self.disciplines_table.hideColumn(0)

        table_button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Editar Selecionado", self)
        self.edit_button.setObjectName("secondaryButton")
        self.edit_button.clicked.connect(self.edit_selected_discipline)
        table_button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Excluir Selecionado", self)
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self.delete_selected_discipline)
        table_button_layout.addWidget(self.delete_button)

        main_layout.addWidget(self.disciplines_table)
        main_layout.addLayout(table_button_layout)

        self.setLayout(main_layout)

    def save_discipline(self):
        name = self.discipline_name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Campo Obrigatório", "Por favor, digite o nome da disciplina.")
            return

        if self.current_discipline_id is None:
            if database.add_discipline(name):
                QMessageBox.information(self, "Sucesso", "Disciplina adicionada com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Disciplina com este nome já existe.")
        else:
            if database.update_discipline(self.current_discipline_id, name):
                QMessageBox.information(self, "Sucesso", "Disciplina atualizada com sucesso!")
                self.current_discipline_id = None
            else:
                QMessageBox.warning(self, "Erro", "Disciplina com este nome já existe.")

        self.clear_form()
        self.load_disciplines()

    def load_disciplines(self):
        self.disciplines_table.setRowCount(0)
        disciplines = database.get_disciplines()

        for row_num, discipline in enumerate(disciplines):
            self.disciplines_table.insertRow(row_num)
            self.disciplines_table.setItem(row_num, 0, QTableWidgetItem(str(discipline[0])))
            self.disciplines_table.setItem(row_num, 1, QTableWidgetItem(discipline[1]))
        
        self.disciplines_table.resizeColumnsToContents()

    def edit_selected_discipline(self):
        selected_rows = self.disciplines_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione uma disciplina para editar.")
            return

        row = selected_rows[0].row()
        self.current_discipline_id = int(self.disciplines_table.item(row, 0).text())
        discipline_name = self.disciplines_table.item(row, 1).text()
        
        self.discipline_name_input.setText(discipline_name)
        self.save_button.setText("Atualizar Disciplina")

    def delete_selected_discipline(self):
        selected_rows = self.disciplines_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione uma disciplina para excluir.")
            return

        row = selected_rows[0].row()
        discipline_id = int(self.disciplines_table.item(row, 0).text())
        discipline_name = self.disciplines_table.item(row, 1).text()

        reply = QMessageBox.question(self, "Confirmação de Exclusão",
                                     f"Tem certeza que deseja excluir a disciplina '{discipline_name}'?\n"
                                     "Isso também excluirá todas as aulas e materiais associados a ela.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            database.delete_discipline(discipline_id)
            QMessageBox.information(self, "Sucesso", "Disciplina excluída com sucesso!")
            self.load_disciplines()
            self.clear_form()

    def clear_form(self):
        self.discipline_name_input.clear()
        self.current_discipline_id = None
        self.save_button.setText("Salvar Disciplina")

    def update_style(self, stylesheet):
        self.setStyleSheet(stylesheet)
        
        for child_widget in self.findChildren(QWidget):
            child_widget.style().polish(child_widget)
