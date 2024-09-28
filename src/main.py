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

import sys
import os
import traceback
# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import matplotlib
matplotlib.use('QtAgg')

from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.core.timer import Timer
from src.core.session_manager import SessionManager
from src.core.task_manager import TaskManager
from src.core.ai_interface import AIInterface
from src.data.database import Database
from src.utils.config import config
from src.core.notification_manager import NotificationManager
from src.data.ai_conversation import AIConversationManager  # この行を修正
from src.utils.ui_helpers import load_stylesheet

def main():
    app = QApplication(sys.argv)

    # 設定の初期化
    config.load()

    # テーマの適用
    theme = config.get('theme', 'ライト')
    if theme == 'ダーク':
        stylesheet = load_stylesheet("resources/styles/dark_style.qss")
    else:
        stylesheet = load_stylesheet("resources/styles/style.qss")
    
    if stylesheet:
        app.setStyleSheet(stylesheet)
    else:
        print(f"警告: {theme}モードのスタイルシートが空です。")

    # データベースの初期化
    db = Database(config)
    db.initialize_database()

    # 各コアモジュールの初期化
    notification_manager = NotificationManager(config)
    session_manager = SessionManager(db, config)  # session_managerを先に初期化
    timer = Timer(config, notification_manager, session_manager)  # session_managerを渡す
    task_manager = TaskManager(db, config)
    ai_conversation_manager = AIConversationManager(db)
    ai_interface = AIInterface(config, ai_conversation_manager)

    # 設定変更時のコールバックを登録
    config.register_observer('test_mode', lambda key, value: timer.update_settings(config))
    config.register_observer('work_time', lambda key, value: timer.update_settings(config))
    config.register_observer('short_break', lambda key, value: timer.update_settings(config))
    config.register_observer('long_break', lambda key, value: timer.update_settings(config))

    # メインウィンドウの作成と表示
    main_window = MainWindow(timer, session_manager, task_manager, ai_interface, config, ai_conversation_manager)
    main_window.show()

    # アプリケーションの実行
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        print("詳細:")
        traceback.print_exc()
        sys.exit(1)