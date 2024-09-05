"""
タイマー表示ウィジェット

役割:
- 現在のタイマー状態の表示
- タイマーの開始/停止/リセット機能の提供

主な機能:
- デジタル時計形式でのタイマー表示
- タイマーの状態に応じた表示色の変更（作業中、休憩中など）

使用するクラス/モジュール:
- core.timer.Timer
- utils.ui_helpers

注意点:
- タイマーの状態変更時にシグナルを発行し、他のウィジェット（特にCharacterWidget）に通知すること
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from src.utils.helpers import format_time

class TimerWidget(QWidget):
    timer_updated = Signal(str, str, int)  # 状態, タイマータイプ, 残り時間

    def __init__(self, timer):
        super().__init__()
        self.timer = timer
        self.setup_ui()
        self.timer.add_observer(self.update_timer)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setObjectName("timerWidget")
        layout.addWidget(self.time_label)

    def update_timer(self, state, timer_type, remaining_time):
        formatted_time = format_time(remaining_time)
        self.time_label.setText(formatted_time)
        self.update_color(timer_type)
        self.timer_updated.emit(state.name, timer_type.name, remaining_time)

    def update_color(self, timer_type):
        if timer_type.name == "WORK":
            self.time_label.setStyleSheet("color: #4CAF50;")  # 緑色
        elif timer_type.name == "SHORT_BREAK":
            self.time_label.setStyleSheet("color: #2196F3;")  # 青色
        else:  # LONG_BREAK
            self.time_label.setStyleSheet("color: #FFC107;")  # 黄色