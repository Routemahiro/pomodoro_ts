"""
タイマー表示ウィジェット

役割:
- 現在のタイマー状態の表示
- タイマーの開始/停止/リセット機能の提供

主な機能:
- デジタル時計形式でのタイマー表示
- 円形進捗バーでの視覚的なタイマー表示
- タイマーの状態に応じた表示色の変更（作業中、休憩中など）

使用するクラス/モジュール:
- core.timer.Timer
- utils.ui_helpers
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPalette
from src.utils.helpers import format_time
from src.core.timer import TimerType

class TimerWidget(QWidget):
    timer_updated = Signal(str, str, int, bool)  # 状態, タイマータイプ, 残り時間, リセット可能か

    def __init__(self, timer):
        super().__init__()
        self.timer = timer
        self.progress = 0
        self.setup_ui()
        self.timer.add_observer(self.update_timer)
        self.setFixedSize(200, 200)  # ウィジェットのサイズを固定

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.time_label = QLabel(format_time(self.timer.remaining_time))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setObjectName("timerWidget")
        
        # ラベルの背景を透明にする
        palette = self.time_label.palette()
        palette.setColor(QPalette.Window, Qt.transparent)
        self.time_label.setPalette(palette)
        self.time_label.setAutoFillBackground(True)
        
        layout.addWidget(self.time_label)
        
        # ウィジェット自体の背景も透明にする
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 円形進捗バーの描画
        pen_width = 10
        size = min(self.width(), self.height()) - pen_width
        rect = QRectF((self.width() - size) / 2, (self.height() - size) / 2, size, size)

        painter.setPen(QPen(QColor(200, 200, 200), pen_width))
        painter.drawArc(rect, 0, 360 * 16)

        painter.setPen(QPen(self.get_color(), pen_width))
        painter.drawArc(rect, 90 * 16, -self.progress * 360 * 16)

    def update_timer(self, state, timer_type, remaining_time, can_reset):
        formatted_time = format_time(remaining_time)
        self.time_label.setText(formatted_time)
        total_duration = self.get_total_duration(timer_type)
        self.progress = 1 - (remaining_time / total_duration)
        self.update()
        self.timer_updated.emit(state.name, timer_type.name, remaining_time, can_reset)

    def get_total_duration(self, timer_type):
        if timer_type == TimerType.WORK:
            return self.timer.config.get('work_time', 25 * 60)
        elif timer_type == TimerType.SHORT_BREAK:
            return self.timer.config.get('short_break', 5 * 60)
        else:  # LONG_BREAK
            return self.timer.config.get('long_break', 15 * 60)

    def get_color(self):
        if self.timer.timer_type == TimerType.WORK:
            return QColor("#4CAF50")  # 緑色
        elif self.timer.timer_type == TimerType.SHORT_BREAK:
            return QColor("#2196F3")  # 青色
        else:  # LONG_BREAK
            return QColor("#FFC107")  # 黄色

    def update_display(self):
        formatted_time = format_time(self.timer.remaining_time)
        self.time_label.setText(formatted_time)
        self.update()