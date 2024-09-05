"""
AI会話パネル

役割:
- AIとのチャットインターフェースの提供
- AIからの提案をタスクリストに追加する機能

主な機能:
- メッセージの送受信
- 会話履歴の表示
- 「タスクに追加」ボタンの実装

使用するクラス/モジュール:
- gui.slide_panel.SlidePanel
- core.ai_interface.AIInterface
- core.task_manager.TaskManager
- data.ai_conversation.AIConversation
- utils.ui_helpers

注意点:
- 長文の応答や処理時間が長い場合の UI のレスポンシブ性に注意
- APIキーが設定されていない場合の適切なエラーハンドリング
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal
from src.utils.ui_helpers import create_button
from src.core.ai_interface import AIInterface
from src.core.task_manager import TaskManager

class AIChatPanel(QWidget):
    task_added = Signal(str)  # タスクが追加されたときに発行するシグナル

    def __init__(self, ai_interface: AIInterface, task_manager: TaskManager):
        super().__init__()
        self.ai_interface = ai_interface
        self.task_manager = task_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # チャット履歴表示エリア
        self.chat_history = QListWidget()
        layout.addWidget(self.chat_history)

        # メッセージ入力エリア
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("AIに質問やタスクの提案を入力してください...")
        layout.addWidget(self.message_input)

        # ボタンエリア
        button_layout = QHBoxLayout()
        self.send_button = create_button("送信", style_class="primary")
        self.send_button.clicked.connect(self.send_message)
        self.add_task_button = create_button("タスクに追加", style_class="secondary")
        self.add_task_button.clicked.connect(self.add_task)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.add_task_button)
        layout.addLayout(button_layout)

    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if message:
            self.add_message_to_history("You", message)
            self.message_input.clear()

            # AIの応答を取得（非同期で行うべきですが、簡略化のため同期的に実装）
            response = self.ai_interface.send_message(message)
            self.add_message_to_history("AI", response)

    def add_message_to_history(self, sender, message):
        item = QListWidgetItem(f"{sender}: {message}")
        self.chat_history.addItem(item)
        self.chat_history.scrollToBottom()

    def add_task(self):
        selected_items = self.chat_history.selectedItems()
        if selected_items:
            task_description = selected_items[0].text().split(": ", 1)[1]
            self.task_manager.create_task(task_description)
            self.task_added.emit(task_description)