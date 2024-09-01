"""
アプリケーションのメインエントリーポイント

役割:
- QApplicationの初期化
- メインウィンドウの作成と表示
- 各コアモジュールの初期化と連携

使用するクラス/モジュール:
- gui.main_window.MainWindow
- core.timer.Timer
- core.session_manager.SessionManager
- core.task_manager.TaskManager
- core.ai_interface.AIInterface
- data.database.Database
- utils.config.Config

注意点:
- アプリケーション全体の設定（Config）を最初に読み込み、各モジュールに渡すこと
- 例外処理を適切に行い、予期せぬエラーでアプリケーションが終了しないようにすること
"""