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