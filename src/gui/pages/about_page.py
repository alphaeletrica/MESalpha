from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from gui.themes import Themes

class AboutPage(QWidget):
    def __init__(self, db, theme=Themes.LIGHT):
        super().__init__()
        self.db = db
        self.theme = theme
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        about_text = """
        <h1>SISTEMA MES | Alpha - Automação de Sistemas Elétricos</h1>
        <p>Versão 1.0.0</p>
        <p>Desenvolvido por Alpha Automação de Sistemas Elétricos</p>
        <p>© 2025 Todos os direitos reservados</p>
        """
        
        label = QLabel(about_text)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        self.setLayout(layout)
        initial_theme_name = 'LIGHT' if self.theme == Themes.LIGHT else 'DARK'
        self.update_theme(initial_theme_name)

    def update_theme(self, theme_name):
        self.theme = getattr(Themes, theme_name)
        self.setStyleSheet(f"""
            background-color: {self.theme['bg_primary']};
            color: {self.theme['text_primary']};
        """)