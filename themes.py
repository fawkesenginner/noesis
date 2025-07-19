import os
from PyQt5.QtWidgets import QApplication

class ThemeManager:
    def __init__(self, app: QApplication):
        self.app = app
        self.current_theme = ""
        self.themes_path = os.path.join(os.path.dirname(__file__), "themes")

    def apply_theme(self, theme_name):
        qss_file = ""
        if theme_name == "Claro":
            qss_file = os.path.join(self.themes_path, "light.qss")
        elif theme_name == "Escuro":
            qss_file = os.path.join(self.themes_path, "dark.qss")
        elif theme_name == "Ciano (Padrão)":
            qss_file = os.path.join(self.themes_path, "cyan.qss")
        
        if os.path.exists(qss_file):
            with open(qss_file, "r") as f:
                self.app.setStyleSheet(f.read())
            self.current_theme = theme_name
        else:
            print(f"Erro: Arquivo de tema não encontrado: {qss_file}")
            self.app.setStyleSheet("") # Limpa o estilo se o tema não for encontrado
        
    def get_available_themes(self):
        themes = []
        if os.path.exists(self.themes_path):
            for filename in os.listdir(self.themes_path):
                if filename.endswith(".qss"):
                    name = filename.replace(".qss", "").replace("_", " ").title()
                    if name.lower() == "light":
                        themes.append("Claro")
                    elif name.lower() == "dark":
                        themes.append("Escuro")
                    elif name.lower() == "cyan":
                        themes.append("Ciano (Padrão)")
                    else:
                        themes.append(name)
        themes.sort()
        return themes

    def get_current_theme(self):
        return self.current_theme
