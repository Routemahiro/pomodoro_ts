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
        
        self.session_label = QLabel("Today's Sessions: 0")
        self.task_label = QLabel("Completed Tasks: 0")
        self.focus_time_label = QLabel("Total Focus Time: 0h 0m")

        self.content_layout.addWidget(self.session_label)
        self.content_layout.addWidget(self.task_label)
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
        
        self.session_label.setText(f"Today's Sessions: {today_stats['session_count']}")
        self.task_label.setText(f"Completed Tasks: {completed_tasks}")
        
        focus_time_hours = today_stats['total_focus_time'] // 3600
        focus_time_minutes = (today_stats['total_focus_time'] % 3600) // 60
        self.focus_time_label.setText(f"Total Focus Time: {focus_time_hours}h {focus_time_minutes}m")

    def showEvent(self, event):
        super().showEvent(event)
        self.update_dashboard()