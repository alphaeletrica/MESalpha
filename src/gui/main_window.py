from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QPushButton, QLabel, QStackedWidget, QFrame,
                              QSizePolicy)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QIcon, QFont
from gui.pages.home_page import HomePage
from gui.pages.tasks_page import TasksPage
from gui.pages.about_page import AboutPage
from gui.pages.dashboards_page import DashboardWindow
from gui.themes import Themes, get_stylesheet
import os

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_theme = 'LIGHT'
        self.sidebar_expanded = True
        self.icons_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icons"))
        self.button_width_expanded = 200
        self.button_width_collapsed = 50
        self.button_height = 40
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SISTEMA MES | Alpha Automação')
        self.setGeometry(100, 100, 1280, 720)
        
        icon_path = os.path.join(self.icons_path, "icon_alpha.ico") 
        self.setWindowIcon(QIcon(icon_path))
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.header = self.create_header()
        self.sidebar = self.create_sidebar()
        self.stack = QStackedWidget()
        
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.create_content_container())
        
        self.apply_theme()
        self.load_page(HomePage)

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(80)
        header.setObjectName("header")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.addWidget(self.create_logo_container())
        header_layout.addWidget(self.create_title_container(), 1)
        
        return header

    def create_logo_container(self):
        logo_container = QWidget()
        logo_container.setFixedWidth(220)
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)

        self.logo = QLabel()
        self.update_logo()
        
        logo_layout.addWidget(self.logo)
        return logo_container

    def update_logo(self):
        logo_filename = "alpha_logo_d.png" if self.current_theme == 'DARK' else "alpha_logo_l.png"
        logo_path = os.path.join(self.icons_path, logo_filename)
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            self.logo.setPixmap(pixmap.scaled(180, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            print(f"Erro: Não foi possível carregar a logo em {logo_path}")
            self.logo.setText("Logo Not Found")

    def create_title_container(self):
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel('Sistema MES | Alpha Automação')
        title_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(title_label)
        return title_container

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setMinimumWidth(220)
        sidebar.setMaximumWidth(220)
        sidebar.setObjectName("sidebar")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(4)
        sidebar_layout.setContentsMargins(8, 8, 8, 8)
        
        self.toggle_button = self.create_toggle_button()
        self.nav_buttons = self.createNavButtons()
        
        sidebar_layout.addWidget(self.toggle_button, alignment=Qt.AlignCenter | Qt.AlignTop)
        for btn, text in self.nav_buttons:
            sidebar_layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        self.theme_btn = self.create_theme_button()
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.theme_btn, alignment=Qt.AlignCenter)
        
        return sidebar

    def create_toggle_button(self):
        toggle_button = QPushButton()
        icon_path = os.path.join(self.icons_path, "menu.png")
        toggle_button.setIcon(QIcon(icon_path))
        toggle_button.setIconSize(QSize(24, 24))
        toggle_button.setFixedSize(self.button_width_expanded, self.button_height)
        toggle_button.setObjectName("toggleButton")
        toggle_button.clicked.connect(self.toggle_sidebar)
        return toggle_button

    def createNavButtons(self):
        navData = [
            ('Home', 'home.png', HomePage),
            ('Tarefas', 'task.png', TasksPage),
            ('Dashboards', 'dashboard.png', DashboardWindow),
            ('Sobre', 'about.png', AboutPage)
        ]
        
        buttons = []
        for text, iconName, pageClass in navData:
            btn = QPushButton(text)
            iconPath = os.path.join(self.icons_path, iconName)
            icon = QIcon(iconPath)
            if icon.availableSizes(): 
                btn.setIcon(icon)
                btn.setIconSize(QSize(24, 24))
            btn.setFont(QFont('Segoe UI', 11))
            btn.setMinimumWidth(self.button_width_expanded)
            btn.setMaximumWidth(self.button_width_expanded)
            btn.setFixedHeight(self.button_height)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setObjectName("navButton")
            btn.clicked.connect(lambda checked, cls=pageClass: self.load_page(cls)) 
            buttons.append((btn, text))
        
        return buttons

    def create_theme_button(self):
        theme_btn = QPushButton()
        icon_path = os.path.join(self.icons_path, "theme.png")
        theme_btn.setIcon(QIcon(icon_path))
        theme_btn.setIconSize(QSize(24, 24))
        theme_btn.setFixedSize(50, 50)
        theme_btn.setObjectName("themeButton")
        theme_btn.clicked.connect(self.toggle_theme)
        return theme_btn
    
    def create_content_container(self):
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.stack)
        return content_container

    def toggle_sidebar(self):
        new_width = 50 if self.sidebar_expanded else 230
        
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.sidebar.width())
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

        self.toggle_button.setFixedSize(
            self.button_width_collapsed if self.sidebar_expanded else self.button_width_expanded,
            self.button_height
        )

        for btn, text in self.nav_buttons:
            btn.setText("" if self.sidebar_expanded else text)
            btn.setMinimumWidth(self.button_width_collapsed if self.sidebar_expanded else self.button_width_expanded)
            btn.setMaximumWidth(self.button_width_collapsed if self.sidebar_expanded else self.button_width_expanded)
            btn.setToolTip(text if self.sidebar_expanded else "")

        self.sidebar_expanded = not self.sidebar_expanded

    def apply_theme(self):
        self.setStyleSheet(get_stylesheet(getattr(Themes, self.current_theme)))
        self.update_logo() 
        
        for i in range(self.stack.count()):
            page = self.stack.widget(i)
            if hasattr(page, 'update_theme'):
                page.update_theme(self.current_theme)

    def load_page(self, page_class):
        try:
            for i in range(self.stack.count()):
                if isinstance(self.stack.widget(i), page_class):
                    self.stack.setCurrentIndex(i)
                    current_page = self.stack.currentWidget()
                    if hasattr(current_page, 'update_theme'):
                        current_page.update_theme(getattr(Themes, self.current_theme)) 
                    return
            
            new_page = page_class(self.db, getattr(Themes, self.current_theme))
            self.stack.addWidget(new_page)
            self.stack.setCurrentWidget(new_page)
            
            if hasattr(new_page, 'update_theme'):
                new_page.update_theme(self.current_theme)
        except Exception as e:
            print(f"Erro ao carregar a página {page_class.__name__}: {str(e)}")

    def toggle_theme(self):
        self.current_theme = 'DARK' if self.current_theme == 'LIGHT' else 'LIGHT'
        self.apply_theme()