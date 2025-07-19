
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt, QDate
import database

class NoesisFullNotesWidget(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.current_note_id = None
        self.setObjectName("notesPage") # Nome do objeto para estilização

        self.initUI()
        self.load_notes()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Minhas Notas Completas", self)
        title_label.setObjectName("pageTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Formulário de notas
        form_frame = QFrame(self)
        form_frame.setObjectName("noteFormFrame") # Objeto para estilização
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.note_content_input = QTextEdit(self)
        self.note_content_input.setPlaceholderText("Escreva sua nota aqui...")
        self.note_content_input.setMinimumHeight(100)
        form_layout.addRow("Conteúdo da Nota:", self.note_content_input)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar Nota", self)
        self.save_button.setObjectName("primaryButton") # Objeto para estilização
        self.save_button.clicked.connect(self.save_note)
        button_layout.addWidget(self.save_button)

        self.clear_button = QPushButton("Limpar Formulário", self)
        self.clear_button.setObjectName("secondaryButton") # Objeto para estilização
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_button)

        form_layout.addRow("", button_layout)

        main_layout.addWidget(form_frame)

        # Tabela de notas
        notes_list_label = QLabel("Notas Cadastradas", self)
        notes_list_label.setObjectName("sectionTitle")
        main_layout.addWidget(notes_list_label)

        self.notes_table = QTableWidget(self)
        self.notes_table.setObjectName("notesTable") # Objeto para estilização
        self.notes_table.setColumnCount(3)
        self.notes_table.setHorizontalHeaderLabels(["ID", "Conteúdo", "Data de Criação"])
        self.notes_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.notes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.notes_table.setSelectionMode(QTableWidget.SingleSelection)
        self.notes_table.horizontalHeader().setStretchLastSection(True)
        self.notes_table.hideColumn(0) # Esconder o ID da nota
        self.notes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # Conteúdo preenche o espaço

        table_button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Editar Selecionado", self)
        self.edit_button.setObjectName("secondaryButton") # Objeto para estilização
        self.edit_button.clicked.connect(self.edit_selected_note)
        table_button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Excluir Selecionado", self)
        self.delete_button.setObjectName("dangerButton") # Objeto para estilização
        self.delete_button.clicked.connect(self.delete_selected_note)
        table_button_layout.addWidget(self.delete_button)

        main_layout.addWidget(self.notes_table)
        main_layout.addLayout(table_button_layout)

        self.setLayout(main_layout)

    def save_note(self):
        content = self.note_content_input.toPlainText().strip()

        if not content:
            QMessageBox.warning(self, "Campo Obrigatório", "Por favor, digite o conteúdo da nota.")
            return
        
        if self.user_id is None:
            QMessageBox.warning(self, "Erro", "Não é possível salvar notas. Usuário não autenticado.")
            return

        if self.current_note_id is None:
            if database.add_note(self.user_id, content):
                QMessageBox.information(self, "Sucesso", "Nota adicionada com sucesso!")
            else:
                QMessageBox.warning(self, "Erro", "Erro ao adicionar nota.")
        else:
            if database.update_note(self.current_note_id, content):
                QMessageBox.information(self, "Sucesso", "Nota atualizada com sucesso!")
                self.current_note_id = None
            else:
                QMessageBox.warning(self, "Erro", "Erro ao atualizar nota.")

        self.clear_form()
        self.load_notes()

    def load_notes(self):
        self.notes_table.setRowCount(0)
        if self.user_id is None:
            # Não carregar notas se não houver user_id
            return

        notes = database.get_notes(self.user_id)

        for row_num, note in enumerate(notes):
            self.notes_table.insertRow(row_num)
            self.notes_table.setItem(row_num, 0, QTableWidgetItem(str(note[0]))) # ID
            self.notes_table.setItem(row_num, 1, QTableWidgetItem(note[1])) # Conteúdo
            self.notes_table.setItem(row_num, 2, QTableWidgetItem(str(note[2]))) # Data de Criação
        
        self.notes_table.resizeColumnsToContents()

    def edit_selected_note(self):
        selected_rows = self.notes_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione uma nota para editar.")
            return

        row = selected_rows[0].row()
        self.current_note_id = int(self.notes_table.item(row, 0).text())
        note_content = self.notes_table.item(row, 1).text()
        
        self.note_content_input.setText(note_content)
        self.save_button.setText("Atualizar Nota")

    def delete_selected_note(self):
        selected_rows = self.notes_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione uma nota para excluir.")
            return

        row = selected_rows[0].row()
        note_id = int(self.notes_table.item(row, 0).text())
        note_content_preview = self.notes_table.item(row, 1).text()[:50] + "..." if len(self.notes_table.item(row, 1).text()) > 50 else self.notes_table.item(row, 1).text()

        reply = QMessageBox.question(self, "Confirmação de Exclusão",
                                     f"Tem certeza que deseja excluir a nota:\n'{note_content_preview}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            database.delete_note(note_id)
            QMessageBox.information(self, "Sucesso", "Nota excluída com sucesso!")
            self.load_notes()
            self.clear_form()

    def clear_form(self):
        self.note_content_input.clear()
        self.current_note_id = None
        self.save_button.setText("Salvar Nota")

    # Adicione este método à sua classe NoesisFullNotesWidget
    def update_style(self, stylesheet):
        self.setStyleSheet(stylesheet)
        for child_widget in self.findChildren(QWidget):
            child_widget.style().polish(child_widget)
