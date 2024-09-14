"""
ダッシュボードウィジェット

役割:
- 現在の作業状況の表示
- 今日の達成タスク数の表示

主な機能:
- 折りたたみ可能なウィジェット
- リアルタイムでの情報更新

使用するクラス/モジュール:
- core.session_manager.SessionManager
- core.task_manager.TaskManager
- utils.ui_helpers

注意点:
- 情報の更新はイベントドリブンで行い、不要な再描画を避けること
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Slot

class DashboardWidget(QWidget):
    def __init__(self, session_manager, task_manager):
        super().__init__()
        self.session_manager = session_manager
        self.task_manager = task_manager
        self.setup_ui()
        self.is_expanded = True

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.toggle_button = QPushButton("▼ Dashboard")
        self.toggle_button.clicked.connect(self.toggle_dashboard)
        layout.addWidget(self.toggle_button)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        self.pomodoro_count_label = QLabel("完了したポモドーロ: 0")  # この行を追加
        self.completed_tasks_label = QLabel("完了したタスク: 0")  # この行を修正
        self.focus_time_label = QLabel("集中時間: 0分")  # この行を修正

        self.content_layout.addWidget(self.pomodoro_count_label)  # この行を追加
        self.content_layout.addWidget(self.completed_tasks_label)
        self.content_layout.addWidget(self.focus_time_label)

        layout.addWidget(self.content_widget)
        self.setMaximumHeight(200)
        self.setObjectName("dashboardWidget")

    @Slot()
    def toggle_dashboard(self):
        self.is_expanded = not self.is_expanded
        self.content_widget.setVisible(self.is_expanded)
        self.toggle_button.setText("▼ Dashboard" if self.is_expanded else "▶ Dashboard")

    def update_dashboard(self):
        today_stats = self.session_manager.get_today_stats()
        completed_tasks = self.task_manager.get_completed_tasks_count()

        self.pomodoro_count_label.setText(f"完了したポモドーロ: {today_stats['completed_pomodoros']}")
        self.focus_time_label.setText(f"集中時間: {today_stats['total_focus_time'] // 60} 分")
        self.completed_tasks_label.setText(f"完了したタスク: {completed_tasks}")

    def showEvent(self, event):
        super().showEvent(event)
        self.update_dashboard()

class MiniDashboardWidget(QWidget):
    def __init__(self, session_manager, task_manager):
        super().__init__()
        self.session_manager = session_manager
        self.task_manager = task_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # マージンを追加
        self.completed_pomodoros_label = QLabel()
        self.total_focus_time_label = QLabel()
        self.completed_tasks_label = QLabel()

        layout.addWidget(self.completed_pomodoros_label)
        layout.addWidget(self.total_focus_time_label)
        layout.addWidget(self.completed_tasks_label)

        self.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 12px;
                margin-bottom: 5px;
            }
        """)

    def update_stats(self):
        stats = self.session_manager.get_today_stats()
        completed_tasks = self.task_manager.get_completed_tasks_count()
        self.completed_pomodoros_label.setText(f"完了したポモドーロ: {stats['completed_pomodoros']}")
        self.total_focus_time_label.setText(f"総集中時間: {stats['total_focus_time'] // 60}分")
        self.completed_tasks_label.setText(f"完了したタスク: {completed_tasks}")

    def showEvent(self, event):
        super().showEvent(event)
        self.update_stats()