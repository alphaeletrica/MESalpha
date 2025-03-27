# home_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from gui.themes import Themes

class HomePage(QWidget):
    def __init__(self, db, theme=Themes.LIGHT):
        super().__init__()
        self.db = db
        self.theme = theme
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        welcome_label = QLabel("Bem-vindo!")
        welcome_label.setFont(QFont('Segoe UI', 48, QFont.Bold))
        welcome_label.setStyleSheet("background-color: transparent;")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        slogan_label = QLabel("O sistema perfeito para o monitoramento do seu negócio!")
        slogan_label.setFont(QFont('Segoe UI', 18))
        slogan_label.setStyleSheet("background-color: transparent;")
        slogan_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(slogan_label)

        # Aplicar o tema inicial como string
        initial_theme_name = 'LIGHT' if self.theme == Themes.LIGHT else 'DARK'
        self.update_theme(initial_theme_name)

    def update_theme(self, theme_name):
        self.theme = getattr(Themes, theme_name)
        self.setStyleSheet(f"""
            background-color: {self.theme['bg_primary']};
            color: {self.theme['text_primary']};
        """)