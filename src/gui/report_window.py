"""
レポート表示ウィンドウ

役割:
- 生産性データの視覚化と表示

主な機能:
- 日別、週別、月別の作業統計グラフ
- タスク完了率の表示
- 集中時間の分析

使用するクラス/モジュール:
- data.data_analyzer.DataAnalyzer
- utils.ui_helpers

注意点:
- 大量のデータを扱う場合のパフォーマンスに注意
- グラフ描画にはmatplotlibやPyQtChartを使用し、見やすい視覚化を心がけること
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
from PySide6.QtGui import QPainter
from src.data.data_analyzer import DataAnalyzer
from PySide6.QtCore import Qt

class ReportWindow(QWidget):
    def __init__(self, data_analyzer: DataAnalyzer):
        super().__init__()
        self.data_analyzer = data_analyzer
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.setWindowTitle("生産性レポート")
        self.setMinimumSize(800, 600)

        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_daily_report(), "日別レポート")
        tab_widget.addTab(self.create_weekly_report(), "週別レポート")
        tab_widget.addTab(self.create_monthly_report(), "月別レポート")

        layout.addWidget(tab_widget)

    def create_daily_report(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 日別の作業時間グラフ
        chart = self.create_bar_chart("日別作業時間", self.data_analyzer.get_daily_work_time())
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(chart_view)

        # タスク完了率
        completion_rate = self.data_analyzer.calculate_task_completion_rate()
        layout.addWidget(QLabel(f"タスク完了率: {completion_rate:.2f}%"))

        # 集中時間の分析
        focus_stats = self.data_analyzer.generate_focus_time_statistics()
        layout.addWidget(QLabel(f"総集中時間: {focus_stats['total_focus_time'] / 3600:.2f}時間"))
        layout.addWidget(QLabel(f"平均集中時間: {focus_stats['avg_focus_time'] / 60:.2f}分"))

        return widget

    def create_weekly_report(self):
        # 週別レポートの実装（日別レポートと同様の構造）
        pass

    def create_monthly_report(self):
        # 月別レポートの実装（日別レポートと同様の構造）
        pass

    def create_bar_chart(self, title, data):
        chart = QChart()
        chart.setTitle(title)

        series = QBarSeries()
        bar_set = QBarSet("作業時間")

        for value in data.values():
            bar_set.append(value)

        series.append(bar_set)
        chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(list(data.keys()))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        return chart