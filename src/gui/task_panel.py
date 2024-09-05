"""
タスク管理パネル

役割:
- タスクリストの表示と管理
- タスクの追加/編集/削除機能の提供

主な機能:
- タスクのツリー表示（メインタスクとサブタスク）
- タスクの状態変更（未開始、進行中、完了）
- ドラッグ&ドロップによるタスクの並べ替え

使用するクラス/モジュール:
- gui.slide_panel.SlidePanel
- core.task_manager.TaskManager
- utils.ui_helpers

注意点:
- 大量のタスクがある場合のパフォーマンスに注意（仮想化リストの使用を検討）
- タスクの変更はリアルタイムでデータベースと同期すること
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout, QInputDialog
from PySide6.QtCore import Qt
from src.core.task_manager import TaskManager
from src.utils.ui_helpers import create_button

class TaskPanel(QWidget):
    def __init__(self, task_manager: TaskManager):
        super().__init__()
        self.task_manager = task_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # タスクツリー
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["タスク", "状態"])
        self.task_tree.setDragDropMode(QTreeWidget.InternalMove)
        self.task_tree.itemChanged.connect(self.on_task_changed)
        layout.addWidget(self.task_tree)

        # ボタン
        button_layout = QHBoxLayout()
        add_task_button = create_button("タスク追加", style_class="primary")
        add_task_button.clicked.connect(self.add_task)
        delete_task_button = create_button("タスク削除", style_class="secondary")
        delete_task_button.clicked.connect(self.delete_task)
        button_layout.addWidget(add_task_button)
        button_layout.addWidget(delete_task_button)
        layout.addLayout(button_layout)

        self.load_tasks()

    def load_tasks(self):
        self.task_tree.clear()
        tasks = self.task_manager.get_task_tree()
        for task in tasks:
            self.add_task_to_tree(task, self.task_tree.invisibleRootItem())

    def add_task_to_tree(self, task, parent_item):
        item = QTreeWidgetItem(parent_item, [task.title, task.status])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setData(0, Qt.UserRole, task.id)
        for subtask in task.subtasks:
            self.add_task_to_tree(subtask, item)

    def add_task(self):
        title, ok = QInputDialog.getText(self, "タスク追加", "タスク名を入力してください:")
        if ok and title:
            self.task_manager.create_task(title)
            self.load_tasks()

    def delete_task(self):
        selected_items = self.task_tree.selectedItems()
        if selected_items:
            task_id = selected_items[0].data(0, Qt.UserRole)
            self.task_manager.delete_task(task_id)
            self.load_tasks()

    def on_task_changed(self, item, column):
        if column == 0:  # タスク名が変更された場合
            task_id = item.data(0, Qt.UserRole)
            new_title = item.text(0)
            self.task_manager.update_task_title(task_id, new_title)
        elif column == 1:  # 状態が変更された場合
            task_id = item.data(0, Qt.UserRole)
            new_status = item.text(1)
            self.task_manager.update_task_status(task_id, new_status)