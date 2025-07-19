from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QFormLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QDate
import database

class NoesisMaterialsWidget(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.current_material_id = None
        self.initUI()
        self.load_materials()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Gerenciamento de Materiais de Estudo", self)
        title_label.setObjectName("pageTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        form_frame = QFrame(self)
        form_frame.setObjectName("materialFormFrame")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Título do Material (ex: Slides Aula 1)")
        form_layout.addRow("Título:", self.title_input)

        self.type_combo = QComboBox(self)
        self.type_combo.addItems(["Link", "PDF", "Documento", "Vídeo", "Outro"])
        form_layout.addRow("Tipo:", self.type_combo)

        self.link_file_input = QLineEdit(self)
        self.link_file_input.setPlaceholderText("URL ou Caminho do arquivo (ex: https://exemplo.com/material.pdf)")
        form_layout.addRow("Link/Caminho:", self.link_file_input)

        self.discipline_combo = QComboBox(self)
        self.discipline_combo.setPlaceholderText("Selecione uma disciplina")
        self.populate_disciplines_combo()
        self.discipline_combo.currentIndexChanged.connect(self.populate_lessons_combo)
        form_layout.addRow("Disciplina:", self.discipline_combo)

        self.lesson_combo = QComboBox(self)
        self.lesson_combo.setPlaceholderText("Selecione uma aula (opcional)")
        self.lesson_combo.addItem("Selecione uma aula (opcional)", -1)
        self.lesson_combo.hide()
        form_layout.addRow("Aula (Opcional):", self.lesson_combo)

        self.description_input = QTextEdit(self)
        self.description_input.setPlaceholderText("Breve descrição ou palavras-chave...")
        self.description_input.setFixedHeight(80)
        form_layout.addRow("Descrição:", self.description_input)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar Material", self)
        self.save_button.clicked.connect(self.save_material)
        button_layout.addWidget(self.save_button)

        self.clear_button = QPushButton("Limpar Formulário", self)
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_button)

        form_layout.addRow("", button_layout)

        main_layout.addWidget(form_frame)

        materials_list_label = QLabel("Meus Materiais Cadastrados", self)
        materials_list_label.setObjectName("sectionTitle")
        main_layout.addWidget(materials_list_label)

        self.materials_table = QTableWidget(self)
        self.materials_table.setColumnCount(7)
        self.materials_table.setHorizontalHeaderLabels([
            "ID", "Título", "Tipo", "Link/Caminho", "Disciplina", "Aula", "Descrição"
        ])
        self.materials_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.materials_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.materials_table.setSelectionMode(QTableWidget.SingleSelection)
        self.materials_table.horizontalHeader().setStretchLastSection(True)
        self.materials_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.materials_table.hideColumn(0)

        table_button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Editar Selecionado", self)
        self.edit_button.clicked.connect(self.edit_selected_material)
        table_button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Excluir Selecionado", self)
        self.delete_button.clicked.connect(self.delete_selected_material)
        table_button_layout.addWidget(self.delete_button)

        main_layout.addWidget(self.materials_table)
        main_layout.addLayout(table_button_layout)

        self.setLayout(main_layout)

    def populate_disciplines_combo(self):
        self.discipline_combo.clear()
        self.discipline_combo.addItem("Selecione uma disciplina", -1)
        disciplines = database.get_disciplines()
        if disciplines:
            for disc_id, disc_name in disciplines:
                self.discipline_combo.addItem(disc_name, disc_id)

    def populate_lessons_combo(self):
        discipline_id = self.discipline_combo.currentData()
        self.lesson_combo.clear()
        self.lesson_combo.addItem("Selecione uma aula (opcional)", -1)

        if discipline_id is not None and discipline_id != -1:
            lessons = database.get_lessons_by_discipline(discipline_id)
            if lessons:
                for lesson_id, lesson_name in lessons:
                    self.lesson_combo.addItem(lesson_name, lesson_id)
            self.lesson_combo.show()
        else:
            self.lesson_combo.hide()

    def save_material(self):
        title = self.title_input.text().strip()
        material_type = self.type_combo.currentText()
        link_file = self.link_file_input.text().strip()
        discipline_id = self.discipline_combo.currentData()
        lesson_id = self.lesson_combo.currentData() if self.lesson_combo.isVisible() and self.lesson_combo.currentData() != -1 else -1
        description = self.description_input.toPlainText().strip()

        if not title or not link_file or discipline_id == -1:
            QMessageBox.warning(self, "Campos Obrigatórios",
                                "Título, Link/Caminho e Disciplina são obrigatórios.")
            return

        if self.current_material_id is None:
            database.add_material(title, material_type, link_file, discipline_id, lesson_id, description)
            QMessageBox.information(self, "Sucesso", "Material adicionado com sucesso!")
        else:
            database.update_material(self.current_material_id, title, material_type, link_file,
                                     discipline_id, lesson_id, description)
            QMessageBox.information(self, "Sucesso", "Material atualizado com sucesso!")
            self.current_material_id = None

        self.clear_form()
        self.load_materials()

    def load_materials(self):
        self.materials_table.setRowCount(0)
        materials = database.get_materials()

        for row_num, material in enumerate(materials):
            self.materials_table.insertRow(row_num)

            material_id = material[0]
            title = material[1]
            material_type = material[2]
            link_file = material[3]
            discipline_id = material[4]
            lesson_id = material[5]
            description = material[6]

            discipline_name = database.get_discipline_name(discipline_id)
            lesson_name = database.get_lesson_name(lesson_id) if lesson_id is not None and lesson_id != -1 else ""

            self.materials_table.setItem(row_num, 0, QTableWidgetItem(str(material_id)))
            self.materials_table.setItem(row_num, 1, QTableWidgetItem(title))
            self.materials_table.setItem(row_num, 2, QTableWidgetItem(material_type))
            self.materials_table.setItem(row_num, 3, QTableWidgetItem(link_file))
            self.materials_table.setItem(row_num, 4, QTableWidgetItem(discipline_name))
            self.materials_table.setItem(row_num, 5, QTableWidgetItem(lesson_name))
            self.materials_table.setItem(row_num, 6, QTableWidgetItem(description))

        self.materials_table.resizeColumnsToContents()

    def edit_selected_material(self):
        selected_rows = self.materials_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione um material para editar.")
            return

        row = selected_rows[0].row()
        self.current_material_id = int(self.materials_table.item(row, 0).text())
        material_data = database.get_material_by_id(self.current_material_id)
        if material_data:
            self.title_input.setText(material_data[1])
            self.type_combo.setCurrentText(material_data[2])
            self.link_file_input.setText(material_data[3])

            idx_discipline = self.discipline_combo.findData(material_data[4])
            if idx_discipline != -1:
                self.discipline_combo.setCurrentIndex(idx_discipline)

                if material_data[5] is not None and material_data[5] != -1:
                    idx_lesson = self.lesson_combo.findData(material_data[5])
                    if idx_lesson != -1:
                        self.lesson_combo.setCurrentIndex(idx_lesson)
            else:
                self.discipline_combo.setCurrentIndex(0)
                self.lesson_combo.hide()

            self.description_input.setPlainText(material_data[6])
            self.save_button.setText("Atualizar Material")
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível carregar os dados do material.")

    def delete_selected_material(self):
        selected_rows = self.materials_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Seleção", "Por favor, selecione um material para excluir.")
            return

        row = selected_rows[0].row()
        material_id = int(self.materials_table.item(row, 0).text())
        material_title = self.materials_table.item(row, 1).text()

        reply = QMessageBox.question(self, "Confirmação de Exclusão",
                                     f"Tem certeza que deseja excluir o material '{material_title}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            database.delete_material(material_id)
            QMessageBox.information(self, "Sucesso", "Material excluído com sucesso!")
            self.load_materials()
            self.clear_form()

    def clear_form(self):
        self.title_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.link_file_input.clear()
        self.discipline_combo.setCurrentIndex(0)
        self.lesson_combo.clear()
        self.lesson_combo.addItem("Selecione uma aula (opcional)", -1)
        self.lesson_combo.hide()
        self.description_input.clear()
        self.current_material_id = None
        self.save_button.setText("Salvar Material")

    def update_style(self, stylesheet):
        self.setStyleSheet(stylesheet)
