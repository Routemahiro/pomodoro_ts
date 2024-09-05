"""
アプリケーション全体で使用する定数

役割:
- 共通の定数値を一元管理

主な内容:
- デフォルトの時間設定（作業時間、休憩時間など）
- カラーコード
- ファイルパス
- エラーメッセージ

注意点:
- 定数名は明確で理解しやすいものを選ぶこと
- 必要に応じて、列挙型（Enum）を使用して関連する定数をグループ化すること
"""
from enum import Enum
from src.utils.config import config

class TimerDefaults(Enum):
    WORK_TIME = config.get('work_time', 25 * 60)  # デフォルト: 25分
    SHORT_BREAK = config.get('short_break', 5 * 60)  # デフォルト: 5分
    LONG_BREAK = config.get('long_break', 15 * 60)  # デフォルト: 15分
    POMODOROS_BEFORE_LONG_BREAK = config.get('pomodoros_before_long_break', 4)

class Colors(Enum):
    PRIMARY = config.get('color_primary', "#4CAF50")
    SECONDARY = config.get('color_secondary', "#2196F3")
    ACCENT = config.get('color_accent', "#FFC107")
    BACKGROUND = config.get('color_background', "#FFFFFF")
    TEXT = config.get('color_text', "#333333")

class FilePaths(Enum):
    DATABASE = config.get('database_path', "data/pomodoro.db")
    SETTINGS = config.get('settings_path', "data/settings.json")
    LOGS = config.get('logs_path', "logs/app.log")

class ErrorMessages(Enum):
    DATABASE_CONNECTION = "データベースへの接続に失敗しました。"
    SETTINGS_LOAD = "設定の読み込みに失敗しました。"
    TIMER_START = "タイマーの開始に失敗しました。"

# 他の定数カテゴリーを必要に応じて追加