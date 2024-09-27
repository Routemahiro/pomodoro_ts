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

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout, QInputDialog, QDateEdit, QTimeEdit, QRadioButton, QButtonGroup, QDialog, QLabel, QComboBox, QStyledItemDelegate, QTextEdit, QDateTimeEdit, QToolTip, QStyleOptionViewItem
from PySide6.QtCore import Qt, QDate, QTime, QDateTime, QEvent, QPoint

from src.core.task_manager import TaskManager
from src.utils.ui_helpers import create_button
from datetime import datetime, timedelta
from src.data.task_data import TaskPriority, TaskStatus


class TaskDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.statuses = [status.value for status in TaskStatus]
        self.priorities = [priority.value for priority in TaskPriority]
        self.date_format = "yyyy-MM-dd HH:mm"  # 日付フォーマットを定義

    def createEditor(self, parent, option, index):
        if index.column() == 1:  # 状態列
            combo = QComboBox(parent)
            combo.addItems(self.statuses)
            return combo
        elif index.column() == 2:  # 優先度列
            combo = QComboBox(parent)
            combo.addItems(self.priorities)
            return combo
        elif index.column() == 3:  # 期限列
            editor = QDateTimeEdit(parent)
            editor.setDisplayFormat(self.date_format)
            editor.setCalendarPopup(True)
            editor.setDateTime(QDateTime.currentDateTime())
            return editor
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if index.column() == 1:
            current_text = index.data(Qt.EditRole)
            idx = self.statuses.index(current_text) if current_text in self.statuses else 0
            editor.setCurrentIndex(idx)
        elif index.column() == 2:
            current_text = index.data(Qt.EditRole)
            idx = self.priorities.index(current_text) if current_text in self.priorities else 0
            editor.setCurrentIndex(idx)
        elif index.column() == 3:
            date_str = index.data(Qt.EditRole)
            if date_str:
                date_time = QDateTime.fromString(date_str, self.date_format)
                if date_time.isValid():
                    editor.setDateTime(date_time)
                else:
                    editor.setDateTime(QDateTime.currentDateTime())
            else:
                editor.setDateTime(QDateTime.currentDateTime())
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == 1:
            new_status = editor.currentText()
            model.setData(index, new_status, Qt.EditRole)
        elif index.column() == 2:
            new_priority = editor.currentText()
            model.setData(index, new_priority, Qt.EditRole)
        elif index.column() == 3:
            new_due_date = editor.dateTime().toString(self.date_format)
            model.setData(index, new_due_date, Qt.EditRole)
        else:
            super().setModelData(editor, model, index)


class TaskPanel(QWidget):
    def __init__(self, task_manager: TaskManager):
        super().__init__()
        self.task_manager = task_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # タスクツリー
        self.task_tree = QTreeWidget()
        self.task_tree.setHeaderLabels(["タスク", "状態", "優先度", "期限"])
        self.task_tree.setDragDropMode(QTreeWidget.InternalMove)
        self.task_tree.itemChanged.connect(self.on_task_changed)

        # ソートを有効にする
        self.task_tree.setSortingEnabled(True)

        layout.addWidget(self.task_tree)

        # カラムの幅を設定
        self.task_tree.setColumnWidth(0, 180)  # タスク
        self.task_tree.setColumnWidth(1, 75)  # 状態
        self.task_tree.setColumnWidth(2, 60)  # 優先度
        self.task_tree.setColumnWidth(3, 150)  # 期限

        # TaskDelegateを適用
        task_delegate = TaskDelegate(self.task_tree)
        self.task_tree.setItemDelegateForColumn(1, task_delegate)
        self.task_tree.setItemDelegateForColumn(2, task_delegate)
        self.task_tree.setItemDelegateForColumn(3, task_delegate)

        # タスクツリーにイベントフィルターを追加
        self.task_tree.installEventFilter(self)

        # ボタン
        button_layout = QHBoxLayout()
        add_task_button = create_button("タスク追加", style_class="primary")
        add_task_button.clicked.connect(self.add_task)

        delete_task_button = create_button("タスク削除", style_class="secondary")
        delete_task_button.clicked.connect(self.delete_task)

        import_task_button = create_button("タスクインポート", style_class="secondary")
        import_task_button.clicked.connect(self.show_text_import_widget)

        button_layout.addWidget(add_task_button)
        button_layout.addWidget(delete_task_button)
        button_layout.addWidget(import_task_button)
        layout.addLayout(button_layout)

        self.load_tasks()

    def eventFilter(self, source, event):
        if source == self.task_tree and event.type() == QEvent.ToolTip:
            pos = event.pos()
            # アイテムの高さを取得
            item_height = self.task_tree.visualItemRect(self.task_tree.topLevelItem(0)).height()
            # マウス位置を上に調整（アイテムの高さ分）
            adjusted_pos = pos - QPoint(0, item_height)
            index = self.task_tree.indexAt(adjusted_pos)
            if index.isValid():
                item = self.task_tree.itemFromIndex(index)
                if item:
                    QToolTip.showText(event.globalPos(), item.text(0))
                    return True
        return super().eventFilter(source, event)

    def load_tasks(self):
        self.task_tree.clear()
        tasks = self.task_manager.get_task_tree()
        for task in tasks:
            self.add_task_to_tree(task, self.task_tree.invisibleRootItem())

    def add_task_to_tree(self, task, parent_item):
        due_date = task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else ""
        item = CustomTreeWidgetItem(parent_item, [task.title, task.status.value, task.priority.value, due_date])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setData(0, Qt.UserRole, task.id)

        # 優先度のソート用の値を設定
        priority_sort_value = {"高": 0, "中": 1, "低": 2}
        item.setData(2, Qt.UserRole + 1, priority_sort_value.get(task.priority.value, 3))

        # 期限のソート用の値を設定
        due_date_sort_value = task.due_date.timestamp() if task.due_date else float('inf')
        item.setData(3, Qt.UserRole + 1, due_date_sort_value)

        # 状態のソート用の値を設定
        status_sort_value = {"未着手": 0, "着手": 1, "保留": 2, "完了": 3}
        item.setData(1, Qt.UserRole + 1, status_sort_value.get(task.status.value, 4))

        for subtask in task.subtasks:
            self.add_task_to_tree(subtask, item)

    def add_task(self):
        title, ok = QInputDialog.getText(self, "タスク追加", "タスク名を入力してください:")
        if ok and title:
            priority = self.get_priority_from_user()
            due_date = self.get_due_date_from_user()
            if due_date:
                self.task_manager.create_task(title, priority=priority, due_date=due_date)
                self.load_tasks()

    def get_priority_from_user(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("優先度設定")
        layout = QVBoxLayout(dialog)

        # 説明ラベルを追加
        label = QLabel("タスクの優先度を選択してください：")
        layout.addWidget(label)

        priority_group = QButtonGroup(dialog)
        for priority in [TaskPriority.HIGH, TaskPriority.MEDIUM, TaskPriority.LOW]:
            radio = QRadioButton(priority.value)
            priority_group.addButton(radio)
            layout.addWidget(radio)

        # デフォルトで「低」を選択
        priority_group.buttons()[-1].setChecked(True)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.Accepted:
            return TaskPriority(priority_group.checkedButton().text())
        return TaskPriority.LOW

    def get_due_date_from_user(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("期限設定")
        layout = QVBoxLayout(dialog)

        label = QLabel("タスクの期限を選択してください：")
        layout.addWidget(label)

        # 日付選択
        date_edit = QDateEdit(dialog)
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate().addDays(1))
        layout.addWidget(date_edit)

        # 時間選択（時）
        hour_combo = QComboBox(dialog)
        hour_combo.addItems([f"{i:02d}" for i in range(24)])
        hour_combo.setCurrentText(QTime.currentTime().toString("HH"))
        layout.addWidget(hour_combo)

        # 時間選択（分）
        minute_combo = QComboBox(dialog)
        minute_combo.addItems([f"{i:02d}" for i in range(0, 60, 5)])
        current_minute = QTime.currentTime().minute()
        minute_combo.setCurrentText(f"{(current_minute // 5) * 5:02d}")
        layout.addWidget(minute_combo)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.Accepted:
            selected_date = date_edit.date().toPython()
            selected_time = QTime(int(hour_combo.currentText()), int(minute_combo.currentText()))
            return datetime.combine(selected_date, selected_time.toPython())
        return None

    def delete_task(self):
        selected_items = self.task_tree.selectedItems()
        if selected_items:
            task_id = selected_items[0].data(0, Qt.UserRole)
            self.task_manager.delete_task(task_id)
            self.load_tasks()

    def on_task_changed(self, item, column):
        task_id = item.data(0, Qt.UserRole)
        if column == 0:  # タスク名が変更された場合
            new_title = item.text(0)
            self.task_manager.update_task_title(task_id, new_title)
        elif column == 1:  # 状態が変更された場合
            new_status = TaskStatus(item.text(1))
            self.task_manager.update_task_status(task_id, new_status)
        elif column == 2:  # 優先度が変更された場合
            new_priority = TaskPriority(item.text(2))
            self.task_manager.update_task_priority(task_id, new_priority)
        elif column == 3:  # 期限が変更された場合
            new_due_date = item.text(3)
            try:
                new_due_date = datetime.strptime(new_due_date, "%Y-%m-%d %H:%M") if new_due_date else None
                self.task_manager.update_task_due_date(task_id, new_due_date)
            except ValueError:
                pass  # 無効な日付形式の場合は無視

        # ソート用の値を更新
        if column == 1:
            status_sort_value = {"未着手": 0, "着手": 1, "保留": 2, "完了": 3}
            item.setData(1, Qt.UserRole + 1, status_sort_value.get(item.text(1), 4))
        elif column == 2:
            priority_sort_value = {"高": 0, "中": 1, "低": 2}
            item.setData(2, Qt.UserRole + 1, priority_sort_value.get(item.text(2), 3))
        elif column == 3:
            due_date = datetime.strptime(item.text(3), "%Y-%m-%d %H:%M") if item.text(3) else None
            due_date_sort_value = due_date.timestamp() if due_date else float('inf')
            item.setData(3, Qt.UserRole + 1, due_date_sort_value)

        self.task_tree.sortItems(column, Qt.AscendingOrder)

    def show_text_import_widget(self):
        # タスクインポートウィジェットを作成
        self.import_widget = QWidget()
        import_layout = QHBoxLayout(self.import_widget)

        # 左半分のレイアウト
        left_layout = QVBoxLayout()
        
        # タスク生成用のテキスト入力枠
        self.task_generation_edit = QTextEdit()
        left_layout.addWidget(self.task_generation_edit)

        # 最終期限入力用のレイアウト
        deadline_layout = QHBoxLayout()
        deadline_label = QLabel("最終期限：")
        self.deadline_edit = QDateTimeEdit()
        self.deadline_edit.setCalendarPopup(True)  # カレンダーポップアップを有効化
        self.deadline_edit.setDateTime(QDateTime.currentDateTime())  # 現在の日時をデフォルトに設定
        deadline_layout.addWidget(deadline_label)
        deadline_layout.addWidget(self.deadline_edit)
        left_layout.addLayout(deadline_layout)

        # タスク生成ボタン
        generate_button = create_button("タスク生成", style_class="primary")
        generate_button.clicked.connect(self.generate_task_suggestions)
        left_layout.addWidget(generate_button)

        import_layout.addLayout(left_layout)

        # 右半分のレイアウト
        right_layout = QVBoxLayout()

        # インポート用のテキスト入力枠
        self.text_edit = QTextEdit()
        right_layout.addWidget(self.text_edit)

        # 送信とキャンセルボタンを縦並びに
        send_button = create_button("送信", style_class="primary")
        cancel_button = create_button("キャンセル", style_class="secondary")
        send_button.clicked.connect(self.import_tasks_from_text)
        cancel_button.clicked.connect(self.hide_text_import_widget)
        right_layout.addWidget(send_button)
        right_layout.addWidget(cancel_button)

        import_layout.addLayout(right_layout)

        # サンプルテキストを表示
        sample_text = (
            "＜タスク追加用テキストサンプル＞\n"
            "- タスク1 @高 @2023-10-31\n"
            "  - サブタスク1 @中 @2023-10-25\n"
            "  - サブタスク2 @低\n"
            "- タスク2 @中"
        )
        sample_label = QLabel(sample_text)
        sample_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        right_layout.addWidget(sample_label)

        self.layout().addWidget(self.import_widget)

    def generate_task_suggestions(self):
        # タスク生成ロジックをここに実装
        input_text = self.task_generation_edit.toPlainText()
        deadline = self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm")
        # ここでAIを使ってタスクの細分化を行う
        # 結果を self.text_edit に設定する
        # 例：
        # generated_tasks = ai_generate_tasks(input_text, deadline)
        # self.text_edit.setPlainText(generated_tasks)
        pass

    def generate_task_suggestions(self):
        # タスク生成ロジックをここに実装
        input_text = self.task_generation_edit.toPlainText()
        # ここでAIを使ってタスクの細分化を行う
        # 結果を self.text_edit に設定する
        # 例：
        # generated_tasks = ai_generate_tasks(input_text)
        # self.text_edit.setPlainText(generated_tasks)
        pass

    def hide_text_import_widget(self):
        # タスクインポートウィジェットを削除
        self.import_widget.setParent(None)
        self.import_widget = None

    def import_tasks_from_text(self):
        text = self.text_edit.toPlainText()
        self.parse_and_add_tasks(text)
        self.hide_text_import_widget()
        self.load_tasks()

    def parse_and_add_tasks(self, text):
        lines = text.splitlines()
        parent_ids = {0: None}
        indent_levels = []

        for line in lines:
            if not line.strip():
                continue

            # インデントの計算（スペースやタブを含む）
            stripped_line = line.lstrip()
            indent_str = line[:len(line) - len(stripped_line)]
            indent = len(indent_str)

            # 行頭の '-' を削除
            if stripped_line.startswith('-'):
                stripped_line = stripped_line[1:].lstrip()

            # 期限と優先度を解析
            tokens = stripped_line.split()
            task_title_parts = []
            priority = TaskPriority.LOW  # デフォルト値
            due_date = None

            for token in tokens:
                if token.startswith('@'):
                    if token[1:] in [p.value for p in TaskPriority]:
                        priority = TaskPriority(token[1:])
                    else:
                        try:
                            due_date = datetime.strptime(token[1:], "%Y-%m-%d")
                        except ValueError:
                            pass  # 無効な形式は無視
                else:
                    task_title_parts.append(token)

            task_title = ' '.join(task_title_parts)

            # レベルの計算
            while indent_levels and indent < indent_levels[-1]:
                indent_levels.pop()

            if not indent_levels or indent > indent_levels[-1]:
                indent_levels.append(indent)

            level = len(indent_levels) - 1
            parent_id = parent_ids.get(level - 1, None)

            task_id = self.task_manager.create_task(
                title=task_title,
                parent_id=parent_id,
                priority=priority,
                due_date=due_date
            )
            parent_ids[level] = task_id


class CustomTreeWidgetItem(QTreeWidgetItem):
    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        data1 = self.data(column, Qt.UserRole + 1)
        data2 = other.data(column, Qt.UserRole + 1)

        if data1 is not None and data2 is not None:
            return data1 < data2
        else:
            # 比較できない場合は文字列として比較
            return self.text(column) < other.text(column)