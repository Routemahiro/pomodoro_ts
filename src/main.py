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
# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.core.timer import Timer
from src.core.session_manager import SessionManager
from src.core.task_manager import TaskManager
from src.core.ai_interface import AIInterface
from src.data.database import Database
from src.utils.config import config

def main():
    app = QApplication(sys.argv)

    # 設定の初期化
    config.load()

    # データベースの初期化
    db = Database(config)
    db.initialize()

    # 各コアモジュールの初期化
    timer = Timer(config)
    session_manager = SessionManager(db, config)
    task_manager = TaskManager(db, config)
    ai_interface = AIInterface(config)

    # メインウィンドウの作成と表示
    main_window = MainWindow(timer, session_manager, task_manager, ai_interface, config)
    main_window.show()

    # アプリケーションの実行
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        sys.exit(1)