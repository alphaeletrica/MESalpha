from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from gui.themes import Themes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtGui import QPainter

class GrainDashboard(QtWidgets.QWidget):
    def __init__(self, db_handler, theme):
        super().__init__()
        self.db_handler = db_handler
        self.theme = theme
        self.animations = []
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(25)

        self.create_filter_controls()

        self.charts_container = QtWidgets.QWidget()
        self.charts_container.setObjectName("chartsContainer")
        self.charts_layout = QtWidgets.QVBoxLayout(self.charts_container)
        self.charts_layout.setSpacing(10)
        self.charts_layout.setContentsMargins(0, 0, 0, 0)

        self.fig_soja = Figure(facecolor=self.theme['bg_card'])
        self.canvas_soja = FigureCanvas(self.fig_soja)
        self.canvas_soja.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.update_soja_chart()

        self.fig_farelo = Figure(facecolor=self.theme['bg_card'])
        self.canvas_farelo = FigureCanvas(self.fig_farelo)
        self.canvas_farelo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.update_farelo_chart()

        self.charts_layout.addWidget(self.canvas_soja)
        self.charts_layout.addWidget(self.canvas_farelo)

        self.layout.addWidget(self.charts_container)
        self.animate_charts_entrance()

    def create_filter_controls(self):
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.setSpacing(10)

        self.year_label = QtWidgets.QLabel("Filtrar por Ano:")
        filter_layout.addWidget(self.year_label)
        self.year_combo = QtWidgets.QComboBox()
        self.year_combo.addItems(["Todos"] + [str(year) for year in range(2020, 2026)])
        self.year_combo.currentTextChanged.connect(self.update_charts)
        filter_layout.addWidget(self.year_combo)

        self.month_label = QtWidgets.QLabel("Filtrar por Mês:")
        filter_layout.addWidget(self.month_label)
        self.month_combo = QtWidgets.QComboBox()
        self.month_combo.addItems(["Todos"] + [f"{i:02d}" for i in range(1, 13)])
        self.month_combo.currentTextChanged.connect(self.update_charts)
        filter_layout.addWidget(self.month_combo)

        filter_layout.addStretch()
        self.layout.addLayout(filter_layout)

    def get_connection(self):
        if hasattr(self.db_handler, "get_connection"):
            conn = self.db_handler.get_connection()
            if conn:
                return conn
            else:
                raise Exception("Falha ao obter conexão com o banco de dados.")
        else:
            raise AttributeError("O db_handler não possui o método 'get_connection'.")

    def fetch_soja_mensal(self, year_filter=None, month_filter=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT strftime('%Y-%m', Data) as Mes, SUM(ProducaoDiaria) as Total_Mensal
                    FROM ProducaoSoja
                    WHERE 1=1
                """
                params = []
                if year_filter and year_filter != "Todos":
                    query += " AND strftime('%Y', Data) = ?"
                    params.append(year_filter)
                if month_filter and month_filter != "Todos":
                    query += " AND strftime('%m', Data) = ?"
                    params.append(month_filter)
                query += " GROUP BY Mes ORDER BY Mes"
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return rows
        except Exception as e:
            print(f"Erro ao buscar produção mensal de soja: {e}")
            return []

    def fetch_farelo_umidade_mensal(self, year_filter=None, month_filter=None):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT strftime('%Y-%m', Data) as Mes, AVG(UmidadeFarelo) as Umidade_Media
                    FROM FareloSojaTostado
                    WHERE 1=1
                """
                params = []
                if year_filter and year_filter != "Todos":
                    query += " AND strftime('%Y', Data) = ?"
                    params.append(year_filter)
                if month_filter and month_filter != "Todos":
                    query += " AND strftime('%m', Data) = ?"
                    params.append(month_filter)
                query += " GROUP BY Mes ORDER BY Mes"
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return rows
        except Exception as e:
            print(f"Erro ao buscar umidade média do farelo por mês: {e}")
            return []

    def update_charts(self):
        year_filter = self.year_combo.currentText()
        month_filter = self.month_combo.currentText()
        self.update_soja_chart(year_filter, month_filter)
        self.update_farelo_chart(year_filter, month_filter)
        self.animate_charts_entrance()

    def update_soja_chart(self, year_filter=None, month_filter=None):
        self.fig_soja.clear()
        ax = self.fig_soja.add_subplot(111)
        ax.set_title("Produção Mensal de Soja", fontsize=14, pad=20, color=self.theme['text_primary'])
        ax.set_xlabel("Mês", fontsize=10, color=self.theme['text_secondary'], labelpad=15)  
        ax.set_ylabel("Produção (ton)", fontsize=10, color=self.theme['text_secondary'], labelpad=15)  

        dados = self.fetch_soja_mensal(year_filter, month_filter)
        meses = [datetime.strptime(d[0], "%Y-%m") for d in dados]
        producao = [d[1] for d in dados]

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        self.fig_soja.autofmt_xdate()

        line, = ax.plot(meses, producao, marker='o', linestyle='-', color='red',
                        linewidth=2, markersize=6)

        ax.grid(True, linestyle='--', alpha=0.7, color=self.theme['border'])
        ax.set_facecolor(self.theme['bg_secondary'])
        ax.tick_params(axis='both', colors=self.theme['text_secondary'], labelsize=8)

        for spine in ax.spines.values():
            spine.set_linewidth(0.5)
            spine.set_color(self.theme['border'])
        ax.set_xlim(ax.get_xlim())
        ax.set_ylim(ax.get_ylim())
        y_min, y_max = ax.get_ylim()
        y_padding = (y_max - y_min) * 0.1
        ax.set_ylim(y_min - y_padding, y_max + y_padding)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_position(('outward', 10))
        ax.spines['bottom'].set_position(('outward', 10))

        # Criação da anotação com zorder alto
        self.annotation_soja = ax.annotate("", 
                                           xy=(0, 0),
                                           xytext=(0, 0),
                                           textcoords="offset pixels",
                                           bbox=dict(boxstyle="round,pad=0.5", fc=self.theme['bg_card'], 
                                                     alpha=0.9, ec=self.theme['border']),
                                           color=self.theme['text_primary'],
                                           visible=False,
                                           zorder=10)  # Zorder alto para ficar acima do título
        
        def hover(event):
            if event.inaxes == ax:
                cont, ind = line.contains(event)
                if cont:
                    idx = ind["ind"][0]
                    if 0 <= idx < len(meses):
                        x, y = meses[idx], producao[idx]
                        self.annotation_soja.xy = (x, y)
                        self.annotation_soja.set_text(f"Mês: {meses[idx]:%Y-%m}\nProdução: {producao[idx]:.2f} ton")
                        
                        xlim = ax.get_xlim()
                        ylim = ax.get_ylim()
                        x_norm = (mdates.date2num(x) - xlim[0]) / (xlim[1] - xlim[0])
                        y_norm = (y - ylim[0]) / (ylim[1] - ylim[0])
                        
                        # Ajustar posição da anotação
                        if x_norm > 0.8:  # Borda direita
                            self.annotation_soja.set_ha('right')
                            self.annotation_soja.set_va('center')
                            self.annotation_soja.xytext = (-10, 0)
                        elif x_norm < 0.2:  # Borda esquerda
                            self.annotation_soja.set_ha('left')
                            self.annotation_soja.set_va('center')
                            self.annotation_soja.xytext = (10, 0)
                        else:
                            if y_norm > 0.9:  # Próximo ao topo (ajustado para evitar título)
                                self.annotation_soja.set_ha('center')
                                self.annotation_soja.set_va('bottom')
                                self.annotation_soja.xytext = (0, -20)  # Aumentado para evitar título
                            elif y_norm < 0.2:  # Próximo à base
                                self.annotation_soja.set_ha('center')
                                self.annotation_soja.set_va('top')
                                self.annotation_soja.xytext = (0, 10)
                            else:  # Posição central
                                self.annotation_soja.set_ha('center')
                                self.annotation_soja.set_va('bottom')
                                self.annotation_soja.xytext = (0, -15)
                        
                        self.annotation_soja.set_visible(True)
                        self.fig_soja.canvas.draw_idle()
                else:
                    if self.annotation_soja.get_visible():
                        self.annotation_soja.set_visible(False)
                        self.fig_soja.canvas.draw_idle()
        
        self.fig_soja.canvas.mpl_connect("motion_notify_event", hover)

        self.fig_soja.tight_layout()
        self.adjust_figure_size(self.fig_soja, self.canvas_soja)
        self.canvas_soja.draw()

    def update_farelo_chart(self, year_filter=None, month_filter=None):
        self.fig_farelo.clear()
        ax = self.fig_farelo.add_subplot(111)
        ax.set_title("Umidade Média do Farelo por Mês", fontsize=14, pad=20, color=self.theme['text_primary'])  # Increased padding
        ax.set_xlabel("Mês", fontsize=10, color=self.theme['text_secondary'], labelpad=15)  # Increased label padding
        ax.set_ylabel("Umidade (%)", fontsize=10, color=self.theme['text_secondary'], labelpad=15)  # Increased label padding

        dados = self.fetch_farelo_umidade_mensal(year_filter, month_filter)
        meses = [datetime.strptime(d[0], "%Y-%m") for d in dados]
        umidade = [d[1] for d in dados]

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        self.fig_farelo.autofmt_xdate()

        # Plotar a linha principal em vermelho
        line, = ax.plot(meses, umidade, marker='o', linestyle='-', color='red',
                        linewidth=2, markersize=6)

        ax.grid(True, linestyle='--', alpha=0.7, color=self.theme['border'])
        ax.set_facecolor(self.theme['bg_secondary'])
        ax.tick_params(axis='both', colors=self.theme['text_secondary'], labelsize=8)

        for spine in ax.spines.values():
            spine.set_linewidth(0.5)
            spine.set_color(self.theme['border'])
        ax.set_xlim(ax.get_xlim())
        ax.set_ylim(ax.get_ylim())
        y_min, y_max = ax.get_ylim()
        y_padding = (y_max - y_min) * 0.1  # 10% padding
        ax.set_ylim(y_min - y_padding, y_max + y_padding)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_position(('outward', 10))  # Increased spacing
        ax.spines['bottom'].set_position(('outward', 10))

        self.annotation_farelo = ax.annotate("", 
                                             xy=(0, 0),
                                             xytext=(0, 0),
                                             textcoords="offset pixels",
                                             bbox=dict(boxstyle="round,pad=0.5", fc=self.theme['bg_card'], 
                                                       alpha=0.9, ec=self.theme['border']),
                                             color=self.theme['text_primary'],
                                             visible=False,
                                             zorder=10)
        
        def hover(event):
            if event.inaxes == ax:
                cont, ind = line.contains(event)
                if cont:
                    idx = ind["ind"][0]
                    if 0 <= idx < len(meses):
                        x, y = meses[idx], umidade[idx]
                        self.annotation_farelo.xy = (x, y)
                        self.annotation_farelo.set_text(f"Mês: {meses[idx]:%Y-%m}\nUmidade: {umidade[idx]:.2f}%")
                        
                        xlim = ax.get_xlim()
                        ylim = ax.get_ylim()
                        x_norm = (mdates.date2num(x) - xlim[0]) / (xlim[1] - xlim[0])
                        y_norm = (y - ylim[0]) / (ylim[1] - ylim[0])
                        
                        if x_norm > 0.8:
                            self.annotation_farelo.set_ha('right')
                            self.annotation_farelo.set_va('center')
                            self.annotation_farelo.xytext = (-10, 0)
                        elif x_norm < 0.2:
                            self.annotation_farelo.set_ha('left')
                            self.annotation_farelo.set_va('center')
                            self.annotation_farelo.xytext = (10, 0)
                        else:
                            if y_norm > 0.9:
                                self.annotation_farelo.set_ha('center')
                                self.annotation_farelo.set_va('bottom')
                                self.annotation_farelo.xytext = (0, -20)
                            elif y_norm < 0.2:
                                self.annotation_farelo.set_ha('center')
                                self.annotation_farelo.set_va('top')
                                self.annotation_farelo.xytext = (0, 10)
                            else:
                                self.annotation_farelo.set_ha('center')
                                self.annotation_farelo.set_va('bottom')
                                self.annotation_farelo.xytext = (0, -15)
                        
                        self.annotation_farelo.set_visible(True)
                        self.fig_farelo.canvas.draw_idle()
                else:
                    if self.annotation_farelo.get_visible():
                        self.annotation_farelo.set_visible(False)
                        self.fig_farelo.canvas.draw_idle()
        
        self.fig_farelo.canvas.mpl_connect("motion_notify_event", hover)

        self.fig_farelo.tight_layout()
        self.adjust_figure_size(self.fig_farelo, self.canvas_farelo)
        self.canvas_farelo.draw()

    def adjust_figure_size(self, fig, canvas):
        width = canvas.width() / 100
        height = canvas.height() / 100
        fig.set_size_inches(max(width, 5), max(height, 2))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_figure_size(self.fig_soja, self.canvas_soja)
        self.adjust_figure_size(self.fig_farelo, self.canvas_farelo)
        self.canvas_soja.draw()
        self.canvas_farelo.draw()

    def apply_theme(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        shadow.setColor(QColor(100, 100, 100))
        self.charts_container.setGraphicsEffect(shadow)
        self.canvas_soja.setStyleSheet(f"border: 1px solid {self.theme['border']}; border-radius: 10px;")
        self.canvas_farelo.setStyleSheet(f"border: 1px solid {self.theme['border']}; border-radius: 10px;")

        self.year_label.setStyleSheet(f"color: {self.theme['text_primary']};")
        self.month_label.setStyleSheet(f"color: {self.theme['text_primary']};")
        combo_style = f"""
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
            QComboBox QAbstractItemView {{
                background-color: {self.theme['bg_card']};
                color: {self.theme['text_primary']};
                selection-background-color: {self.theme['hover']};
            }}
        """
        self.year_combo.setStyleSheet(combo_style)
        self.month_combo.setStyleSheet(combo_style)

        self.fig_soja.set_facecolor(self.theme['bg_card'])
        self.fig_farelo.set_facecolor(self.theme['bg_card'])
        for ax in self.fig_soja.get_axes():
            ax.set_facecolor(self.theme['bg_secondary'])
        for ax in self.fig_farelo.get_axes():
            ax.set_facecolor(self.theme['bg_secondary'])

        self.canvas_soja.draw()
        self.canvas_farelo.draw()

    def animate_charts_entrance(self):
        for animation in self.animations:
            animation.stop()
        self.animations.clear()

        for widget in [self.canvas_soja, self.canvas_farelo]:
            widget.setStyleSheet(f"opacity: 0; border: 1px solid {self.theme['border']}; border-radius: 10px;")
            animation = QPropertyAnimation(widget, b"windowOpacity", self)
            animation.setDuration(1000)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.InOutQuad)
            animation.start()
            self.animations.append(animation)

    def update_theme(self, theme):
        self.theme = theme
        self.update_charts()
        self.apply_theme()

    def export_to_pdf(self, file_path):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)

        painter = QPainter(printer)
        self.render(painter)
        painter.end()