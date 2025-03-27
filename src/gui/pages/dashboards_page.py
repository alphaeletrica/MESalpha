from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QStackedWidget, QPushButton, QLabel, QComboBox, QSizePolicy, QFileDialog
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QPixmap
from gui.themes import Themes, get_stylesheet
from .dashboards.grain_dashboard import GrainDashboard
from .dashboards.maintenance_dashboard import MaintenanceDashboard

class DashboardWindow(QWidget):
    def __init__(self, db_handler, theme=Themes.LIGHT):
        super().__init__()
        self.db_handler = db_handler
        self.theme = theme
        self.animations = []
        self.grain_dashboard = None
        self.maintenance_dashboard = None
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        main_layout.addWidget(scroll_area)

        container = QWidget()
        container.setObjectName("dashboardContainer")
        scroll_area.setWidget(container)

        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(25)

        self.create_dashboard_selection_buttons()

        self.dashboard_stack = QStackedWidget()
        self.dashboard_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.grain_dashboard = GrainDashboard(self.db_handler, self.theme)
        self.grain_dashboard.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dashboard_stack.addWidget(self.grain_dashboard)

        self.maintenance_dashboard = MaintenanceDashboard(self.db_handler, self.theme)
        self.maintenance_dashboard.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dashboard_stack.addWidget(self.maintenance_dashboard)

        self.layout.addWidget(self.dashboard_stack)
        self.layout.addStretch()

    def create_export_button(self):
        self.export_button = QLabel()
        self.export_button.setFixedSize(30, 30)
        self.export_button.setPixmap(QPixmap("icons/download.png").scaled(30, 30))
        self.export_button.mousePressEvent = self.export_current_page
        self.selection_layout.addWidget(self.export_button)

    def export_current_page(self, event):
        current_widget = self.dashboard_stack.currentWidget()
        if current_widget:
            file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Página", "", "PDF Files (*.pdf);;All Files (*)")
            if file_path:
                current_widget.export_to_pdf(file_path)

    def create_dashboard_selection_buttons(self):
        self.selection_layout = QHBoxLayout()
        self.selection_layout.setSpacing(20)

        self.grain_button = QPushButton("Grão")
        self.grain_button.setFixedSize(200, 50)
        self.grain_button.clicked.connect(lambda: self.dashboard_stack.setCurrentIndex(0))
        self.selection_layout.addWidget(self.grain_button)

        self.maintenance_button = QPushButton("Manutenção")
        self.maintenance_button.setFixedSize(200, 50)
        self.maintenance_button.clicked.connect(lambda: self.dashboard_stack.setCurrentIndex(1))
        self.selection_layout.addWidget(self.maintenance_button)

        self.selection_layout.addStretch()
        self.create_export_button()
        self.layout.addLayout(self.selection_layout)

    def apply_theme(self):
        stylesheet = get_stylesheet(self.theme)
        self.setStyleSheet(stylesheet)

        for label in self.findChildren(QLabel):
            label.setStyleSheet(f"color: {self.theme['text_primary']};")
        for combo in self.findChildren(QComboBox):
            combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {self.theme['bg_card']};
                    color: {self.theme['text_primary']};
                    border: 1px solid {self.theme['border']};
                    border-radius: 5px;
                    padding: 5px;
                }}
                QComboBox::drop-down {{
                    border-left: 1px solid {self.theme['border']};
                }}
                QComboBox:hover {{
                    background-color: {self.theme['hover']};
                }}
            """)
        for button in self.findChildren(QPushButton):
            if button in [self.grain_button, self.maintenance_button, self.export_button]:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.theme['red']};
                        color: {self.theme['button_text']};
                        border: none;
                        border-radius: 10px;
                        padding: 8px;
                        font-size: 18px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.theme['red_hover']};
                    }}
                    QPushButton:pressed {{
                        background-color: {self.theme['active']};
                    }}
                """)
            else:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.theme['accent']};
                        color: {self.theme['button_text']};
                        border: none;
                        border-radius: 5px;
                        padding: 8px;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.theme['hover']};
                    }}
                    QPushButton:pressed {{
                        background-color: {self.theme['active']};
                    }}
                """)
        self.dashboard_stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {self.theme['bg_card']};
                border-radius: {self.theme['card_radius']};
            }}
        """)
        for widget in [self.grain_dashboard, self.maintenance_dashboard]:
            if widget:
                widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: {self.theme['bg_card']};
                        border-radius: {self.theme['card_radius']};
                    }}
                """)

    def update_theme(self, theme_name):
        self.theme = getattr(Themes, theme_name)
        self.apply_theme()
        if self.grain_dashboard:
            self.grain_dashboard.update_theme(self.theme)
        if self.maintenance_dashboard:
            self.maintenance_dashboard.update_theme(self.theme)
        self.style().unpolish(self)
        self.style().polish(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.dashboard_stack.setMaximumWidth(self.width() - 60)
        current_widget = self.dashboard_stack.currentWidget()
        if current_widget:
            current_widget.updateGeometry()