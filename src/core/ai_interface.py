"""
AI (ChatGPT) とのインターフェース

役割:
- ChatGPT APIとの通信
- AIの応答の解析とタスク分解

主な機能:
- APIリクエストの送信と応答の受信
- 応答のJSON解析とタスクデータへの変換

使用するクラス/モジュール:
- utils.config.Config
- data.ai_conversation.AIConversation

注意点:
- API呼び出しの頻度制限に注意
- APIキーの安全な管理（設定ファイルからの読み込み、暗号化など）
- ネットワークエラーなどの例外処理を適切に行うこと
"""