from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtPrintSupport import QPrinter
from gui.themes import Themes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

class MaintenanceDashboard(QtWidgets.QWidget):
    def __init__(self, db_handler, theme):
        super().__init__()
        self.db_handler = db_handler
        self.theme = theme
        self.df = self.fetch_data()
        self.init_ui()
        self.apply_theme()

    def fetch_data(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT DataInicial, DataFinal, TAG, Tipo, Falha, Descrição, Horímetro, Operador
                    FROM TabelaTeste
                    ORDER BY TAG, DataInicial
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=['DataInicial', 'DataFinal', 'TAG', 'Tipo', 'Falha', 'Descrição', 'Horímetro', 'Operador'])
                df['DataInicial'] = pd.to_datetime(df['DataInicial'], errors='coerce')
                df['DataFinal'] = pd.to_datetime(df['DataFinal'], errors='coerce')
                df['Descrição'] = df['Descrição'].fillna('').replace('-', '')
                df['Falha'] = df['Falha'].fillna('Sem Falha').replace('', 'Sem Falha')
                
                def convert_horimetro_to_hours(horimetro):
                    if pd.isna(horimetro) or not isinstance(horimetro, str):
                        return 0.0
                    try:
                        h, m, s = map(int, horimetro.split(':'))
                        return h + m / 60 + s / 3600
                    except (ValueError, AttributeError):
                        return 0.0

                df['DuracaoHoras'] = df['Horímetro'].apply(convert_horimetro_to_hours)
                df['Horímetro'] = df['Horímetro'].fillna('00:00:00')
                df = df.rename(columns={
                    'DataInicial': 'Início da Manutenção', 'DataFinal': 'Fim da Manutenção', 'TAG': 'TAG',
                    'Tipo': 'Tipo', 'Falha': 'Falha', 'Descrição': 'Descrição', 'Horímetro': 'Horímetro',
                    'Operador': 'Operador', 'DuracaoHoras': 'Duração da Manutenção'
                })
                return df
        except Exception as e:
            print(f"Erro ao buscar dados da TabelaTeste: {e}")
            return pd.DataFrame()

    def get_connection(self):
        if hasattr(self.db_handler, "get_connection"):
            conn = self.db_handler.get_connection()
            if conn:
                return conn
            else:
                raise Exception("Falha ao obter conexão com o banco de dados.")
        else:
            raise AttributeError("O db_handler não possui o método 'get_connection'.")

    def format_duration(self, hours):
        if pd.isna(hours) or hours < 0:
            return "00:00"
        total_seconds = int(hours * 3600)
        hours_part = total_seconds // 3600
        minutes_part = (total_seconds % 3600) // 60
        return f"{hours_part:02d}:{minutes_part:02d}"

    def parse_duration(self, duration_str):
        if isinstance(duration_str, str) and ':' in duration_str:
            hours, minutes = map(int, duration_str.split(':'))
            return hours + minutes / 60
        return 0

    def calculate_kpis(self, df):
        if df.empty:
            return {"total_equipamentos": 0, "equipamentos_em_manutencao": 0, "quantidade_falhas": 0}
        total_equipamentos = df['TAG'].nunique()
        equipamentos_em_manutencao = df[df['Fim da Manutenção'].isna()]['TAG'].nunique()
        quantidade_falhas = df[df['Falha'] != 'Sem Falha'].shape[0]
        return {
            "total_equipamentos": total_equipamentos,
            "equipamentos_em_manutencao": equipamentos_em_manutencao,
            "quantidade_falhas": quantidade_falhas
        }

    def init_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(20)

        kpis = self.calculate_kpis(self.df)
        kpi_layout = QtWidgets.QHBoxLayout()
        kpi_layout.setSpacing(10)

        self.total_equip_label = QtWidgets.QLabel(f"Total de Equipamentos\n{kpis['total_equipamentos']}")
        self.total_equip_label.setAlignment(QtCore.Qt.AlignCenter)
        self.total_equip_label.setFixedSize(230, 80)
        kpi_layout.addWidget(self.total_equip_label)

        self.maint_equip_label = QtWidgets.QLabel(f"Equipamentos em Manutenção\n{kpis['equipamentos_em_manutencao']}")
        self.maint_equip_label.setAlignment(QtCore.Qt.AlignCenter)
        self.maint_equip_label.setFixedSize(230, 80)
        kpi_layout.addWidget(self.maint_equip_label)

        self.faults_label = QtWidgets.QLabel(f"Quantidade de Falhas\n{kpis['quantidade_falhas']}")
        self.faults_label.setAlignment(QtCore.Qt.AlignCenter)
        self.faults_label.setFixedSize(230, 80)
        kpi_layout.addWidget(self.faults_label)

        kpi_layout.addStretch()
        self.layout.addLayout(kpi_layout)

        self.charts_container = QtWidgets.QWidget()
        self.charts_container.setObjectName("chartsContainer")
        self.charts_layout = QtWidgets.QVBoxLayout(self.charts_container)
        self.charts_layout.setSpacing(10)
        self.charts_layout.setContentsMargins(0, 0, 0, 0)

        self.fig_line = Figure(figsize=(12, 3), facecolor=self.theme['bg_card'])
        self.canvas_line = FigureCanvas(self.fig_line)
        self.canvas_line.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.canvas_line.setMinimumHeight(150)
        self.update_line_chart()
        self.charts_layout.addWidget(self.canvas_line)

        charts_row = QtWidgets.QHBoxLayout()
        charts_row.setSpacing(10)

        self.fig_bar = Figure(figsize=(5, 3), facecolor=self.theme['bg_card'])
        self.canvas_bar = FigureCanvas(self.fig_bar)
        self.canvas_bar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.canvas_bar.setMinimumHeight(150)
        self.update_bar_chart()
        charts_row.addWidget(self.canvas_bar)

        self.fig_pie = Figure(figsize=(5, 3), facecolor=self.theme['bg_card'])
        self.canvas_pie = FigureCanvas(self.fig_pie)
        self.canvas_pie.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.canvas_pie.setMinimumHeight(150)
        self.update_pie_chart()
        charts_row.addWidget(self.canvas_pie)

        self.charts_layout.addLayout(charts_row)
        self.layout.addWidget(self.charts_container)
        self.layout.addStretch()

    def update_line_chart(self):
        self.fig_line.clear()
        ax = self.fig_line.add_subplot(111)
        ax.set_title("Duração da Manutenção por Equipamento", fontsize=14, pad=10, color=self.theme['text_primary'])
        ax.set_xlabel("TAG", fontsize=10, color=self.theme['text_secondary'])
        ax.set_ylabel("Duração (h)", fontsize=10, color=self.theme['text_secondary'])

        if not self.df.empty:
            df = self.df.copy()
            df['Duração (horas)'] = df['Duração da Manutenção']
            pivot_df = df.pivot_table(index='TAG', columns=df.groupby('TAG').cumcount(), values='Duração (horas)', fill_value=0)
            bars = []
            bottom = None

            num_colors = len(pivot_df.columns)
            colors = [(1, 0, 0, 1 - i / num_colors) for i in range(num_colors)]

            for i, col in enumerate(pivot_df.columns):
                bar = ax.bar(pivot_df.index, pivot_df[col], bottom=bottom, color=colors[i], edgecolor='black', linewidth=0.5)
                bars.append(bar)
                bottom = pivot_df[col] if bottom is None else bottom + pivot_df[col]

            # Adicionar hover
            self.annotation_line = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                                               bbox=dict(boxstyle="round,pad=0.5", fc=self.theme['bg_card'], alpha=0.9, ec=self.theme['border']),
                                               color=self.theme['text_primary'], visible=False, zorder=10)

            def hover(event):
                if event.inaxes == ax:
                    for i, bar_group in enumerate(bars):
                        for j, bar in enumerate(bar_group):
                            cont = bar.contains(event)[0]
                            if cont:
                                tag = pivot_df.index[j]
                                if i == 0:
                                    y = bar.get_height()
                                else:
                                    y = bar.get_height() + sum(pivot_df.iloc[j, :i])
                                duration = bar.get_height()
                                self.annotation_line.set_text(f"TAG: {tag}\nDuração: {self.format_duration(duration)}")
                                self.annotation_line.xy = (bar.get_x() + bar.get_width() / 2, y)
                                self.annotation_line.set_visible(True)
                                self.fig_line.canvas.draw_idle()
                                return
                    if self.annotation_line.get_visible():
                        self.annotation_line.set_visible(False)
                        self.fig_line.canvas.draw_idle()

            self.fig_line.canvas.mpl_connect("motion_notify_event", hover)

        ax.grid(True, linestyle='--', alpha=0.7, color=self.theme['border'])
        ax.set_facecolor(self.theme['bg_secondary'])
        ax.tick_params(axis='both', colors=self.theme['text_secondary'], labelsize=8)
        for spine in ax.spines.values():
            spine.set_linewidth(0.5)
            spine.set_color(self.theme['border'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.fig_line.tight_layout()
        self.canvas_line.draw()

    def update_bar_chart(self):
        self.fig_bar.clear()
        ax = self.fig_bar.add_subplot(111)
        ax.set_title("Falhas por Equipamento", fontsize=14, pad=10, color=self.theme['text_primary'])
        ax.set_xlabel("TAG", fontsize=10, color=self.theme['text_secondary'])
        ax.set_ylabel("Quantidade", fontsize=10, color=self.theme['text_secondary'])

        if not self.df.empty:
            falhas_por_equipamento = self.df[self.df['Falha'] != 'Sem Falha'].groupby('TAG').size()
            bars = ax.bar(falhas_por_equipamento.index, falhas_por_equipamento, color='#FF0000', edgecolor='black', linewidth=0.5)

            self.annotation_bar = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                                              bbox=dict(boxstyle="round,pad=0.5", fc=self.theme['bg_card'], alpha=0.9, ec=self.theme['border']),
                                              color=self.theme['text_primary'], visible=False, zorder=10)

            def hover(event):
                if event.inaxes == ax:
                    for bar in bars:
                        cont = bar.contains(event)[0]
                        if cont:
                            tag = falhas_por_equipamento.index[int(bar.get_x() + bar.get_width() / 2)]
                            count = int(bar.get_height())
                            self.annotation_bar.set_text(f"TAG: {tag}\nFalhas: {count}")
                            self.annotation_bar.xy = (bar.get_x() + bar.get_width() / 2, bar.get_height())
                            self.annotation_bar.set_visible(True)
                            self.fig_bar.canvas.draw_idle()
                            return
                    if self.annotation_bar.get_visible():
                        self.annotation_bar.set_visible(False)
                        self.fig_bar.canvas.draw_idle()

            self.fig_bar.canvas.mpl_connect("motion_notify_event", hover)

        ax.grid(True, linestyle='--', alpha=0.7, color=self.theme['border'])
        ax.set_facecolor(self.theme['bg_secondary'])
        ax.tick_params(axis='both', colors=self.theme['text_secondary'], labelsize=8)
        for spine in ax.spines.values():
            spine.set_linewidth(0.5)
            spine.set_color(self.theme['border'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.fig_bar.tight_layout()
        self.canvas_bar.draw()

    def update_pie_chart(self):
        self.fig_pie.clear()
        ax = self.fig_pie.add_subplot(111)
        ax.set_title("Distribuição de Falhas", fontsize=14, pad=10, color=self.theme['text_primary'])

        if not self.df.empty:
            falha_counts = self.df['Falha'].value_counts()
            wedges, texts, autotexts = ax.pie(falha_counts, labels=falha_counts.index, autopct='%1.1f%%',
                                              colors=['#FF0000', '#FF3333', '#CC0000'],
                                              textprops={'fontsize': 8, 'color': self.theme['text_primary']})

            self.annotation_pie = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                                              bbox=dict(boxstyle="round,pad=0.5", fc=self.theme['bg_card'], alpha=0.9, ec=self.theme['border']),
                                              color=self.theme['text_primary'], visible=False, zorder=10)

            def hover(event):
                if event.inaxes == ax:
                    for i, wedge in enumerate(wedges):
                        cont = wedge.contains(event)[0]
                        if cont:
                            falha = falha_counts.index[i]
                            count = falha_counts.iloc[i]
                            self.annotation_pie.set_text(f"Falha: {falha}\nQuantidade: {count}")
                            self.annotation_pie.xy = (event.xdata, event.ydata)
                            self.annotation_pie.set_visible(True)
                            self.fig_pie.canvas.draw_idle()
                            return
                    if self.annotation_pie.get_visible():
                        self.annotation_pie.set_visible(False)
                        self.fig_pie.canvas.draw_idle()

            self.fig_pie.canvas.mpl_connect("motion_notify_event", hover)

        ax.set_facecolor(self.theme['bg_secondary'])
        self.fig_pie.tight_layout()
        self.canvas_pie.draw()

    def apply_theme(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        shadow.setColor(QColor(100, 100, 100))
        self.charts_container.setGraphicsEffect(shadow)

        for label in [self.total_equip_label, self.maint_equip_label, self.faults_label]:
            label.setStyleSheet(f"""
                background-color: {self.theme['bg_card']};
                color: {self.theme['text_primary']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            """)
        self.canvas_line.setStyleSheet(f"border: 1px solid {self.theme['border']}; border-radius: 10px;")
        self.canvas_bar.setStyleSheet(f"border: 1px solid {self.theme['border']}; border-radius: 10px;")
        self.canvas_pie.setStyleSheet(f"border: 1px solid {self.theme['border']}; border-radius: 10px;")

        self.fig_line.set_facecolor(self.theme['bg_card'])
        self.fig_bar.set_facecolor(self.theme['bg_card'])
        self.fig_pie.set_facecolor(self.theme['bg_card'])
        for ax in self.fig_line.get_axes():
            ax.set_facecolor(self.theme['bg_secondary'])
        for ax in self.fig_bar.get_axes():
            ax.set_facecolor(self.theme['bg_secondary'])
        for ax in self.fig_pie.get_axes():
            ax.set_facecolor(self.theme['bg_secondary'])

        self.canvas_line.draw()
        self.canvas_bar.draw()
        self.canvas_pie.draw()

    def update_theme(self, theme):
        self.theme = theme
        self.update_line_chart()
        self.update_bar_chart()
        self.update_pie_chart()
        self.apply_theme()

    def export_to_pdf(self, file_path):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_path)

        painter = QtGui.QPainter(printer) # type: ignore
        self.render(painter)
        painter.end()